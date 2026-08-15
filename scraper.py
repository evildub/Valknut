import re
import os
import time
import random
import tempfile
import threading
from urllib.parse import urlencode, urlparse, parse_qs
from bs4 import BeautifulSoup

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    import requests as curl_requests
    HAS_CURL_CFFI = False


MAX_PAGES = 15
PAGE_SIZE = 60        # eBay standard items per page


class EbayScraper:
    def __init__(self, headless=False):
        """
        Scraper for eBay store and seller listings with anti-bot bypass.
        """
        self.headless = headless
        self.profile_dir = os.path.join(tempfile.gettempdir(), "ebay_harvester_edge_profile")

    def search(self, store_url: str, include_term: str,
               exclude_terms: list[str] = None,
               condition: str = "all",
               stop_event: threading.Event = None,
               pause_event: threading.Event = None) -> list[dict]:
        """
        Search an eBay store/seller for include_term, applying exclude_terms.
        Supports stop_event and pause_event for real-time user control.
        """
        store_info = self.resolve_store_info(store_url)
        exclude_terms = exclude_terms or []
        cleaned_excludes = self._sanitize_exclusions(include_term, exclude_terms)

        items = []
        seen_ids = set()

        if HAS_PLAYWRIGHT:
            try:
                items = self._search_via_playwright(
                    store_info, include_term, cleaned_excludes, condition, seen_ids,
                    stop_event=stop_event, pause_event=pause_event
                )
                if items or (stop_event and stop_event.is_set()):
                    return items
            except Exception:
                pass

        # Fallback to requests search
        page = 1
        seller_label = store_info.get("store_name") or store_info.get("seller") or ""
        while page <= MAX_PAGES:
            if stop_event and stop_event.is_set():
                break
            if pause_event:
                pause_event.wait()

            url = self._build_url(store_info, include_term, cleaned_excludes, page, condition)
            html = self._fetch_via_requests(url)
            if not html:
                break
            page_items = self._parse_html(html, fallback_seller=seller_label)
            if not page_items:
                break

            new_found = 0
            for item in page_items:
                item_id = item.get("item_id")
                dedup_key = item_id if item_id else item.get("url")
                if dedup_key and dedup_key not in seen_ids:
                    seen_ids.add(dedup_key)
                    items.append(item)
                    new_found += 1

            if new_found == 0 or len(page_items) < 10:
                break
            page += 1
            time.sleep(random.uniform(1.0, 2.0))

        return items

    def _search_via_playwright(self, store_info: dict,
                               include_term: str, excludes: list[str],
                               condition: str, seen_ids: set,
                               stop_event: threading.Event = None,
                               pause_event: threading.Event = None) -> list[dict]:
        """Search across pages using a single browser session with stop/pause support."""
        items = []
        seller_label = store_info.get("store_name") or store_info.get("seller") or ""

        with sync_playwright() as p:
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--no-first-run",
                "--no-default-browser-check"
            ]
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
            try:
                context = p.chromium.launch_persistent_context(
                    self.profile_dir,
                    channel="msedge",
                    headless=self.headless,
                    user_agent=ua,
                    viewport={"width": 1440, "height": 900},
                    args=launch_args
                )
            except Exception:
                context = p.chromium.launch_persistent_context(
                    self.profile_dir,
                    headless=self.headless,
                    user_agent=ua,
                    viewport={"width": 1440, "height": 900},
                    args=launch_args
                )

            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.navigator.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)

            page = context.pages[0] if context.pages else context.new_page()
            page_num = 1

            while page_num <= MAX_PAGES:
                if stop_event and stop_event.is_set():
                    break
                if pause_event:
                    pause_event.wait()

                url = self._build_url(store_info, include_term, excludes, page_num, condition)
                try:
                    page.goto(url, wait_until="load", timeout=25000)
                    time.sleep(1.5)
                    html = page.content()
                except Exception:
                    break

                page_items = self._parse_html(html, fallback_seller=seller_label)
                if not page_items:
                    break

                new_found = 0
                for item in page_items:
                    item_id = item.get("item_id")
                    dedup_key = item_id if item_id else item.get("url")
                    if dedup_key and dedup_key not in seen_ids:
                        seen_ids.add(dedup_key)
                        items.append(item)
                        new_found += 1

                if new_found == 0 or len(page_items) < 10:
                    break

                page_num += 1
                time.sleep(random.uniform(1.0, 2.0))

            context.close()
        return items

    # ── Store / Seller Info Resolver ──────────────────────────────────────────
    def resolve_store_info(self, url: str) -> dict:
        """
        Extract store_name, seller username, and store flag.
        Returns dict: {'store_name': str, 'seller': str, 'is_store': bool}
        """
        info = {
            "store_name": "",
            "seller": "",
            "is_store": False
        }
        if not url:
            return info
            
        url_str = url.strip().rstrip("/")

        # Check for query parameters first (e.g. pasted eBay search URL)
        if "?" in url_str:
            parsed = urlparse(url_str)
            qs = parse_qs(parsed.query)
            if "store_name" in qs:
                info["store_name"] = qs["store_name"][0].strip()
                info["is_store"] = True
            if "_ssn" in qs:
                info["seller"] = qs["_ssn"][0].strip()
            if info["store_name"] or info["seller"]:
                return info

        # Check for store URL pattern /str/
        if "/str/" in url_str.lower():
            part = url_str.lower().split("/str/")[-1]
            store_name = part.split("/")[0].split("?")[0].strip()
            info["store_name"] = store_name
            info["is_store"] = True
            return info

        # Check for user / seller URL pattern /usr/ or /seller/
        for pattern in ["/usr/", "/seller/"]:
            if pattern in url_str.lower():
                part = url_str.lower().split(pattern)[-1]
                user_name = part.split("/")[0].split("?")[0].strip()
                info["seller"] = user_name
                info["is_store"] = False
                return info

        # Check /sch/username/m.html pattern
        m = re.search(r"/sch/([^/?&#]+)/m\.html", url_str, re.IGNORECASE)
        if m:
            info["seller"] = m.group(1).strip()
            info["is_store"] = False
            return info

        # Plain text input
        if not url_str.startswith("http://") and not url_str.startswith("https://"):
            clean_name = url_str.split("/")[0].split("?")[0].strip()
            info["store_name"] = clean_name
            info["is_store"] = True
            return info

        last_seg = url_str.split("/")[-1].split("?")[0].strip()
        info["store_name"] = last_seg
        info["is_store"] = True
        return info

    def resolve_seller(self, url: str) -> str:
        """Backwards compatibility for main.py."""
        info = self.resolve_store_info(url)
        return info.get("store_name") or info.get("seller") or url

    # ── Exclusion Sanitizer ───────────────────────────────────────────────────
    def _sanitize_exclusions(self, include_term: str, exclude_terms: list[str]) -> list[str]:
        """
        Ensure no exclusion term contradicts or cancels out the search term.
        """
        inc_lower = include_term.lower()
        inc_tokens = set(re.findall(r"\w+", inc_lower))

        safe_excludes = []
        for ex in exclude_terms:
            ex_clean = ex.strip().strip('"')
            if not ex_clean:
                continue
            ex_lower = ex_clean.lower()
            ex_tokens = set(re.findall(r"\w+", ex_lower))
            if ex_lower == inc_lower or (ex_tokens and ex_tokens.issubset(inc_tokens)):
                continue
            safe_excludes.append(ex_clean)

        return safe_excludes

    # ── URL Builder ───────────────────────────────────────────────────────────
    def _build_url(self, store_info: dict, include: str, excludes: list[str],
                   page: int, condition: str = "all") -> str:
        """
        Build eBay search URL matching native store or seller search.
        Handles multi-word exclusions properly by wrapping them in quotes (e.g. -"General Motors").
        """
        nkw_parts = [include.strip()]
        for ex in excludes:
            ex_str = ex.strip().strip('"')
            if ex_str:
                if " " in ex_str:
                    nkw_parts.append(f'-"{ex_str}"')
                else:
                    nkw_parts.append(f"-{ex_str}")
        nkw = " ".join(nkw_parts)

        store_name = store_info.get("store_name", "")
        seller = store_info.get("seller", "")
        is_store = store_info.get("is_store", False)

        # 1. Store Search: use eBay's in-store search endpoint
        if is_store and store_name:
            params = {
                "_nkw": nkw,
                "_pgn": page,
                "_ipg": PAGE_SIZE,
            }
            if condition == "new":
                params["LH_ItemCondition"] = "1000"
            elif condition == "used":
                params["LH_ItemCondition"] = "3000"
            
            if seller and seller != store_name:
                params["_ssn"] = seller
                params["store_name"] = store_name

            return f"https://www.ebay.com/str/{store_name}?" + urlencode(params)

        # 2. Seller search on /sch/i.html
        target = seller if seller else store_name
        params = {
            "_dkr": "1",
            "iconV2Request": "true",
            "_blrs": "recall_filtering",
            "_oac": "1",
            "_nkw": nkw,
            "_ipg": PAGE_SIZE,
            "_pgn": page,
            "_sacat": "0",
        }

        if target:
            params["_ssn"] = target

        if condition == "new":
            params["LH_ItemCondition"] = "1000"
        elif condition == "used":
            params["LH_ItemCondition"] = "3000"

        return "https://www.ebay.com/sch/i.html?" + urlencode(params)

    def _fetch_via_requests(self, url: str) -> str:
        """Fallback fetch using session."""
        try:
            if HAS_CURL_CFFI:
                session = curl_requests.Session(impersonate="chrome124")
            else:
                session = curl_requests.Session()
            session.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            })
            resp = session.get(url, timeout=15)
            return resp.text if resp.status_code == 200 else ""
        except Exception:
            return ""

    def _parse_html(self, html: str, fallback_seller: str = "") -> list[dict]:
        """
        Parse listing items from modern .s-card, classic .s-item, and store layouts.
        Extracts robust high-resolution thumbnail URLs.
        """
        soup = BeautifulSoup(html, "html.parser")
        items = []

        containers = soup.select(
            "li.s-card, li.s-item, div.s-item__wrapper, li.srp-results__item, .str-item-card, div.str-item-card__wrapper"
        )

        for card in containers:
            if card.select_one(".s-item__placeholder") or card.select_one(".srp-river-answer"):
                continue

            # 1. URL & Item ID
            link_el = (
                card.select_one('a[href*="/itm/"]') or
                card.select_one("a.s-item__link, a.s-card__link, a.str-item-card__link")
            )
            if not link_el or not link_el.get("href"):
                continue

            raw_url = link_el["href"]
            item_url = raw_url.split("?")[0]
            item_id = self._extract_item_id(raw_url)

            # 2. Title
            title_el = (
                card.select_one(".s-card__title") or
                card.select_one(".s-item__title") or
                card.select_one(".str-item-card__title") or
                card.select_one('[role="heading"]') or
                card.select_one("h3")
            )
            title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)

            if not title or title.lower() == "shop on ebay":
                continue
            if "Opens in a new window or tab" in title:
                title = title.replace("Opens in a new window or tab", "").strip()
            if title.startswith("New Listing"):
                title = title.replace("New Listing", "", 1).strip()

            # 3. Price
            price_el = (
                card.select_one(".s-card__price") or
                card.select_one(".s-item__price") or
                card.select_one(".str-item-card__price") or
                card.select_one(".text-display-2")
            )
            price = price_el.get_text(strip=True) if price_el else ""

            # 4. Thumbnail Image URL Extraction
            img_url = ""
            img_el = (
                card.select_one('img[src*="ebayimg.com"]') or
                card.select_one('img[data-src*="ebayimg.com"]') or
                card.select_one("img.s-card__image") or
                card.select_one("img.s-item__image-img") or
                card.select_one(".str-item-card__image img") or
                card.select_one("img")
            )
            if img_el:
                candidates = [
                    img_el.get("data-src"),
                    img_el.get("data-lazy"),
                    img_el.get("src"),
                ]
                srcset = img_el.get("srcset", "")
                if srcset:
                    candidates.insert(0, srcset.split()[0].strip())
                for cand in candidates:
                    if cand and "ebayimg.com" in cand and not cand.endswith(".gif") and not cand.startswith("data:"):
                        img_url = cand
                        break
                if not img_url:
                    for cand in candidates:
                        if cand and not cand.startswith("data:") and not cand.endswith(".gif"):
                            img_url = cand
                            break

            # 5. Seller
            seller_el = (
                card.select_one(".s-item__seller-info-text") or
                card.select_one(".s-item__seller-info") or
                card.select_one(".s-card__seller-info") or
                card.select_one(".str-seller-info") or
                card.select_one(".s-card__subtitle")
            )
            seller = seller_el.get_text(strip=True) if seller_el else fallback_seller
            if seller and "(" in seller:
                seller = seller.split("(")[0].strip()

            # 6. Item Location / Origin
            loc_el = (
                card.select_one(".s-item__location") or
                card.select_one(".s-card__location") or
                card.select_one(".s-item__location--text") or
                card.select_one(".s-item__itemLocation") or
                card.select_one(".str-item-card__location") or
                card.select_one("span[class*='location']") or
                card.select_one(".s-item__detail--secondary")
            )
            item_location = loc_el.get_text(strip=True) if loc_el else ""
            if not item_location:
                for span in card.select("span, div.s-item__detail, div.s-card__detail"):
                    txt = span.get_text(strip=True)
                    if (txt.lower().startswith("from ") or "located in" in txt.lower()) and len(txt) < 50:
                        item_location = txt
                        break

            if item_location.lower().startswith("from "):
                item_location = item_location[5:].strip()
            elif "located in" in item_location.lower():
                item_location = item_location.split(":")[-1].strip()

            items.append({
                "title":     title,
                "url":       item_url,
                "item_id":   item_id,
                "price":     price,
                "image_url": img_url,
                "seller":    seller if seller else fallback_seller,
                "location":  item_location,
            })

        return items

    def _extract_item_id(self, url: str) -> str:
        """Extract eBay 12-digit item ID from URL."""
        m = re.search(r"/itm/(?:[^/]+/)?(\d+)", url)
        if m:
            return m.group(1)
        m = re.search(r"[?&]item=(\d+)", url)
        if m:
            return m.group(1)
        return ""
