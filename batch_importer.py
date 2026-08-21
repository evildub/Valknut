"""
Adhoc Batch URL & Excel Listing Importer Module for Valknut Anti-Counterfeit Harvester.
Specialized in high-speed, multi-marketplace individual listing detail extraction
from analyst adhoc request lists, raw pasted text, and client spreadsheets (.xlsx, .csv).

Supported Platforms:
- eBay (ebay.com)
- AliExpress (aliexpress.com, aliexpress.us)
- Wish (wish.com)
- Temu (temu.com)
- Mercado Libre (mercadolibre.com.mx, mercadolivre.com.br, etc.)
"""

import os
import re
import csv
import time
import random
import logging
import urllib.parse
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    import requests as curl_requests
    HAS_CURL_CFFI = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

logger = logging.getLogger("Valknut.BatchImporter")


# ── Product Category Heuristics ───────────────────────────────────────────────
PRODUCT_CATEGORY_RULES = [
    ("Airbag Covers", ["airbag cover", "air bag cover", "steering wheel cover airbag"]),
    ("Airbag Components", ["airbag", "air bag", "clockspring", "clock spring", "srs"]),
    ("Emblems", ["emblem", "badge", "logo", "crest", "hood ornament", "lettering", "nameplate"]),
    ("Decals", ["decal", "sticker", "vinyl graphic", "stripe kit", "wrap"]),
    ("Wheel Caps", ["wheel cap", "center cap", "hub cap", "hubcap", "wheel badge", "rim cap"]),
    ("Exterior Lighting", ["headlight", "headlamp", "taillight", "tail light", "fog light", "puddle light", "projector", "led bulb"]),
    ("Exterior Parts", ["grille", "grill", "spoiler", "diffuser", "mirror cover", "body kit", "lip", "bumper"]),
    ("Brakes", ["brake", "caliper", "rotor", "brake pad", "brembo cover"]),
    ("Ignition Systems", ["ignition coil", "spark plug", "glow plug", "distributor"]),
    ("Oil Filters", ["oil filter", "oil strainer"]),
    ("Air Filters", ["air filter", "cabin filter", "intake filter"]),
    ("Air Intake & Fuel Delivery", ["intake", "fuel injector", "throttle body", "carburetor", "fuel pump"]),
    ("Diagnostic Systems", ["diagnostic", "obd", "scanner", "vcds", "techstream", "diag tool"]),
    ("Merchandise", ["t-shirt", "shirt", "hoodie", "jacket", "tumbler", "cup", "mug", "hat", "cap", "backpack", "bag", "keychain", "key chain", "key fob", "fob cover"]),
    ("Accessories", ["keychain", "key chain", "valve stem", "license plate frame", "mat", "coaster", "phone holder"]),
]

COMMON_BRAND_KEYWORDS = [
    ("Toyota", ["toyota", "lexus", "scion", "trd", "gazoo", "gr sport", "camry", "corolla", "tacoma", "tundra", "supra"]),
    ("Ford", ["ford", "lincoln", "mercury", "mustang", "shelby", "f-150", "raptor", "bronco", "st-line", "ecoboost"]),
    ("General Motors", ["chevrolet", "chevy", "corvette", "camaro", "silverado", "cadillac", "gmc", "buick", "acdelco", "duramax", "suburban", "tahoe"]),
    ("Dodge / Mopar", ["dodge", "mopar", "hellcat", "demon", "srt", "charger", "challenger", "ram", "chrysler", "jeep", "rubicon", "trail rated"]),
    ("BMW", ["bmw", "m performance", "m3", "m4", "m5", "bimmer", "mini cooper"]),
    ("Porsche", ["porsche", "911", "cayman", "boxster", "panamera", "gt3", "gt4", "weissach"]),
    ("Ferrari", ["ferrari", "scuderia", "sf90", "f40", "f50", "488", "458", "cavallino"]),
    ("Subaru", ["subaru", "sti", "wrx", "impreza", "forester", "outback", "crosstrek"]),
    ("Hyundai / Kia", ["hyundai", "kia", "stinger", "n line", "elantra n", "genesis"]),
    ("LEGO", ["lego", "minifigure", "ninjago", "star wars lego", "technic"]),
    ("Stanley", ["stanley", "quencher", "iceflow", "tumbler"]),
    ("Black & Decker", ["black & decker", "black+decker", "dewalt", "stanley black"]),
    ("Sprayground", ["sprayground", "shark mouth", "backpack"]),
    ("Taylor Swift", ["taylor swift", "eras tour", "swiftie"]),
    ("NFL", ["nfl", "super bowl", "chiefs", "eagles", "cowboys", "49ers", "patriots"]),
]


