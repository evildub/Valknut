import json
import os
import sys
import re
from datetime import datetime

def get_base_dir():
    """Return directory where executable/script lives to ensure persistent local storage."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

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
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
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
        with open(DATA_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

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
                # maybe it's a top-level model
                models = self._data["brands"][parent].setdefault("models", [])
                if model not in models:
                    models.append(model)
            self._save()
        except KeyError:
            pass

    def remove_brand_item(self, name):
        """Remove a brand/sub/model by name (searches all levels)."""
        brands = self._data["brands"]
        # top level
        if name in brands:
            del brands[name]
            self._save()
            return
        # sub level
        for parent, data in brands.items():
            if name in data.get("subs", {}):
                del data["subs"][name]
                self._save()
                return
            # model level
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

        # check if it's a parent brand
        if brand_name in brands:
            terms.extend(brands[brand_name].get("models", []))
            for sub, models in brands[brand_name].get("subs", {}).items():
                terms.append(sub)
                terms.extend(models)
            return terms

        # check if it's a sub-brand
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

    def save_preset(self, name, brand_keys):
        presets = self.get_presets()
        presets[name] = list(brand_keys)
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
            "seller": seller,
            "first_seen": now_str,
            "last_scanned": now_str,
            "scan_count": 0,
            "brands": [],
            "product_types": [],
            "total_listings": 0,
            "total_value": 0.0,
            "locations": [],
            "items": []
        })

        entry["last_scanned"] = now_str
        entry["scan_count"] += 1

        existing_item_ids = {it.get("item_id") for it in entry.get("items", []) if it.get("item_id")}

        for it in items:
            iid = str(it.get("item_id", "")).strip()
            brand = it.get("brand") or brand_name or "Unknown"
            pt = it.get("product_type", "")
            loc = it.get("location", "")
            price_str = str(it.get("price", ""))

            # Parse numeric price value
            m = re.search(r"[\d,]+(?:\.\d+)?", price_str)
            price_val = 0.0
            if m:
                try:
                    price_val = float(m.group(0).replace(",", ""))
                except ValueError:
                    price_val = 0.0

            if brand and brand not in entry["brands"]:
                entry["brands"].append(brand)
            if pt and pt not in entry["product_types"]:
                entry["product_types"].append(pt)
            if loc and loc not in entry["locations"]:
                entry["locations"].append(loc)

            # Deduplicate items recorded for this seller
            if not iid or iid not in existing_item_ids:
                if iid:
                    existing_item_ids.add(iid)
                entry["total_listings"] += 1
                entry["total_value"] = round(entry["total_value"] + price_val, 2)
                entry["items"].append({
                    "item_id": iid,
                    "title": it.get("title", ""),
                    "brand": brand,
                    "product_type": pt,
                    "price": price_str,
                    "price_val": price_val,
                    "seller": it.get("seller") or seller,
                    "location": loc,
                    "url": it.get("url", ""),
                    "scanned_at": now_str
                })

        self._data["enforcement_registry"] = reg
        self._save()

    def save_enforcement_registry(self, reg: dict):
        self._data["enforcement_registry"] = reg
        self._save()

    def clear_enforcement_registry(self):
        self._data["enforcement_registry"] = {}
        self._save()

    def delete_registry_entry(self, seller: str):
        reg = self.get_enforcement_registry()
        if seller in reg:
            del reg[seller]
            self._data["enforcement_registry"] = reg
            self._save()

    # ── whitelist / authorized dealers ─────────────────────────────────────────
    def get_whitelist(self) -> dict:
        """Return dict of whitelisted sellers {slug: {seller, brand, dealer_name, notes, added_at}}."""
        return self._data.setdefault("whitelist", {})

    def is_seller_whitelisted(self, seller_or_url: str) -> bool:
        """Check if seller handle or store slug is whitelisted (case-insensitive & hyphen-normalized)."""
        if not seller_or_url:
            return False
        raw = str(seller_or_url).strip().lower()
        if "/str/" in raw or "/usr/" in raw:
            raw = raw.split("/str/")[-1].split("/usr/")[-1].split("?")[0].split("/")[0].strip()
        slug = re.sub(r"[^a-z0-9]", "", raw)
        if not slug:
            return False
        
        wl = self.get_whitelist()
        for k in wl.keys():
            k_slug = re.sub(r"[^a-z0-9]", "", k.lower())
            if k_slug == slug:
                return True
        return False

    def add_to_whitelist(self, seller_handle: str, brand: str = "", dealer_name: str = "", notes: str = ""):
        """Add seller to authorized whitelist."""
        if not seller_handle:
            return
        wl = self.get_whitelist()
        clean_handle = seller_handle.strip()
        if "/str/" in clean_handle or "/usr/" in clean_handle:
            clean_handle = clean_handle.split("/str/")[-1].split("/usr/")[-1].split("?")[0].split("/")[0].strip()
        
        wl[clean_handle] = {
            "seller": clean_handle,
            "brand": brand.strip() if brand else "General / All Brands",
            "dealer_name": dealer_name.strip(),
            "notes": notes.strip(),
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self._data["whitelist"] = wl
        self._save()

    def remove_from_whitelist(self, seller_handle: str):
        """Remove seller from whitelist."""
        wl = self.get_whitelist()
        clean = seller_handle.strip()
        if clean in wl:
            del wl[clean]
            self._data["whitelist"] = wl
            self._save()
            return
        slug = re.sub(r"[^a-z0-9]", "", clean.lower())
        for k in list(wl.keys()):
            if re.sub(r"[^a-z0-9]", "", k.lower()) == slug:
                del wl[k]
                self._data["whitelist"] = wl
                self._save()
                break

    def bulk_add_whitelist(self, raw_text: str, brand: str = "", notes: str = "") -> int:
        """Bulk import lines of seller handles or store URLs."""
        if not raw_text:
            return 0
        added = 0
        for line in raw_text.splitlines():
            clean = line.strip()
            if not clean:
                continue
            if "/str/" in clean or "/usr/" in clean:
                clean = clean.split("/str/")[-1].split("/usr/")[-1].split("?")[0].split("/")[0].strip()
            m = re.search(r"([a-zA-Z0-9_.-]+)", clean)
            if m:
                handle = m.group(1).strip()
                if handle and not self.is_seller_whitelisted(handle):
                    self.add_to_whitelist(handle, brand=brand, notes=notes)
                    added += 1
        return added

    # ══════════════════════════════════════════════════════════════════════════
    #  SELLER THREAT INTEL & 3PL SMOKESCREEN REGISTRY
    # ══════════════════════════════════════════════════════════════════════════

    COUNTRY_FLAGS = {
        "china": "🇨🇳",
        "hong kong": "🇭🇰",
        "taiwan": "🇹🇼",
        "united states": "🇺🇸",
        "canada": "🇨🇦",
        "united kingdom": "🇬🇧",
        "germany": "🇩🇪",
        "japan": "🇯🇵",
        "south korea": "🇰🇷",
        "korea": "🇰🇷",
        "australia": "🇦🇺",
        "uganda": "🇺🇬",
        "sri lanka": "🇱🇰",
        "thailand": "🇹🇭",
        "malaysia": "🇲🇾",
        "united arab emirates": "🇦🇪",
        "uae": "🇦🇪",
        "dubai": "🇦🇪",
        "turkey": "🇹🇷",
        "argentina": "🇦🇷",
        "vietnam": "🇻🇳",
        "pakistan": "🇵🇰",
        "india": "🇮🇳",
        "indonesia": "🇮🇩",
        "philippines": "🇵🇭",
        "singapore": "🇸🇬",
        "israel": "🇮🇱",
        "nigeria": "🇳🇬",
        "kenya": "🇰🇪",
        "mexico": "🇲🇽",
        "brazil": "🇧🇷",
    }

    HIGH_RISK_JURISDICTIONS = {
        "china", "hong kong", "uganda", "sri lanka", "thailand",
        "malaysia", "united arab emirates", "uae", "dubai",
        "turkey", "argentina", "taiwan", "vietnam", "pakistan",
        "india", "indonesia", "philippines", "nigeria", "kenya"
    }

    KNOWN_3PL_HUBS = {
        "walton", "hebron", "erlanger", "florence, ky",
        "rowland heights", "city of industry", "industry, ca",
        "chino", "ontario, ca", "fontana", "gardena",
        "corona, ca", "la puente", "monterey park", "alhambra",
        "jamaica, ny", "springfield gardens", "flushing",
        "elk grove village", "wood dale",
        "avenel", "edison, nj", "dayton, nj", "carteret"
    }

    def get_seller_intel_cache(self) -> dict:
        """Returns cached seller intel mapping {seller_handle: {country, member_since, ...}}."""
        return self._data.get("seller_intel", {})

    def get_seller_intel(self, seller_handle: str) -> dict:
        """Retrieve cached threat intel for a specific seller handle."""
        if not seller_handle:
            return {}
        clean = seller_handle.strip().lower()
        intel_map = self.get_seller_intel_cache()
        if clean in intel_map:
            return intel_map[clean]
        slug = re.sub(r"[^a-z0-9]", "", clean)
        for k, v in intel_map.items():
            if re.sub(r"[^a-z0-9]", "", k.lower()) == slug:
                return v
        return {}

    def set_seller_intel(self, seller_handle: str, country: str, member_since: str = "", extra: dict = None):
        """Save resolved seller origin and threat data to persistent cache."""
        if not seller_handle:
            return
        clean = seller_handle.strip()
        intel_map = self.get_seller_intel_cache()
        record = {
            "seller": clean,
            "country": country.strip() if country else "Unknown",
            "member_since": member_since.strip() if member_since else "",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if extra:
            record.update(extra)
        intel_map[clean.lower()] = record
        self._data["seller_intel"] = intel_map
        self._save()

    def bulk_set_seller_intel(self, intel_dict: dict):
        """Batch save multiple seller intel records."""
        if not intel_dict:
            return
        intel_map = self.get_seller_intel_cache()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for s, data in intel_dict.items():
            clean = s.strip()
            if not clean:
                continue
            if isinstance(data, str):
                country_val = data
                m_since = ""
            elif isinstance(data, dict):
                country_val = data.get("country", "Unknown")
                m_since = data.get("member_since", "")
            else:
                country_val = str(data)
                m_since = ""
            intel_map[clean.lower()] = {
                "seller": clean,
                "country": country_val.strip() if country_val else "Unknown",
                "member_since": m_since,
                "updated_at": now_str
            }
        self._data["seller_intel"] = intel_map
        self._save()

    def compute_threat_assessment(self, seller_country: str, item_location: str) -> dict:
        """
        Evaluate seller registered country against declared item location to detect
        3PL drop-shipping smokescreens and cross-border counterfeit hubs.
        """
        country_clean = (seller_country or "").strip().lower()
        loc_clean = (item_location or "").strip().lower()
        flag = self.COUNTRY_FLAGS.get(country_clean, "🌍")

        is_high_risk = any(hr in country_clean for hr in self.HIGH_RISK_JURISDICTIONS)
        is_3pl_hub = any(hub in loc_clean for hub in self.KNOWN_3PL_HUBS)

        if not seller_country or country_clean in ("unknown", "unresolved", ""):
            if is_3pl_hub:
                return {
                    "score": "ELEVATED",
                    "badge": f"⚠️ KNOWN 3PL HUB ({item_location})",
                    "country": "Unknown",
                    "flag": "❓",
                    "is_high_risk": False,
                    "is_3pl_hub": True
                }
            return {
                "score": "UNKNOWN",
                "badge": "Unresolved Origin",
                "country": "Unknown",
                "flag": "❓",
                "is_high_risk": False,
                "is_3pl_hub": False
            }

        country_display = seller_country.title()

        if is_high_risk and is_3pl_hub:
            return {
                "score": "CRITICAL",
                "badge": f"🚨 GHOST ORIGIN ({country_display} {flag} | 3PL Hub: {item_location})",
                "country": country_display,
                "flag": flag,
                "is_high_risk": True,
                "is_3pl_hub": True
            }
        elif is_high_risk and any(us in loc_clean for us in ["united states", "us", "usa", "ca", "ny", "ky", "tx", "fl", "il"]):
            return {
                "score": "HIGH",
                "badge": f"🚨 OFFSHORE SMOKESCREEN ({country_display} {flag} | Item: US 3PL)",
                "country": country_display,
                "flag": flag,
                "is_high_risk": True,
                "is_3pl_hub": False
            }
        elif is_high_risk:
            return {
                "score": "HIGH",
                "badge": f"⚠️ HIGH-RISK ORIGIN ({country_display} {flag})",
                "country": country_display,
                "flag": flag,
                "is_high_risk": True,
                "is_3pl_hub": False
            }
        elif "united states" in country_clean or country_clean == "us":
            return {
                "score": "LOW",
                "badge": f"🛡️ Domestic Verified (US {flag})",
                "country": "United States",
                "flag": flag,
                "is_high_risk": False,
                "is_3pl_hub": is_3pl_hub
            }
        else:
            return {
                "score": "MEDIUM",
                "badge": f"🌍 Foreign ({country_display} {flag})",
                "country": country_display,
                "flag": flag,
                "is_high_risk": False,
                "is_3pl_hub": is_3pl_hub
            }


