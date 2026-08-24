"""
Apollo Brand Intelligence - Analyst HoverTip & Tooltip Engine
Provides non-intrusive, theme-adaptive hover tooltips for buttons, table headers,
and threat heuristics with adjustable dwell delay and global master toggle.
"""

import tkinter as tk
from typing import Callable, Optional, Union

class HoverTip:
    def __init__(
        self,
        widget: tk.Widget,
        text: Union[str, Callable[[], str]],
        delay_ms: int = 450,
        theme_provider: Optional[Callable[[], dict]] = None,
        is_enabled_callback: Optional[Callable[[], bool]] = None
    ):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.theme_provider = theme_provider
        self.is_enabled_callback = is_enabled_callback

        self._tip_window = None
        self._after_id = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, event=None):
        self._cancel()
        if self.is_enabled_callback and not self.is_enabled_callback():
            return
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _on_leave(self, event=None):
        self._cancel()
        self._hide()

    def _cancel(self):
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        if self.is_enabled_callback and not self.is_enabled_callback():
            return
        if self._tip_window or not self.widget.winfo_exists():
            return

        tip_text = self.text() if callable(self.text) else str(self.text)
        if not tip_text.strip():
            return

        # Theme colors
        t = self.theme_provider() if self.theme_provider else {}
        bg = t.get("accent", "#2563eb")
        fg = "white" if not str(t.get("name", "")).startswith("⚡") else "black"
        border_bg = t.get("border", "#334155")

        try:
            x = self.widget.winfo_rootx() + 10
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        except Exception:
            return

        # Ensure tooltip does not render off-screen
        screen_w = self.widget.winfo_screenwidth()
        screen_h = self.widget.winfo_screenheight()

        self._tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_attributes("-topmost", True)
        tw.config(bg=border_bg, padx=1, pady=1)

        inner = tk.Frame(tw, bg=bg, padx=8, pady=5)
        inner.pack(fill="both", expand=True)

        lbl = tk.Label(
            inner,
            text=tip_text,
            justify="left",
            bg=bg,
            fg=fg,
            font=("Segoe UI", 9),
            wraplength=380
        )
        lbl.pack()

        tw.update_idletasks()
        w = tw.winfo_width()
        h = tw.winfo_height()

        if x + w > screen_w - 10:
            x = max(10, screen_w - w - 10)
        if y + h > screen_h - 40:
            y = max(10, self.widget.winfo_rooty() - h - 6)

        tw.wm_geometry(f"+{x}+{y}")

    def _hide(self):
        if self._tip_window:
            try:
                self._tip_window.destroy()
            except Exception:
                pass
            self._tip_window = None


def add_tooltip(widget: tk.Widget, text: Union[str, Callable[[], str]], delay_ms: int = 450, theme_provider=None, is_enabled_callback=None) -> HoverTip:
    """Convenience helper to attach a HoverTip to any Tkinter widget."""
    return HoverTip(widget, text, delay_ms=delay_ms, theme_provider=theme_provider, is_enabled_callback=is_enabled_callback)