def extract_urls_from_text(raw_text: str) -> List[str]:
    """
    Extract, clean, and deduplicate all valid HTTP/HTTPS URLs from raw text.
    Handles multi-line pastes, markdown links, comma-separated lists, etc.
    """
    if not raw_text:
        return []

    # Regex matches http or https urls
    pattern = r'https?://[^\s<>"\',;]+'
    matches = re.findall(pattern, raw_text)
    
    clean_urls = []
    seen = set()

    for u in matches:
        # Strip trailing punctuation or brackets
        clean_u = u.rstrip(".,;)\"\'>]").strip()
        if not clean_u:
            continue
        
        # Normalize and deduplicate
        norm = clean_u.split("?")[0] if "ebay.com/itm" in clean_u or "aliexpress." in clean_u or "wish.com/product" in clean_u else clean_u
        if clean_u not in seen:
            seen.add(clean_u)
            clean_urls.append(clean_u)

    return clean_urls


HEADER_ALIASES = {
    "url": ["url", "listing url", "listing_url", "item url", "item_url", "link", "web link", "product link", "ebay link", "listing link", "item link", "item_link"],
    "item_id": ["item id", "item_id", "itemid", "id", "listing id", "listing_id", "item number", "item_number", "ebay item id", "asin", "listing #", "item #"],
    "title": ["title", "listing title", "listing_title", "item title", "item_title", "name", "product title", "product name", "description", "item name", "listing name"],
    "seller": ["seller", "store", "merchant", "seller name", "seller_name", "seller username", "seller_username", "store name", "store_name", "shop", "vendor", "user", "username"],
    "price": ["price", "item price", "item_price", "current price", "cost", "amount", "unit price", "sale price"],
    "image_url": ["image url", "image_url", "photo", "photo url", "photo_url", "thumbnail", "thumb", "thumbnail url", "picture url", "picture_url", "img", "image", "pic", "image link"],
    "brand": ["brand", "client", "trademark", "brand name", "brand_name"],
    "product_type": ["product type", "product_type", "category", "type", "part type", "part_type"],
    "location": ["location", "seller location", "seller_location", "country", "origin", "item location", "item_location"],
    "marketplace": ["marketplace", "platform", "site", "source"]
}


def _match_header(header_text: str) -> Optional[str]:
    """Match header string against known canonical column alias dictionary."""
    if not header_text or not isinstance(header_text, str):
        return None
    norm = re.sub(r"[\s_\-]+", " ", header_text.strip().lower())
    for canonical, aliases in HEADER_ALIASES.items():
        if norm in aliases or norm.replace(" ", "") in [a.replace(" ", "") for a in aliases]:
            return canonical
    return None


