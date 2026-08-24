# visual_catalog_modal.py
# Apollo Visual Threat & Packaging Intelligence Manager Dialog
# Supports Multi-Hash Threat Asset Clusters and 1-Click Variant Merging

import os
import io
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

FONT_TITLE = ("Segoe UI", 12, "bold")
FONT_BOLD = ("Segoe UI", 9, "bold")
FONT_NORM = ("Segoe UI", 9)
FONT_SM = ("Segoe UI", 8)

class VisualCatalogModal(tk.Toplevel):
    def __init__(self, master, visual_catalog_manager, theme, on_update_callback=None):
        super().__init__(master)
        self.vcm = visual_catalog_manager
        self.theme = theme
        self.on_update = on_update_callback
        self.photo_refs = []
        self.selected_card_ids = set()

        self.title("🖼️ Apollo Visual Packaging & Threat Intelligence Library")
        self.geometry("880x660")
        self.minsize(740, 520)
        self.configure(bg=self._t("bg", "#121212"))
        self.transient(master)
        self.grab_set()

        self._center_window(880, 660)
        self._build_ui()
        self._load_gallery()

    def _t(self, key, default="#1e1e1e"):
        return self.theme.get(key, default)

    def _center_window(self, width, height):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        panel_bg = self._t("panel", "#1e1e1e")
        accent_color = self._t("accent", "#00d2ff")
        text_color = self._t("text", "#ffffff")
        subtext_color = self._t("subtext", "#888888")
        btn_bg = self._t("btn_normal_bg", panel_bg)
        btn_fg = self._t("btn_normal_fg", text_color)
        bg_color = self._t("bg", "#121212")

        # Top Header Bar
        header = tk.Frame(self, bg=panel_bg, padx=14, pady=10)
        header.pack(fill="x", side="top")

        lbl_box = tk.Frame(header, bg=panel_bg)
        lbl_box.pack(side="left")

        tk.Label(lbl_box, text="🖼️ Visual Threat Intelligence Catalog", font=FONT_TITLE,
                 bg=panel_bg, fg=accent_color).pack(anchor="w")
        tk.Label(lbl_box, text="Multi-Hash Threat Clusters • Match Benign Packaging & Flag Counterfeit Photo Syndicates",
                 font=FONT_SM, bg=panel_bg, fg=subtext_color).pack(anchor="w")

        # Top Right Action Buttons
        top_btns = tk.Frame(header, bg=panel_bg)
        top_btns.pack(side="right")

        self.merge_btn = tk.Button(top_btns, text="🔗 Merge Selected (0)", font=FONT_BOLD, bg=accent_color,
                                   fg="black" if self.theme.get("name","").startswith("⚡") else "white",
                                   relief="flat", padx=8, pady=4, cursor="hand2", command=self._merge_selected_cards)
        self.merge_btn.pack(side="left", padx=3)

        tk.Button(top_btns, text="➕ Add File", font=FONT_BOLD, bg=btn_bg, fg=btn_fg,
                  relief="flat", padx=8, pady=4, cursor="hand2", command=self._add_from_file).pack(side="left", padx=3)
        tk.Button(top_btns, text="🌐 Add URL", font=FONT_BOLD, bg=btn_bg, fg=btn_fg,
                  relief="flat", padx=8, pady=4, cursor="hand2", command=self._add_from_url).pack(side="left", padx=3)

        # Control Bar: Filters & Sensitivity Slider
        ctrl_bar = tk.Frame(self, bg=panel_bg, padx=14, pady=8, bd=1, relief="solid")
        ctrl_bar.pack(fill="x", side="top", pady=(1, 0))

        # Filter Tabs
        self.filter_var = tk.StringVar(value="all")
        tab_box = tk.Frame(ctrl_bar, bg=panel_bg)
        tab_box.pack(side="left")

        tk.Label(tab_box, text="Filter:", font=FONT_BOLD, bg=panel_bg, fg=text_color).pack(side="left", padx=(0, 6))
        for text, val in [("📁 All", "all"), ("🟢 Benign Packaging", "benign"), ("🔴 Known Counterfeits", "counterfeit")]:
            rb = tk.Radiobutton(tab_box, text=text, value=val, variable=self.filter_var,
                                font=FONT_NORM, bg=panel_bg, fg=text_color, selectcolor=bg_color,
                                activebackground=panel_bg, activeforeground=accent_color,
                                command=self._load_gallery)
            rb.pack(side="left", padx=4)

        # Sensitivity Slider
        slider_box = tk.Frame(ctrl_bar, bg=panel_bg)
        slider_box.pack(side="right")

        tk.Label(slider_box, text="🎯 Matching Sensitivity:", font=FONT_BOLD, bg=panel_bg, fg=text_color).pack(side="left", padx=(0, 4))
        
        current_thresh = getattr(self.vcm, "match_threshold", 6)
        self.thresh_var = tk.IntVar(value=current_thresh)
        self.thresh_lbl = tk.Label(slider_box, text=self._format_thresh_label(current_thresh), font=FONT_SM,
                                   bg=panel_bg, fg=accent_color, width=14, anchor="w")
        
        scale = tk.Scale(slider_box, from_=2, to_=14, orient="horizontal", variable=self.thresh_var,
                         showvalue=0, length=120, bg=panel_bg, fg=accent_color,
                         highlightthickness=0, troughcolor=self._t("entry_bg", "#1a1a1a"),
                         command=self._on_threshold_change)
        scale.pack(side="left", padx=4)
        self.thresh_lbl.pack(side="left")

        # Scrollable Gallery Frame
        container = tk.Frame(self, bg=bg_color)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(container, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.gallery_frame = tk.Frame(self.canvas, bg=bg_color)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.gallery_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.gallery_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.bind("<MouseWheel>", self._on_mousewheel)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.destroy()

    def _format_thresh_label(self, val):
        v = int(val)
        if v <= 3:
            return f"Strict ({v})"
        elif v <= 6:
            return f"Standard ({v})"
        elif v <= 10:
            return f"Loose ({v})"
        else:
            return f"Broad ({v})"

    def _on_threshold_change(self, val):
        v = int(val)
        self.vcm.match_threshold = v
        self.thresh_lbl.config(text=self._format_thresh_label(v))
        if hasattr(self.master, "data_store"):
            self.master.data_store.set_setting("visual_match_threshold", v)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _toggle_card_selection(self, entry_id):
        if entry_id in self.selected_card_ids:
            self.selected_card_ids.remove(entry_id)
        else:
            self.selected_card_ids.add(entry_id)
        self.merge_btn.config(text=f"🔗 Merge Selected ({len(self.selected_card_ids)})")
        self._load_gallery()

    def _load_gallery(self):
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        self.photo_refs.clear()

        bg_color = self._t("bg", "#121212")
        subtext_color = self._t("subtext", "#888888")

        filter_type = self.filter_var.get()
        entries = self.vcm.get_all_entries()

        if filter_type != "all":
            entries = [e for e in entries if e.get("type") == filter_type]

        if not entries:
            msg_box = tk.Frame(self.gallery_frame, bg=bg_color, pady=60)
            msg_box.pack(fill="both", expand=True)
            tk.Label(msg_box, text="No visual fingerprints stored in this category.",
                     font=FONT_BOLD, bg=bg_color, fg=subtext_color).pack()
            tk.Label(msg_box, text="Right-click any listing in the Results Table to mark packaging as Benign or Counterfeit!",
                     font=FONT_SM, bg=bg_color, fg=subtext_color).pack(pady=4)
            return

        cols = 2
        row = 0
        col = 0
        for entry in entries:
            card = self._create_card(self.gallery_frame, entry)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            col += 1
            if col >= cols:
                col = 0
                row += 1

        for c in range(cols):
            self.gallery_frame.grid_columnconfigure(c, weight=1)

    def _create_card(self, parent, entry):
        panel_bg = self._t("panel", "#1e1e1e")
        text_color = self._t("text", "#ffffff")
        subtext_color = self._t("subtext", "#888888")
        entry_bg = self._t("entry_bg", "#1a1a1a")
        accent_color = self._t("accent", "#00d2ff")
        danger_color = self._t("danger", "#ff4444")
        success_color = self._t("success", "#00cc66")
        accent_fg = self._t("btn_accent_fg", "black" if self.theme.get("name","").startswith("⚡") else "white")

        eid = entry.get("id")
        is_selected = eid in self.selected_card_ids

        card_bd_color = accent_color if is_selected else self._t("border", "#333333")
        card = tk.Frame(parent, bg=panel_bg, bd=2 if is_selected else 1, relief="solid",
                        highlightbackground=card_bd_color, highlightcolor=card_bd_color,
                        padx=10, pady=8)

        # 0. Selection Checkbox
        sel_var = tk.BooleanVar(value=is_selected)
        chk = tk.Checkbutton(card, variable=sel_var, bg=panel_bg, selectcolor=entry_bg,
                             activebackground=panel_bg, command=lambda: self._toggle_card_selection(eid))
        chk.pack(side="left", padx=(0, 6))

        # 1. Thumbnail
        tp = entry.get("thumb_path", "")
        photo = None
        if tp and os.path.exists(tp):
            try:
                pimg = Image.open(tp).convert("RGBA")
                pimg.thumbnail((72, 72), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pimg)
                self.photo_refs.append(photo)
            except Exception:
                pass

        img_lbl = tk.Label(card, image=photo if photo else "", text="[No Photo]" if not photo else "",
                           bg=entry_bg, width=72, height=72, cursor="hand2")
        img_lbl.pack(side="left", padx=(0, 10))
        img_lbl.bind("<Button-1>", lambda e: self._toggle_card_selection(eid))

        # 2. Right Action Buttons
        btn_box = tk.Frame(card, bg=panel_bg)
        btn_box.pack(side="right", fill="y", padx=(6, 0))

        del_btn = tk.Button(btn_box, text="🗑 Delete", font=FONT_SM, bg=danger_color, fg="white",
                            relief="flat", padx=6, pady=2, cursor="hand2",
                            command=lambda: self._delete_entry(eid))
        del_btn.pack(anchor="ne", pady=(0, 6))

        sweep_btn = tk.Button(btn_box, text="📸 Sweep", font=("Segoe UI", 8, "bold"),
                              bg=accent_color, fg=accent_fg,
                              relief="flat", padx=6, pady=3, cursor="hand2",
                              command=lambda: self._sweep_from_card(entry))
        sweep_btn.pack(anchor="se")

        # 3. Center Info Box
        info = tk.Frame(card, bg=panel_bg)
        info.pack(side="left", fill="both", expand=True)

        is_benign = entry.get("type") == "benign"
        badge_color = success_color if is_benign else danger_color
        variants_count = len(entry.get("variants", [])) or len(entry.get("hashes", [])) or 1

        cluster_tag = f" • 🔗 {variants_count} VARIANTS" if variants_count > 1 else ""
        badge_text = ("🟢 BENIGN PACKAGING" if is_benign else "🔴 KNOWN COUNTERFEIT") + cluster_tag

        b_lbl = tk.Label(info, text=badge_text, font=("Segoe UI", 8, "bold"), bg=panel_bg, fg=badge_color)
        b_lbl.pack(anchor="w")

        lbl_text = entry.get("label", "Packaging")
        if len(lbl_text) > 30: lbl_text = lbl_text[:28] + "..."
        name_lbl = tk.Label(info, text=lbl_text, font=FONT_BOLD, bg=panel_bg, fg=text_color)
        name_lbl.pack(anchor="w", pady=(1, 2))

        h_val = entry.get("hash", "")[:14] + "..."
        h_lbl = tk.Label(info, text=f"pHash: {h_val} | Matches: {entry.get('match_count', 0)}", font=FONT_SM,
                         bg=panel_bg, fg=subtext_color)
        h_lbl.pack(anchor="w")

        return card

    def _merge_selected_cards(self):
        if len(self.selected_card_ids) < 2:
            messagebox.showinfo("Select Items", "Please check at least 2 visual fingerprints to merge them into a unified Multi-Hash Threat Cluster.")
            return

        t = self.theme
        win = tk.Toplevel(self)
        win.title("Merge into Multi-Hash Threat Cluster")
        win.configure(bg=self._t("bg", "#121212"))
        win.geometry("480x240")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        selected_entries = [e for e in self.vcm.get_all_entries() if e.get("id") in self.selected_card_ids]
        suggested_label = selected_entries[0].get("label", "Threat Cluster")

        tk.Label(win, text="🔗 Unified Threat Cluster Name:", font=FONT_BOLD,
                 bg=self._t("bg", "#121212"), fg=self._t("text", "#ffffff")).pack(anchor="w", padx=16, pady=(16, 4))

        name_ent = tk.Entry(win, font=FONT_NORM, bg=self._t("entry_bg", "#1a1a1a"),
                            fg=self._t("text", "#ffffff"), insertbackground=self._t("text", "#ffffff"))
        name_ent.pack(fill="x", padx=16, pady=4)
        name_ent.insert(0, suggested_label)
        name_ent.focus_set()

        tk.Label(win, text=f"This will bundle {len(self.selected_card_ids)} photo fingerprints into 1 cluster.\nAny listing matching ANY of these angles/variants will trigger this threat!",
                 font=FONT_SM, bg=self._t("bg", "#121212"), fg=self._t("subtext", "#888888"), justify="left").pack(anchor="w", padx=16, pady=10)

        def _do_merge():
            cluster_name = name_ent.get().strip() or "Unified Threat Cluster"
            res = self.vcm.merge_entries(list(self.selected_card_ids), unified_label=cluster_name)
            win.destroy()
            self.selected_card_ids.clear()
            self.merge_btn.config(text="🔗 Merge Selected (0)")
            self._load_gallery()
            if self.on_update:
                self.on_update()
            messagebox.showinfo("Cluster Merged", f"Successfully created Multi-Hash Threat Cluster:\n'{cluster_name}'\n\nAll variant hashes are now active in parallel!")

        btn_box = tk.Frame(win, bg=self._t("bg", "#121212"))
        btn_box.pack(fill="x", padx=16, pady=14)
        tk.Button(btn_box, text="🔗 Merge Cluster", font=FONT_BOLD, bg=self._t("accent", "#00d2ff"),
                  fg="black" if self.theme.get("name","").startswith("⚡") else "white",
                  relief="flat", padx=12, pady=4, command=_do_merge).pack(side="right")
        tk.Button(btn_box, text="Cancel", font=FONT_NORM, bg=self._t("panel", "#1e1e1e"),
                  fg=self._t("subtext", "#888888"), relief="flat", padx=8, pady=4, command=win.destroy).pack(side="right", padx=6)

    def _sweep_from_card(self, entry):
        source = entry.get("source_url") or entry.get("thumb_path")
        if not source:
            messagebox.showwarning("Warning", "No source image available for this entry.")
            return
        lbl = entry.get("label", "Visual Reference")
        mkt = self.master.marketplace_var.get() if hasattr(self.master, "marketplace_var") else "eBay"
        
        reg = None
        if "Vinted" in mkt and hasattr(self.master, "vinted_country_var"):
            v_c = self.master.vinted_country_var.get()
            for code, names in {
                "UK": ["UK", "United Kingdom"], "FR": ["France", "FR"], "DE": ["Germany", "DE"],
                "ES": ["Spain", "ES"], "IT": ["Italy", "IT"], "PL": ["Poland", "PL"],
                "US": ["United States", "US"], "NL": ["Netherlands", "NL"], "BE": ["Belgium", "BE"],
                "All": ["All", "Europe", "Global"]
            }.items():
                if any(n in v_c for n in names):
                    reg = code
                    break
        elif "Mercado" in mkt and hasattr(self.master, "meli_country_var"):
            reg = self.master.meli_country_var.get()

        self.destroy()
        if hasattr(self.master, "_reverse_visual_search_from_url"):
            self.master._reverse_visual_search_from_url(source, label=lbl, marketplace=mkt, region=reg)

    def _delete_entry(self, entry_id):
        if messagebox.askyesno("Confirm Delete", "Remove this visual fingerprint from the catalog?"):
            self.vcm.remove_entry(entry_id)
            if entry_id in self.selected_card_ids:
                self.selected_card_ids.remove(entry_id)
                self.merge_btn.config(text=f"🔗 Merge Selected ({len(self.selected_card_ids)})")
            self._load_gallery()
            if self.on_update:
                self.on_update()

    def _add_from_file(self):
        fp = filedialog.askopenfilename(
            parent=self,
            title="Select Reference Packaging / Threat Photo",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
        )
        if not fp:
            return
        try:
            pil_img = Image.open(fp).convert("RGBA")
            self._prompt_save_entry(pil_img, source_path=fp)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def _add_from_url(self):
        panel_bg = self._t("panel", "#1e1e1e")
        text_color = self._t("text", "#ffffff")
        entry_bg = self._t("entry_bg", "#1a1a1a")
        accent_color = self._t("accent", "#00d2ff")
        subtext_color = self._t("subtext", "#888888")
        bg_color = self._t("bg", "#121212")

        win = tk.Toplevel(self)
        win.title("Add Visual Fingerprint from URL")
        win.configure(bg=bg_color)
        win.geometry("450x180")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="Direct Image URL (PNG, JPG, WebP):", font=FONT_BOLD, bg=bg_color, fg=text_color).pack(anchor="w", padx=14, pady=(12, 4))
        url_ent = tk.Entry(win, font=FONT_NORM, bg=entry_bg, fg=text_color, insertbackground=text_color)
        url_ent.pack(fill="x", padx=14, pady=4)
        url_ent.focus_set()

        def _fetch():
            url = url_ent.get().strip()
            if not url:
                return
            win.destroy()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = r.read()
                pil_img = Image.open(io.BytesIO(data)).convert("RGBA")
                self._prompt_save_entry(pil_img, source_url=url)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download image: {e}")

        btn_box = tk.Frame(win, bg=bg_color)
        btn_box.pack(fill="x", padx=14, pady=12)
        tk.Button(btn_box, text="Fetch & Add", font=FONT_BOLD, bg=accent_color, fg="white",
                  relief="flat", padx=10, pady=4, command=_fetch).pack(side="right")
        tk.Button(btn_box, text="Cancel", font=FONT_NORM, bg=panel_bg, fg=subtext_color,
                  relief="flat", padx=8, pady=4, command=win.destroy).pack(side="right", padx=6)

    def _prompt_save_entry(self, pil_img, source_path="", source_url=""):
        panel_bg = self._t("panel", "#1e1e1e")
        text_color = self._t("text", "#ffffff")
        entry_bg = self._t("entry_bg", "#1a1a1a")
        accent_color = self._t("accent", "#00d2ff")
        subtext_color = self._t("subtext", "#888888")
        bg_color = self._t("bg", "#121212")

        win = tk.Toplevel(self)
        win.title("Save Visual Threat Entry")
        win.configure(bg=bg_color)
        win.geometry("460x280")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        preview = pil_img.copy()
        preview.thumbnail((64, 64), Image.Resampling.LANCZOS)
        p_photo = ImageTk.PhotoImage(preview)
        self.photo_refs.append(p_photo)

        top_f = tk.Frame(win, bg=bg_color, padx=14, pady=10)
        top_f.pack(fill="x")
        tk.Label(top_f, image=p_photo, bg=entry_bg, width=64, height=64).pack(side="left", padx=(0, 10))

        tf_right = tk.Frame(top_f, bg=bg_color)
        tf_right.pack(side="left", fill="both", expand=True)
        tk.Label(tf_right, text="Catalog Classification:", font=FONT_BOLD, bg=bg_color, fg=text_color).pack(anchor="w")

        type_var = tk.StringVar(value="benign")
        tk.Radiobutton(tf_right, text="🟢 Known Benign Packaging", value="benign", variable=type_var,
                       font=FONT_NORM, bg=bg_color, fg=text_color, selectcolor=panel_bg).pack(anchor="w")
        tk.Radiobutton(tf_right, text="🔴 Known Counterfeit Photo", value="counterfeit", variable=type_var,
                       font=FONT_NORM, bg=bg_color, fg=text_color, selectcolor=panel_bg).pack(anchor="w")

        # Label input
        tk.Label(win, text="Descriptive Label (e.g. Denso Blue Box, Fake Holo 90919):", font=FONT_BOLD,
                 bg=bg_color, fg=text_color).pack(anchor="w", padx=14, pady=(6, 2))
        lbl_ent = tk.Entry(win, font=FONT_NORM, bg=entry_bg, fg=text_color, insertbackground=text_color)
        lbl_ent.pack(fill="x", padx=14, pady=4)
        if source_path:
            lbl_ent.insert(0, os.path.splitext(os.path.basename(source_path))[0])
        else:
            lbl_ent.insert(0, "Packaging Reference")
        lbl_ent.focus_set()

        def _save():
            label = lbl_ent.get().strip() or "Visual Entry"
            etype = type_var.get()
            self.vcm.add_entry(pil_img, entry_type=etype, label=label, source_url=source_url or source_path)
            win.destroy()
            self._load_gallery()
            if self.on_update:
                self.on_update()
            messagebox.showinfo("Saved", f"Fingerprint saved to {etype.upper()} catalog as '{label}'!")

        btn_box = tk.Frame(win, bg=bg_color)
        btn_box.pack(fill="x", padx=14, pady=14)
        tk.Button(btn_box, text="Save Fingerprint", font=FONT_BOLD, bg=accent_color, fg="white",
                  relief="flat", padx=12, pady=4, command=_save).pack(side="right")
        tk.Button(btn_box, text="Cancel", font=FONT_NORM, bg=panel_bg, fg=subtext_color,
                  relief="flat", padx=8, pady=4, command=win.destroy).pack(side="right", padx=6)
