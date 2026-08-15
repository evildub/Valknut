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
        return self._data["settings"].get(key, default)

    def set_setting(self, key, value):
        self._data["settings"][key] = value
        self._save()

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

    def clear_enforcement_registry(self):
        self._data["enforcement_registry"] = {}
        self._save()

    def delete_registry_entry(self, seller: str):
        reg = self.get_enforcement_registry()
        if seller in reg:
            del reg[seller]
            self._data["enforcement_registry"] = reg
            self._save()