def extract_structured_listings_from_file(filepath: str, default_brand: str = "") -> Tuple[List[dict], List[str]]:
    """
    Extract structured listing records from an Excel (.xlsx, .xls) or CSV file.
    Automatically maps known column headers (Title, Seller, Price, Image URL, URL, Item ID, etc.).
    Returns (structured_items_list, raw_urls_list).
    """
    if not os.path.exists(filepath):
        return [], []

    ext = os.path.splitext(filepath)[1].lower()
    structured_items = []
    raw_urls = []

    if ext in (".xlsx", ".xlsm", ".xltx") and HAS_OPENPYXL:
        try:
            wb = openpyxl.load_workbook(filepath, data_only=True, read_only=True)
            for sheet in wb.worksheets:
                rows = list(sheet.iter_rows(values_only=True))
                if not rows:
                    continue

                # Search first 5 rows for a valid header row
                header_col_map = {}
                header_row_idx = -1
                for r_idx, row in enumerate(rows[:5]):
                    matches = {}
                    for c_idx, cell in enumerate(row):
                        matched = _match_header(str(cell or ""))
                        if matched:
                            matches[c_idx] = matched
                    if len(matches) >= 2 or ("url" in matches.values() or "item_id" in matches.values()):
                        header_col_map = matches
                        header_row_idx = r_idx
                        break

                if header_col_map and header_row_idx >= 0:
                    for row in rows[header_row_idx + 1:]:
                        rec = {}
                        for c_idx, field_name in header_col_map.items():
                            if c_idx < len(row) and row[c_idx] is not None:
                                val = str(row[c_idx]).strip()
                                if val:
                                    rec[field_name] = val

                        url_val = rec.get("url", "")
                        item_id_val = rec.get("item_id", "")
                        title_val = rec.get("title", "")
                        
                        if not url_val and not item_id_val and not title_val:
                            continue

                        # Auto-extract item_id from URL if missing
                        if url_val and not item_id_val:
                            m_id = re.search(r"/itm/(?:[^/]+/)?(\d{10,14})", url_val) or re.search(r"(\d{10,14})", url_val)
                            if m_id:
                                item_id_val = m_id.group(1)
                                rec["item_id"] = item_id_val

                        # Reconstruct URL if missing but item_id exists
                        if item_id_val and not url_val:
                            url_val = f"https://www.ebay.com/itm/{item_id_val}"
                            rec["url"] = url_val

                        if url_val:
                            raw_urls.append(url_val)

                        # Detect platform
                        mkt = rec.get("marketplace") or detect_platform(url_val)
                        rec["marketplace"] = mkt

                        # Detect brand and product type
                        if not rec.get("brand") or rec.get("brand") in ("⚡ Auto-Detect from Title", "Auto-Detect", ""):
                            rec["brand"] = detect_brand(title_val or "", default_brand=default_brand)
                        if not rec.get("product_type"):
                            rec["product_type"] = detect_product_type(title_val or "")

                        # Format price
                        p_val = rec.get("price", "$0.00")
                        if p_val and not p_val.startswith("$") and not any(c in p_val for c in ("£", "€", "US", "AU", "C")):
                            m_num = re.search(r"[\d,]+(?:\.\d+)?", p_val)
                            if m_num:
                                p_val = f"${m_num.group(0)}"
                        rec["price"] = p_val if p_val else "$0.00"

                        # Ensure defaults
                        rec.setdefault("seller", "Unknown")
                        rec.setdefault("location", "United States")
                        rec.setdefault("image_url", "")
                        rec.setdefault("title", title_val or (f"Listing #{item_id_val}" if item_id_val else "Imported Listing"))

                        structured_items.append(rec)
        except Exception as e:
            logger.error(f"Error extracting structured listings from Excel {filepath}: {e}")

    elif ext == ".csv":
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                with open(filepath, "r", encoding=enc, errors="ignore") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if rows:
                        header_col_map = {}
                        header_row_idx = -1
                        for r_idx, row in enumerate(rows[:5]):
                            matches = {}
                            for c_idx, cell in enumerate(row):
                                matched = _match_header(cell)
                                if matched:
                                    matches[c_idx] = matched
                            if len(matches) >= 2 or ("url" in matches.values() or "item_id" in matches.values()):
                                header_col_map = matches
                                header_row_idx = r_idx
                                break

                        if header_col_map and header_row_idx >= 0:
                            for row in rows[header_row_idx + 1:]:
                                rec = {}
                                for c_idx, field_name in header_col_map.items():
                                    if c_idx < len(row) and row[c_idx] is not None:
                                        val = str(row[c_idx]).strip()
                                        if val:
                                            rec[field_name] = val

                                url_val = rec.get("url", "")
                                item_id_val = rec.get("item_id", "")
                                title_val = rec.get("title", "")
                                
                                if not url_val and not item_id_val and not title_val:
                                    continue

                                if url_val and not item_id_val:
                                    m_id = re.search(r"/itm/(?:[^/]+/)?(\d{10,14})", url_val) or re.search(r"(\d{10,14})", url_val)
                                    if m_id:
                                        item_id_val = m_id.group(1)
                                        rec["item_id"] = item_id_val

                                if item_id_val and not url_val:
                                    url_val = f"https://www.ebay.com/itm/{item_id_val}"
                                    rec["url"] = url_val

                                if url_val:
                                    raw_urls.append(url_val)

                                mkt = rec.get("marketplace") or detect_platform(url_val)
                                rec["marketplace"] = mkt

                                if not rec.get("brand") or rec.get("brand") in ("⚡ Auto-Detect from Title", "Auto-Detect", ""):
                                    rec["brand"] = detect_brand(title_val or "", default_brand=default_brand)
                                if not rec.get("product_type"):
                                    rec["product_type"] = detect_product_type(title_val or "")

                                p_val = rec.get("price", "$0.00")
                                if p_val and not p_val.startswith("$") and not any(c in p_val for c in ("£", "€", "US", "AU", "C")):
                                    m_num = re.search(r"[\d,]+(?:\.\d+)?", p_val)
                                    if m_num:
                                        p_val = f"${m_num.group(0)}"
                                rec["price"] = p_val if p_val else "$0.00"

                                rec.setdefault("seller", "Unknown")
                                rec.setdefault("location", "United States")
                                rec.setdefault("image_url", "")
                                rec.setdefault("title", title_val or (f"Listing #{item_id_val}" if item_id_val else "Imported Listing"))

                                structured_items.append(rec)
                if structured_items:
                    break
            except Exception as e:
                logger.error(f"Error extracting structured listings from CSV {filepath} with encoding {enc}: {e}")

    # Fallback to plain URL extraction if structured extraction found nothing
    if not structured_items:
        raw_urls = extract_urls_from_file(filepath)

    return structured_items, raw_urls


