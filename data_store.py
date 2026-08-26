import json
import os
import sys
import shutil
import re
from datetime import datetime

def get_base_dir():
    """Return persistent user AppData directory to guarantee user configurations are never wiped by updates."""
    appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    user_dir = os.path.join(appdata, "Apollo_Brand_Intelligence")
    legacy_dir = os.path.join(appdata, "Valknut_Brand_Intelligence")

    # Seamless automatic migration from legacy Valknut directory if present
    if not os.path.exists(user_dir) and os.path.exists(legacy_dir):
        try:
            shutil.copytree(legacy_dir, user_dir)
        except Exception:
            pass

    os.makedirs(user_dir, exist_ok=True)
    return user_dir

DATA_FILE = os.path.join(get_base_dir(), "data.json")

DEFAULT_DATA = {
    "settings": {},
    "brands": {
        "Toyota": {
            "subs": {
                "Lexus": ["ES", "RX", "GX", "IS", "LS"]
            },
            "models": ["Camry", "Corolla", "Tacoma", "Tundra", "RAV4",
                       "Highlander", "4Runner", "Prius", "Supra", "Avalon"]
        },
        "General Motors": {
            "subs": {
                "Chevrolet": ["Corvette", "Camaro", "Silverado", "Blazer", "Malibu", "Tahoe", "Suburban"],
                "GMC":       ["Sierra", "Canyon", "Yukon", "Terrain", "Acadia", "Envoy"],
                "Buick":     ["Enclave", "Encore", "Envision", "LaCrosse"],
                "Cadillac":  ["Escalade", "CT5", "CT4", "XT5", "XT6"]
            },
            "models": []
        },
        "Subaru": {
            "subs": {},
            "models": ["Outback", "Forester", "Impreza", "WRX", "Legacy",
                       "Ascent", "Crosstrek", "BRZ", "Solterra"]
        },
        "Hyundai": {
            "subs": {
                "Kia": ["Sportage", "Sorento", "Telluride", "Stinger",
                        "Soul", "Forte", "K5", "Carnival"],
                "Genesis": ["G70", "G80", "G90", "GV70", "GV80"]
            },
            "models": ["Elantra", "Sonata", "Tucson", "Santa Fe",
                       "Palisade", "Kona", "Veloster", "Ioniq"]
        },
        "Nike": {
            "subs": {
                "Jordan": ["Retro 1", "Retro 4", "Retro 11", "Spizike", "Jumpman"],
                "Nike SB": ["Dunk Low", "Dunk High", "Stefan Janoski", "Travis Scott"],
                "Sportswear": ["Tech Fleece", "Club Fleece", "Windrunner", "Center Swoosh"]
            },
            "models": ["Dunk Low", "Air Force 1", "Air Max 90", "Air Max 95", "Air Max Plus TN",
                       "Tech Fleece Hoodie", "Tech Fleece Joggers", "VaporMax", "Cortez", "Blazer Mid", "Vintage Sweatshirt"]
        }
    },
    "exclusions": [
        "Toyota", "Honda", "Ford", "Chevrolet", "Dodge", "Jeep",
        "Nissan", "Mazda", "Mitsubishi", "Volkswagen", "BMW",
        "Mercedes", "Audi", "Hyundai", "Kia", "Subaru",
        "aftermarket", "compatible", "fits"
    ]
}


