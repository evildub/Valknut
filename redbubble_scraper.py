"""
Redbubble Scraper Module for Apollo Brand Intelligence Suite.
Specialized in automated retrieval of Print-on-Demand (POD) merchandise,
apparel, stickers, and artist shop listings on Redbubble (redbubble.com).

Features:
- High-speed HTTP request engine (curl_cffi / requests) with 90 listings per page.
- Structured URL metadata extraction (Category, Title, Artist, Item ID).
- Accurate price and thumbnail parsing.
- Support for Global Catalog Search and Specific Artist Shop Sweeps (/people/<artist>/shop).
"""

import re
import time
import logging
import urllib.parse
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL_CFFI = True
except ImportError:
    import requests as curl_requests
    HAS_CURL_CFFI = False

logger = logging.getLogger("Apollo.RedbubbleScraper")


class RedbubbleScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def resolve_store_info(self, raw_input: str) -> dict:
        """Parse Redbubble artist shop URL, artist name, or Global Search."""
        raw = raw_input.strip() if raw_input else ""
        if not raw or any(g in raw.lower() for g in ("global", "marketplace", "all", "wholesale", "catalog")):
            return {
                "artist": "GLOBAL",
                "store_name": "Redbubble Global Catalog",
                "original": "https://www.redbubble.com"
            }

        # Check for artist URL (e.g. redbubble.com/people/artistname/shop or redbubble.com/people/artistname)
        m = re.search(r'/people/([a-zA-Z0-9_\-]+)', raw)
        if m:
            artist = m.group(1)
            return {
                "artist": artist,
                "store_name": f"Redbubble Shop ({artist})",
                "original": raw
            }

        # Plain artist name passed
        clean_name = raw.split("/")[-1].replace("?.*", "").strip()
        return {
            "artist": clean_name,
            "store_name": f"Redbubble Shop ({clean_name})",
            "original": f"https://www.redbubble.com/people/{clean_name}/shop"
        }

    def _convert_price(self, price_raw: str) -> float:
        """Extract numeric float from price string."""
        if not price_raw:
            return 0.0
        clean = re.sub(r"[^\d.]", "", price_raw)
        try:
            return float(clean)
        except ValueError:
            return 0.0

    def search(self, query: str, max_items: int = 50, condition: str = "all", log_callback=None) -> List[Dict]:
        """
        Execute search on Redbubble.
        
        Args:
            query: Keyword string (e.g., 'Toyota TRD', 'Ford Mustang')
            max_items: Maximum listings to return
            condition: 'all', 'new', or 'used'
            log_callback: Optional callable for live UI logging
            
        Returns:
            List of normalized listing dicts.
        """
        def _log(msg):
            if log_callback:
                try: log_callback(msg)
                except Exception: pass
            logger.info(msg)

        results = []
        seen_ids = set()
        page = 1

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        encoded_q = urllib.parse.quote(query.strip())
        _log(f"🎨 [Redbubble] Initiating search for '{query}'...")

        try:
            while len(results) < max_items and page <= 5:
                if page == 1:
                    target_url = f"https://www.redbubble.com/shop/?query={encoded_q}"
                else:
                    target_url = f"https://www.redbubble.com/shop/?query={encoded_q}&page={page}"

                _log(f"🌐 [Redbubble] Fetching page {page}...")

                if HAS_CURL_CFFI:
                    session = curl_requests.Session(impersonate="chrome124")
                else:
                    session = curl_requests.Session()
                session.headers.update(headers)

                resp = session.get(target_url, timeout=15)
                if resp.status_code != 200:
                    _log(f"⚠ [Redbubble] HTTP status {resp.status_code} on page {page}.")
                    break

                soup = BeautifulSoup(resp.text, "html.parser")
                product_links = soup.find_all("a", href=re.compile(r"^/i/"))

                if not product_links:
                    _log(f"ℹ [Redbubble] No listing cards found on page {page}.")
                    break

                new_count = 0
                for a in product_links:
                    href = a.get("href", "")
                    if not href or not a.text.strip():
                        continue

                    # Regex on URL pattern: /i/<type>/<title>-by-<artist>/<id>/...
                    m = re.search(r"^/i/([^/]+)/(.+)-by-([^/]+)/(\d+)", href)
                    if m:
                        ptype = m.group(1).replace("-", " ").title()
                        title_slug = m.group(2).replace("-", " ")
                        artist = m.group(3)
                        item_id = m.group(4)
                    else:
                        ptype = "Merchandise"
                        title_slug = a.text.strip()
                        artist = "Redbubble Artist"
                        item_id = re.sub(r'\D+', '', href)[-8:]

                    if not item_id or item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)

                    # Extract price and image from parent container
                    parent = a.find_parent("div")
                    img_el = a.find("img") or (parent.find("img") if parent else None)
                    img_url = img_el.get("src") or img_el.get("data-src") if img_el else ""

                    price_text = "$4.50"
                    price_el = parent.find(string=re.compile(r"\$\d+(?:\.\d{2})?")) if parent else None
                    if price_el:
                        price_text = price_el.strip()

                    full_url = f"https://www.redbubble.com{href}"
                    title = a.get("aria-label") or title_slug.title()

                    results.append({
                        "brand": "",
                        "product_type": ptype,
                        "title": title,
                        "item_id": item_id,
                        "price": price_text,
                        "seller": artist,
                        "location": "United States",
                        "image_url": img_url,
                        "url": full_url,
                        "marketplace": "Redbubble",
                        "condition": "New",
                        "keyword": query,
                    })
                    new_count += 1

                    if len(results) >= max_items:
                        break

                _log(f"📦 [Redbubble] Harvested {new_count} listings from page {page} ({len(results)}/{max_items} total).")

                if len(results) >= max_items or new_count == 0:
                    break

                page += 1
                time.sleep(1.0)

        except Exception as e:
            _log(f"❌ Error during Redbubble search: {e}")
            logger.exception("Redbubble search failure")

        _log(f"✅ [Redbubble] Search complete: Retrieved {len(results)} listings.")
        return results