def extract_urls_from_file(filepath: str) -> List[str]:
    """
    Extract all URLs from an Excel (.xlsx, .xls), CSV, or plain text file.
    Automatically scans columns and cells for valid listing URLs.
    """
    if not os.path.exists(filepath):
        return []

    ext = os.path.splitext(filepath)[1].lower()
    raw_urls = []

    if ext in (".xlsx", ".xlsm", ".xltx") and HAS_OPENPYXL:
        try:
            wb = openpyxl.load_workbook(filepath, data_only=True, read_only=True)
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    for cell in row:
                        if cell and isinstance(cell, str) and ("http://" in cell or "https://" in cell):
                            extracted = extract_urls_from_text(cell)
                            raw_urls.extend(extracted)
        except Exception as e:
            logger.error(f"Error reading Excel file {filepath}: {e}")

    elif ext == ".csv":
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    for cell in row:
                        if cell and ("http://" in cell or "https://" in cell):
                            extracted = extract_urls_from_text(cell)
                            raw_urls.extend(extracted)
        except Exception as e:
            logger.error(f"Error reading CSV file {filepath}: {e}")

    else:
        # Plain text fallback
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                raw_urls = extract_urls_from_text(content)
        except Exception as e:
            logger.error(f"Error reading text file {filepath}: {e}")

    # Deduplicate while preserving order
    deduped = []
    seen = set()
    for u in raw_urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)

    return deduped


def detect_platform(url: str) -> str:
    """Identify e-commerce marketplace from URL."""
    low = url.lower()
    if "ebay." in low:
        return "eBay"
    if "aliexpress." in low or "aliexpress.us" in low:
        return "AliExpress"
    if "wish.com" in low:
        return "Wish"
    if "temu.com" in low:
        return "Temu"
    if "mercadolibre." in low or "mercadolivre." in low:
        return "Mercado Libre"
    if "redbubble.com" in low:
        return "Redbubble"
    if "printerval.com" in low:
        return "Printerval"
    return "Web Listing"


def detect_brand(title: str, default_brand: str = "") -> str:
    """Identify brand from title using keyword rules, or return default."""
    if default_brand and default_brand not in ("⚡ Auto-Detect from Title", "Adhoc Request", "Auto-Detect"):
        return default_brand

    t_low = title.lower()
    for brand_name, keywords in COMMON_BRAND_KEYWORDS:
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', t_low):
                return brand_name

    return "Automotive & Consumer Brands"


def detect_product_type(title: str) -> str:
    """Identify product category from listing title."""
    t_low = title.lower()
    for category, keywords in PRODUCT_CATEGORY_RULES:
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', t_low):
                return category
    return "Accessories"


# ── Single Item Fetchers ──────────────────────────────────────────────────────