class DataStore:
    def __init__(self):
        # Initial migration: check if local directory data.json exists and migrate to AppData
        if not os.path.exists(DATA_FILE):
            local_src = os.path.join(os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__), "data.json")
            if os.path.exists(local_src):
                try:
                    shutil.copyfile(local_src, DATA_FILE)
                except Exception:
                    pass

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            # migrate old format if needed
            for brand, val in self._data.get("brands", {}).items():
                if not isinstance(val, dict):
                    self._data["brands"][brand] = {"subs": {}, "models": []}
                else:
                    val.setdefault("subs", {})
                    val.setdefault("models", [])
        else:
            self._data = DEFAULT_DATA
            self._save()

    def _save(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # ── settings ──────────────────────────────────────────────────────────────
    def get_setting(self, key, default=""):
        return self._data.get("settings", {}).get(key, default)

    def set_setting(self, key, value):
        self._data.setdefault("settings", {})[key] = value
        self._save()

    def is_wick_unlocked(self) -> bool:
        return bool(self.get_setting("unlocked_wick", False))

    def unlock_wick(self):
        self.set_setting("unlocked_wick", True)

    # ── brands ────────────────────────────────────────────────────────────────
    def get_brands(self):
        return self._data.get("brands", {})

    def add_parent_brand(self, name):
        if name not in self._data["brands"]:
            self._data["brands"][name] = {"subs": {}, "models": []}
            self._save()

    def add_sub_brand(self, parent, name):
        if parent in self._data["brands"]:
            self._data["brands"][parent]["subs"].setdefault(name, [])
            self._save()

    def add_model(self, parent, sub, model):
        try:
            subs = self._data["brands"][parent]["subs"]
            if sub in subs:
                if model not in subs[sub]:
                    subs[sub].append(model)
            else:
                models = self._data["brands"][parent].setdefault("models", [])
                if model not in models:
                    models.append(model)
            self._save()
        except KeyError:
            pass

    def remove_brand_item(self, name):
        """Remove a brand/sub/model by name (searches all levels)."""
        brands = self._data["brands"]
        if name in brands:
            del brands[name]
            self._save()
            return
        for parent, data in brands.items():
            if name in data.get("subs", {}):
                del data["subs"][name]
                self._save()
                return
            if name in data.get("models", []):
                data["models"].remove(name)
                self._save()
                return
            for sub, models in data.get("subs", {}).items():
                if name in models:
                    models.remove(name)
                    self._save()
                    return

    def reorder_parent_brands(self, new_order: list[str]):
        """Persist new parent brand ordering."""
        new_brands = {}
        for k in new_order:
            if k in self._data["brands"]:
                new_brands[k] = self._data["brands"][k]
        for k, v in self._data["brands"].items():
            if k not in new_brands:
                new_brands[k] = v
        self._data["brands"] = new_brands
        self._save()

    def reorder_models(self, parent_name: str, sub_name: str, new_models: list[str]):
        """Persist new model ordering for a parent or sub-brand."""
        if parent_name in self._data["brands"]:
            if sub_name and sub_name in self._data["brands"][parent_name].get("subs", {}):
                self._data["brands"][parent_name]["subs"][sub_name] = new_models
            else:
                self._data["brands"][parent_name]["models"] = new_models
            self._save()

    def reorder_subs(self, parent_name: str, new_subs: list[str]):
        """Persist new sub-brand ordering under a parent brand."""
        if parent_name in self._data["brands"]:
            existing_subs = self._data["brands"][parent_name].get("subs", {})
            new_sub_dict = {}
            for s in new_subs:
                if s in existing_subs:
                    new_sub_dict[s] = existing_subs[s]
            for s, v in existing_subs.items():
                if s not in new_sub_dict:
                    new_sub_dict[s] = v
            self._data["brands"][parent_name]["subs"] = new_sub_dict
            self._save()

    def get_terms_for_brand(self, brand_name):
        """Return the brand name + all its models as search terms."""
        brands = self._data["brands"]
        terms = [brand_name]
        if brand_name in brands:
            terms.extend(brands[brand_name].get("models", []))
            for sub, models in brands[brand_name].get("subs", {}).items():
                terms.append(sub)
                terms.extend(models)
            return terms
        for parent, data in brands.items():
            if brand_name in data.get("subs", {}):
                terms.extend(data["subs"][brand_name])
                return terms
        return terms

    # ── exclusions ────────────────────────────────────────────────────────────
    def get_exclusions(self):
        return self._data.get("exclusions", [])

    def add_exclusion(self, term):
        if term not in self._data["exclusions"]:
            self._data["exclusions"].append(term)
            self._save()

    def remove_exclusion(self, term):
        if term in self._data["exclusions"]:
            self._data["exclusions"].remove(term)
            self._save()

    # ── presets / portfolio bundles ───────────────────────────────────────────
    def get_presets(self):
        default_presets = {
            "🏢 Dub's Automotive Portfolio (Toyota, GM, Subaru, Hyundai/Kia)": [
                "Toyota", "Lexus", "General Motors", "Chevrolet", "ACDelco", "Subaru", "Hyundai", "Kia"
            ],
            "🏁 Toyota & Lexus Full Sweep": [
                "Toyota", "Lexus"
            ],
            "💎 GM & ACDelco Big 4 (Chevy, GMC, Buick, Cadillac, ACDelco)": [
                "General Motors", "Chevrolet", "GMC", "Buick", "Cadillac", "ACDelco"
            ],
            "🔥 MOPAR & Honda Suite (Dodge, Jeep, Honda, Acura)": [
                "Dodge", "Jeep", "Chrysler", "RAM", "Honda", "Acura"
            ],
            "🌐 Complete All-Brands Store Sweep": list(self.get_brands().keys())
        }
        presets = self._data.setdefault("presets", default_presets)
        return presets

    def save_preset(self, name, preset_payload):
        """Save a portfolio preset. Accepts either a list of brands or a full snapshot dict."""
        presets = self.get_presets()
        if isinstance(preset_payload, dict):
            presets[name] = {
                "brands": list(preset_payload.get("brands", [])),
                "generic_excludes": list(preset_payload.get("generic_excludes", [])),
                "custom_includes": list(preset_payload.get("custom_includes", [])),
                "condition": preset_payload.get("condition", "all")
            }
        else:
            presets[name] = list(preset_payload)
        self._data["presets"] = presets
        self._save()

    def delete_preset(self, name):
        presets = self.get_presets()
        if name in presets:
            del presets[name]
            self._data["presets"] = presets
            self._save()

    # ── Enforcement & Recidivism Registry (A2C2 / Brand Protection) ──────────
    def get_enforcement_registry(self):
        return self._data.setdefault("enforcement_registry", {})

    def record_enforcement_scan(self, seller_or_store: str, items: list, brand_name: str = ""):
        """Record harvested results for a seller into the permanent enforcement registry."""
        if not seller_or_store or not seller_or_store.strip():
            return
        seller = seller_or_store.strip()
        reg = self.get_enforcement_registry()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = reg.setdefault(seller, {
            "seller_handle": seller,
            "first_detected": now_str,
            "last_scanned": now_str,
            "total_infringements": 0,
            "total_clean_items": 0,
            "brands_targeted": [],
            "risk_tier": "Low",
            "historical_scan_count": 0,
            "strike_history": []
        })

        entry["last_scanned"] = now_str
        entry["historical_scan_count"] = entry.get("historical_scan_count", 0) + 1

        if brand_name and brand_name not in entry.get("brands_targeted", []):
            entry.setdefault("brands_targeted", []).append(brand_name)

        flagged_items = []
        for itm in items:
            t_score = itm.get("threat_score", 0)
            is_cf = (
                itm.get("high_risk") or 
                itm.get("counterfeit") or 
                itm.get("visual_counterfeit") or
                t_score >= 70 or 
                any(kw in str(itm.get("threat_badge", "")).lower() for kw in ("counterfeit", "syndicate", "flagged"))
            )
            if is_cf:
                entry["total_infringements"] = entry.get("total_infringements", 0) + 1
                flagged_items.append({
                    "item_id": itm.get("item_id"),
                    "title": itm.get("title"),
                    "price": itm.get("price"),
                    "threat_score": t_score,
                    "threat_badge": itm.get("threat_badge", ""),
                    "timestamp": now_str
                })
            else:
                entry["total_clean_items"] = entry.get("total_clean_items", 0) + 1

        total_bad = entry.get("total_infringements", 0)
        total_good = entry.get("total_clean_items", 0)
        total_all = total_bad + total_good

        if total_bad >= 20 or (total_all > 0 and (total_bad / total_all) >= 0.5 and total_bad >= 5):
            entry["risk_tier"] = "🚨 Critical Recidivist (Syndicate)"
        elif total_bad >= 5:
            entry["risk_tier"] = "⚠️ High Risk (Repeat Offender)"
        elif total_bad >= 1:
            entry["risk_tier"] = "🟡 Moderate (Flagged)"
        else:
            entry["risk_tier"] = "🟢 Clean / Low"

        if flagged_items:
            entry.setdefault("strike_history", []).append({
                "scan_date": now_str,
                "flagged_count": len(flagged_items),
                "sample_items": flagged_items[:5]
            })

        self._save()

    def get_seller_intel(self, seller_handle: str) -> dict:
        """Retrieve cached threat intel profile for a seller."""
        intel_cache = self._data.setdefault("seller_intel_cache", {})
        return intel_cache.get(seller_handle.strip(), {})

    def set_seller_intel(self, seller_handle: str, country: str, member_since: str = ""):
        """Cache resolved location & age for a seller handle."""
        if not seller_handle or not seller_handle.strip():
            return
        intel_cache = self._data.setdefault("seller_intel_cache", {})
        intel_cache[seller_handle.strip()] = {
            "country": country,
            "member_since": member_since,
            "resolved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save()

    COUNTRY_FLAGS = {
        "china": "🇨🇳", "cn": "🇨🇳", "hong kong": "🇭🇰", "hk": "🇭🇰",
        "united states": "🇺🇸", "us": "🇺🇸", "usa": "🇺🇸",
        "united kingdom": "🇬🇧", "uk": "🇬🇧", "gb": "🇬🇧",
        "france": "🇫🇷", "fr": "🇫🇷",
        "germany": "🇩🇪", "de": "🇩🇪",
        "spain": "🇪🇸", "es": "🇪🇸",
        "italy": "🇮🇹", "it": "🇮🇹",
        "poland": "🇵🇱", "pl": "🇵🇱",
        "mexico": "🇲🇽", "mx": "🇲🇽",
        "brazil": "🇧🇷", "br": "🇧🇷",
        "argentina": "🇦🇷", "ar": "🇦🇷",
        "colombia": "🇨🇴", "co": "🇨🇴",
        "chile": "🇨🇱", "cl": "🇨🇱",
        "peru": "🇵🇪", "pe": "🇵🇪",
        "netherlands": "🇳🇱", "nl": "🇳🇱",
        "belgium": "🇧🇪", "be": "🇧🇪",
        "japan": "🇯🇵", "jp": "🇯🇵",
        "canada": "🇨🇦", "ca": "🇨🇦",
        "australia": "🇦🇺", "au": "🇦🇺",
        "turkey": "🇹🇷", "tr": "🇹🇷",
        "vietnam": "🇻🇳", "vn": "🇻🇳",
        "taiwan": "🇹🇼", "tw": "🇹🇼",
        "thailand": "🇹🇭", "th": "🇹🇭",
        "india": "🇮🇳", "in": "🇮🇳",
    }

    def compute_threat_assessment(self, origin: str, location: str = "") -> dict:
        """
        Compute high-risk cross-border threat badge and 3PL hub assessment from seller origin and item location.
        """
        orig_clean = str(origin or "").strip().lower()
        loc_clean = str(location or "").strip().lower()

        is_china = any(k in orig_clean or k in loc_clean for k in ("china", "cn", "hong kong", "hk", "shenzhen", "guangdong", "zhejiang", "yiwu", "beijing", "shanghai"))
        is_3pl = False
        if is_china and any(d in loc_clean for d in ("united states", "usa", "us", "california", "ca", "nj", "new jersey", "uk", "united kingdom", "germany", "de", "france", "fr", "spain", "es", "italy", "it", "poland", "pl")):
            is_3pl = True

        country_resolved = "Unknown"
        for cname in self.COUNTRY_FLAGS.keys():
            if cname in orig_clean or cname in loc_clean:
                country_resolved = cname.title()
                break

        badge = "Unresolved"
        is_high = False

        if is_3pl:
            badge = "🚨 Foreign Drop-Ship Hub"
            is_high = True
        elif is_china:
            badge = "⚠️ Cross-Border Direct"
            is_high = True
        elif any(c in orig_clean or c in loc_clean for c in ("mexico", "brazil", "argentina", "colombia", "chile", "peru")):
            badge = "🌎 Latin America Hub"
            is_high = False
        elif any(c in orig_clean or c in loc_clean for c in ("united kingdom", "uk", "france", "germany", "spain", "italy", "poland", "netherlands", "belgium")):
            badge = "🇪🇺 European Direct"
            is_high = False
        elif any(c in orig_clean or c in loc_clean for c in ("united states", "usa", "us")):
            badge = "🇺🇸 Domestic Verified"
            is_high = False
        return {
            "country": country_resolved if country_resolved != "Unknown" else (origin or location or "Unresolved"),
            "badge": badge,
            "is_high_risk": is_high,
            "is_3pl_hub": is_3pl
        }

    def get_column_visibility(self) -> dict:
        """Get column visibility configuration, defaulting to all visible except thumbnail."""
        defaults = {
            "brand": True,
            "product_type": True,
            "title": True,
            "item_id": True,
            "price": True,
            "seller": True,
            "seller_origin": True,
            "threat_badge": True,
            "location": True,
            "thumbnail": False,
            "url": True
        }
        saved = self._data.setdefault("settings", {}).get("column_visibility", {})
        merged = defaults.copy()
        merged.update(saved)
        return merged

    def set_column_visibility(self, visibility_dict: dict):
        """Persist column visibility dictionary."""
        self._data.setdefault("settings", {})["column_visibility"] = visibility_dict
        self._save()

    def set_single_column_visibility(self, col: str, visible: bool):
        """Update single column visibility state."""
        current = self.get_column_visibility()
        current[col] = bool(visible)
        self.set_column_visibility(current)

    def get_show_analyst_hints(self) -> bool:
        """Check if analyst hover onboarding tooltips are enabled."""
        return self._data.setdefault("settings", {}).get("show_analyst_hints", True)

    def set_show_analyst_hints(self, enabled: bool):
        """Set analyst hover onboarding tooltips setting."""
        self._data.setdefault("settings", {})["show_analyst_hints"] = bool(enabled)
        self._save()

    # ── authorized dealer whitelist ───────────────────────────────────────────
    def get_whitelist(self) -> dict:
        """Get dictionary of all whitelisted sellers/dealers."""
        return self._data.setdefault("whitelist", {})

    def is_seller_whitelisted(self, seller_handle: str) -> bool:
        """Check if seller handle is on authorized dealer whitelist."""
        if not seller_handle:
            return False
        clean = str(seller_handle).strip().lower()
        wl = self.get_whitelist()
        for k in wl.keys():
            if str(k).strip().lower() == clean:
                return True
        return False

    def add_to_whitelist(self, seller_handle: str, brand: str = "General", dealer_name: str = "", notes: str = ""):
        """Add or update an authorized dealer on the whitelist."""
        if not seller_handle:
            return
        clean = str(seller_handle).strip()
        wl = self.get_whitelist()
        import datetime
        now_str = datetime.datetime.now().strftime("%Y-%m-%d")
        wl[clean] = {
            "brand": brand or "General",
            "dealer_name": dealer_name or "Authorized Dealership",
            "notes": notes or "",
            "date_added": now_str
        }
        self._save()

    def remove_from_whitelist(self, seller_handle: str):
        """Remove a seller from the authorized dealer whitelist."""
        if not seller_handle:
            return
        clean = str(seller_handle).strip().lower()
        wl = self.get_whitelist()
        found_key = None
        for k in wl.keys():
            if str(k).strip().lower() == clean:
                found_key = k
                break
        if found_key and found_key in wl:
            del wl[found_key]
            self._save()