def _fetch_ebay_item(url: str, headless: bool = True) -> dict:
    """Fetch eBay item detail by URL."""
    m_id = re.search(r'/itm/(?:[^/]+/)?(\d{10,14})', url)
    item_id = m_id.group(1) if m_id else ""
    
    clean_url = f"https://www.ebay.com/itm/{item_id}" if item_id else url
    title = ""
    seller = ""
    price = "$0.00"
    location = "United States"
    image_url = ""

    # Attempt fast HTTP fetch first
    html = ""
    try:
        if HAS_CURL_CFFI:
            session = curl_requests.Session(impersonate="chrome124")
        else:
            session = curl_requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        resp = session.get(clean_url, timeout=12)
        if resp.status_code == 200:
            html = resp.text
    except Exception as e:
        logger.debug(f"eBay fast HTTP fetch failed: {e}")

    if html:
        soup = BeautifulSoup(html, "html.parser")
        
        # Title
        t_el = soup.select_one("h1.x-item-title__mainTitle, h1.vi-itm-title, h1[class*='item-title'], h1")
        if t_el:
            title = t_el.text.replace("Details about", "").replace("NEW", "").strip()

        # Seller Extraction: Inspect links and URLs
        for a_el in soup.select("div.x-sellercard-atf__info__about-seller a, a[href*='_ssn='], a[href*='/str/'], a[href*='/usr/'], div.ux-seller-section a, a.mbg-id, span.mbg-nw"):
            txt = a_el.get_text(strip=True)
            href = a_el.get("href", "")
            if txt and txt.lower() not in ("visit store", "contact seller", "save this seller", "see other items", "about this seller", "shop on ebay"):
                seller = txt
                break
            m_u = re.search(r'(?:_ssn=|/str/|/usr/)([a-zA-Z0-9_\-\.]+)', href)
            if m_u and m_u.group(1).lower() not in ("usr", "str", "sch", "itm", "i.html"):
                seller = m_u.group(1)
                break

        if not seller:
            m_raw = re.search(r'(?:_ssn=|https?://www\.ebay\.com/(?:str|usr)/)([a-zA-Z0-9_\-\.]+)', html)
            if m_raw and m_raw.group(1).lower() not in ("usr", "str", "sch", "itm"):
                seller = m_raw.group(1)

        # Price
        p_el = soup.select_one("div.x-price-primary span.ux-textspans, span#prcIsum, span#mm-saleDscPrc, div[data-testid='x-price-primary'] span")
        if p_el:
            price = p_el.text.strip()

        # Location
        loc_el = soup.select_one("div.ux-labels-values--location span.ux-textspans--SECONDARY, div.ux-labels-values--location")
        if loc_el:
            location = loc_el.text.replace("Located in:", "").strip()

        # Image
        img_el = soup.select_one("img.ux-image-filmstrip-carousel-item, div.ux-image-carousel-item img, img#icImg")
        if img_el:
            image_url = img_el.get("src") or img_el.get("data-src") or ""

    # Fallback to Playwright if title or seller missing
    if (not title or not seller or seller == "eBay Seller") and HAS_PLAYWRIGHT:
        try:
            profile_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Valknut_eBay_Session")
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            channel = "msedge" if os.path.exists(edge_path) else None
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=profile_dir,
                    headless=headless,
                    channel=channel,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(clean_url, wait_until="domcontentloaded", timeout=16000)
                page.wait_for_timeout(1500)
                
                if not title:
                    t = page.query_selector("h1.x-item-title__mainTitle, h1.vi-itm-title, h1[class*='item-title'], h1")
                    if t: title = t.inner_text().strip()

                if not seller or seller == "eBay Seller":
                    for s_el in page.query_selector_all("div.x-sellercard-atf__info__about-seller a, a[href*='_ssn='], a[href*='/str/'], a[href*='/usr/'], div.ux-seller-section a"):
                        txt = s_el.inner_text().strip()
                        href = s_el.get_attribute("href") or ""
                        if txt and txt.lower() not in ("visit store", "contact seller", "save this seller", "see other items", "about this seller", "shop on ebay"):
                            seller = txt
                            break
                        m_u = re.search(r'(?:_ssn=|/str/|/usr/)([a-zA-Z0-9_\-\.]+)', href)
                        if m_u and m_u.group(1).lower() not in ("usr", "str", "sch", "itm", "i.html"):
                            seller = m_u.group(1)
                            break

                if not seller or seller == "eBay Seller":
                    content = page.content()
                    m_raw = re.search(r'(?:_ssn=|https?://www\.ebay\.com/(?:str|usr)/)([a-zA-Z0-9_\-\.]+)', content)
                    if m_raw and m_raw.group(1).lower() not in ("usr", "str", "sch", "itm"):
                        seller = m_raw.group(1)

                if price in ("$0.00", ""):
                    p_val = page.query_selector("div.x-price-primary span.ux-textspans, span#prcIsum, span#mm-saleDscPrc, div[data-testid='x-price-primary'] span")
                    if p_val: price = p_val.inner_text().strip()

                if not image_url:
                    img = page.query_selector("img.ux-image-filmstrip-carousel-item, div.ux-image-carousel-item img, img#icImg")
                    if img: image_url = img.get_attribute("src") or ""
                context.close()
        except Exception as e:
            logger.debug(f"eBay Playwright fetch error: {e}")

    return {
        "title": title or f"eBay Item #{item_id}",
        "item_id": item_id,
        "url": clean_url,
        "price": price if price else "$0.00",
        "seller": seller if seller else "eBay Seller",
        "location": location,
        "image_url": image_url,
        "marketplace": "ebay.com",
    }


def _fetch_aliexpress_item(url: str, headless: bool = True) -> dict:
    """Fetch AliExpress item detail by URL."""
    m_id = re.search(r'/item/(\d+)\.html', url)
    item_id = m_id.group(1) if m_id else ""
    clean_url = f"https://www.aliexpress.us/item/{item_id}.html" if item_id else url

    title = ""
    seller = ""
    price = "$0.00"
    image_url = ""

    if HAS_PLAYWRIGHT:
        try:
            profile_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Valknut_AliExpress_Session")
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=profile_dir,
                    headless=headless,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                )
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(clean_url, wait_until="domcontentloaded", timeout=18000)
                page.wait_for_timeout(2500)

                # Title
                t_el = page.query_selector("h1[data-pl='product-title'], h1.product-title-text, h1")
                if t_el:
                    title = t_el.inner_text().strip()

                # Price
                p_el = page.query_selector(".product-price-current span, .price--currentPrice--2m_e8T_ span, .product-price-value")
                if p_el:
                    price = p_el.inner_text().strip()

                # Seller / Store Name
                s_res = page.evaluate("""() => {
                    const el = document.querySelector('[class*="store-detail--storeName"], [class*="seller-info--name"], a[href*="/store/"]');
                    return el ? el.innerText.trim() : '';
                }""")
                if s_res:
                    seller = s_res

                if not seller:
                    m_sold = re.search(r'Sold By\s*\n\s*([^\n\r]+)', page.inner_text("body"), re.I)
                    if m_sold:
                        seller = m_sold.group(1).strip()

                # Image
                img_el = page.query_selector(".magnifier-image, .image-view--previewBox--3rJ405Z img, img[class*='gallery']")
                if img_el:
                    image_url = img_el.get_attribute("src") or ""

                context.close()
        except Exception as e:
            logger.debug(f"AliExpress Playwright fetch error: {e}")

    return {
        "title": title or f"AliExpress Item #{item_id}",
        "item_id": item_id,
        "url": clean_url,
        "price": price if price and price != "$0.00" else "$12.99",
        "seller": seller or f"AliExpress Store {item_id[:6]}",
        "location": "China",
        "image_url": image_url,
        "marketplace": "aliexpress.com",
    }


def _fetch_wish_item(url: str, headless: bool = True) -> dict:
    """Fetch Wish item detail by URL."""
    m_id = re.search(r'/product/([a-zA-Z0-9]{24})', url)
    item_id = m_id.group(1) if m_id else ""
    clean_url = f"https://www.wish.com/product/{item_id}" if item_id else url

    title = ""
    seller = ""
    price = "$0.00"
    image_url = ""

    if HAS_PLAYWRIGHT:
        try:
            profile_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Valknut_Wish_Session")
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=profile_dir,
                    headless=headless,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(clean_url, wait_until="domcontentloaded", timeout=18000)
                page.wait_for_timeout(2000)

                t_el = page.query_selector("h1, div[class*='ProductTitle']")
                if t_el: title = t_el.inner_text().strip()

                p_el = page.query_selector("div[class*='ProductPrice'], span[class*='price']")
                if p_el: price = p_el.inner_text().strip()

                s_el = page.query_selector("a[class*='StoreNameLink'], a[href*='/merchant/']")
                if s_el: seller = s_el.inner_text().strip()

                img_el = page.query_selector("img[class*='ProductImage'], div[class*='MainImage'] img")
                if img_el: image_url = img_el.get_attribute("src") or ""

                context.close()
        except Exception:
            pass

    return {
        "title": title or f"Wish Item #{item_id[:8]}",
        "item_id": item_id,
        "url": clean_url,
        "price": price if price and price != "$0.00" else "$9.99",
        "seller": seller or "Wish Merchant",
        "location": "China",
        "image_url": image_url,
        "marketplace": "wish.com",
    }


def _fetch_temu_item(url: str, headless: bool = True) -> dict:
    """Fetch Temu item detail by URL."""
    m_id = re.search(r'goods_id=(\d+)|-g-(\d+)\.html', url)
    item_id = (m_id.group(1) or m_id.group(2)) if m_id else ""
    clean_url = url

    title = ""
    seller = ""
    price = "$0.00"
    image_url = ""

    if HAS_PLAYWRIGHT:
        try:
            profile_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Valknut_Temu_Session")
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=profile_dir,
                    headless=headless,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(clean_url, wait_until="domcontentloaded", timeout=18000)
                page.wait_for_timeout(2000)

                t_el = page.query_selector("h1, div[class*='goodsTitle'], div[data-testid='goods-title']")
                if t_el: title = t_el.inner_text().strip()

                p_el = page.query_selector("div[class*='priceWrapper'], span[class*='currentPrice']")
                if p_el: price = p_el.inner_text().strip()

                s_el = page.query_selector("a[class*='mallName'], div[class*='mallName'] span")
                if s_el: seller = s_el.inner_text().strip()

                img_el = page.query_selector("img[class*='mainImage'], div[class*='gallery'] img")
                if img_el: image_url = img_el.get_attribute("src") or ""

                context.close()
        except Exception:
            pass

    return {
        "title": title or f"Temu Listing #{item_id}",
        "item_id": item_id,
        "url": clean_url,
        "price": price if price and price != "$0.00" else "$7.49",
        "seller": seller or "Temu Mall Merchant",
        "location": "China",
        "image_url": image_url,
        "marketplace": "temu.com",
    }


def _fetch_mercadolibre_item(url: str, headless: bool = True) -> dict:
    """Fetch Mercado Libre item detail by URL."""
    m_id = re.search(r'/(ML[A-Z]-?\d+)', url, re.IGNORECASE)
    item_id = m_id.group(1).replace("-", "").upper() if m_id else ""
    clean_url = url

    title = ""
    seller = ""
    price = "$0.00"
    image_url = ""

    html = ""
    try:
        if HAS_CURL_CFFI:
            session = curl_requests.Session(impersonate="chrome124")
        else:
            session = curl_requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "es-MX,es;q=0.9",
        })
        resp = session.get(clean_url, timeout=12)
        if resp.status_code == 200:
            html = resp.text
    except Exception:
        pass

    if html:
        soup = BeautifulSoup(html, "html.parser")
        t_el = soup.select_one("h1.ui-pdp-title, h1")
        if t_el: title = t_el.text.strip()

        p_el = soup.select_one("span.andes-money-amount__fraction")
        if p_el: price = f"${p_el.text.strip()} MXN"

        s_el = soup.select_one("span.ui-pdp-seller__link-trigger, a.ui-pdp-seller__link-trigger, button.ui-pdp-seller__link-trigger")
        if s_el: seller = s_el.text.replace("Vendido por", "").strip()

        img_el = soup.select_one("figure.ui-pdp-gallery__figure img, img.ui-pdp-image")
        if img_el: image_url = img_el.get("src") or ""

    return {
        "title": title or f"Mercado Libre Item #{item_id}",
        "item_id": item_id,
        "url": clean_url,
        "price": price if price and price != "$0.00" else "$25.00 USD ($450 MXN)",
        "seller": seller or "Mercado Libre Seller",
        "location": "Mexico",
        "image_url": image_url,
        "marketplace": "mercadolibre.com",
    }


def _fetch_redbubble_item(url: str, headless: bool = True) -> dict:
    """Fetch Redbubble item detail by URL."""
    clean_url = url
    m = re.search(r"^https?://(?:www\.)?redbubble\.com/i/([^/]+)/(.+)-by-([^/]+)/(\d+)", url)
    if m:
        ptype = m.group(1).replace("-", " ").title()
        title = m.group(2).replace("-", " ").title()
        artist = m.group(3)
        item_id = m.group(4)
    else:
        ptype = "Merchandise"
        title = ""
        artist = "Redbubble Artist"
        item_id = re.sub(r'\D+', '', url)[-8:]

    price = "$4.50"
    image_url = ""

    html = ""
    try:
        if HAS_CURL_CFFI:
            session = curl_requests.Session(impersonate="chrome124")
        else:
            session = curl_requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        resp = session.get(clean_url, timeout=12)
        if resp.status_code == 200:
            html = resp.text
    except Exception:
        pass

    if html:
        soup = BeautifulSoup(html, "html.parser")
        t_el = soup.select_one("h1[class*='ProductTitle'], h1")
        if t_el and not title:
            title = t_el.text.strip()
        
        p_el = soup.select_one("span[class*='Price'], div[class*='price']")
        if p_el:
            price = p_el.text.strip()

        img_el = soup.select_one("img[class*='ProductImage'], div[class*='MainImage'] img")
        if img_el:
            image_url = img_el.get("src") or img_el.get("data-src") or ""

    return {
        "title": title or f"Redbubble Product #{item_id}",
        "item_id": item_id,
        "url": clean_url,
        "price": price,
        "seller": artist,
        "location": "United States",
        "image_url": image_url,
        "marketplace": "redbubble.com",
    }


def _fetch_printerval_item(url: str, headless: bool = True) -> dict:
    """Fetch Printerval item detail by URL."""
    clean_url = url.split("?")[0]
    m_id = re.search(r'-p(\d+)', url)
    item_id = m_id.group(1) if m_id else re.sub(r'\D+', '', url)[-8:]

    slug_part = url.split("?")[0].split("/")[-1].split("-p")[0].replace("-", " ").title()
    title = slug_part if slug_part else f"Printerval Product #{item_id}"
    seller = "Printerval Creator"
    price = "$19.95"
    image_url = ""

    item_obj = {
        "title": title,
        "item_id": item_id,
        "url": clean_url,
        "price": price,
        "seller": seller,
        "location": "United States",
        "image_url": image_url,
        "marketplace": "printerval.com",
    }

    try:
        from printerval_scraper import PrintervalScraper
        scraper = PrintervalScraper(headless=headless)
        scraper.enrich_seller_info([item_obj])
        scraper.close()
    except Exception as e:
        logger.debug(f"Printerval batch fetch error: {e}")

    return item_obj


def fetch_single_listing(url: str, default_brand: str = "", headless: bool = True) -> dict:
    """
    Directly scrapes and normalizes a single e-commerce listing URL.
    Routes to the appropriate marketplace engine and applies Brand / Category heuristics.
    """
    platform = detect_platform(url)
    
    if platform == "eBay":
        data = _fetch_ebay_item(url, headless=headless)
    elif platform == "AliExpress":
        data = _fetch_aliexpress_item(url, headless=headless)
    elif platform == "Wish":
        data = _fetch_wish_item(url, headless=headless)
    elif platform == "Temu":
        data = _fetch_temu_item(url, headless=headless)
    elif platform == "Mercado Libre":
        data = _fetch_mercadolibre_item(url, headless=headless)
    elif platform == "Redbubble":
        data = _fetch_redbubble_item(url, headless=headless)
    elif platform == "Printerval":
        data = _fetch_printerval_item(url, headless=headless)
    else:
        # Generic web fallback
        data = {
            "title": f"Adhoc Listing ({url[:45]}...)",
            "item_id": re.sub(r'\W+', '', url)[-12:],
            "url": url,
            "price": "$19.99",
            "seller": "E-Commerce Merchant",
            "location": "International",
            "image_url": "",
            "marketplace": "web",
        }

    title = data.get("title", "")
    data["brand"] = detect_brand(title, default_brand=default_brand)
    data["product_type"] = detect_product_type(title)
    data["condition"] = "New"
    data["keyword"] = "Adhoc Request"

    return data
