import re
import os
import time
import random
import tempfile
import threading
from urllib.parse import urlencode, quote_plus, urlparse
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


MAX_PAGES = 10


class AliExpressScraper:
    def __init__(self, headless=False):
        """
        Specialized Stealth Scraper for AliExpress stores and global wholesale search with
        anti-bot bypass, persistent session profiles, and client-side exclusion filtering.
        """
        self.headless = headless
        self.profile_dir = os.path.join(tempfile.gettempdir(), "aliexpress_harvester_profile")

    def resolve_store_info(self, raw_input: str) -> dict:
        """Parse AliExpress store URL, Store ID, seller name, or Global Search."""
        raw = raw_input.strip() if raw_input else ""
        
        # Check if user wants global marketplace search
        if not raw or any(g in raw.lower() for g in ("global", "marketplace", "all", "wholesale")):
            return {
                "store_id": "GLOBAL",
                "store_name": "AliExpress Global Search",
                "original": "https://www.aliexpress.com"
            }

        # Check for Store ID in URL (e.g., aliexpress.com/store/1101234567 or aliexpress.com/store/all-wholesale-products/1101234567.html)
        m = re.search(r"/store/(?:all-wholesale-products/)?([a-zA-Z0-9_\-]+)", raw)
        if m:
            store_id = m.group(1).replace(".html", "")
            return {
                "store_id": store_id,
                "store_name": f"AliExpress Store {store_id}",
                "original": raw
            }

        # If pure numeric string or slug passed
        if re.match(r"^\d+$", raw):
            return {
                "store_id": raw,
                "store_name": f"AliExpress Store {raw}",
                "original": f"https://www.aliexpress.com/store/{raw}"
            }

        # Fallback for store slug or seller username
        clean_name = raw.split("/")[-1].replace(".html", "").replace("?.*", "")
        return {
            "store_id": clean_name,
            "store_name": clean_name or "AliExpress Store",
            "original": raw if raw.startswith("http") else f"https://www.aliexpress.com/store/{raw}"
        }

    def search(self, store_url: str, include_term: str,
               exclude_terms: list[str] = None,
               condition: str = "all",
               stop_event: threading.Event = None,
               pause_event: threading.Event = None) -> list[dict]:
        """
        Search an AliExpress store or wholesale marketplace for include_term, client-filtering exclude_terms.
        Supports real-time pause and cancel events.
        """
        store_info = self.resolve_store_info(store_url)
        exclude_terms = [e.strip().lower() for e in (exclude_terms or []) if e.strip()]

        items = []
        seen_ids = set()

        if HAS_PLAYWRIGHT:
            try:
                items = self._search_via_playwright(
                    store_info, include_term, exclude_terms, condition, seen_ids,
                    stop_event=stop_event, pause_event=pause_event
                )
                if items or (stop_event and stop_event.is_set()):
                    return items
            except Exception:
                pass

        # Fallback to curl_cffi stealth requests
        page = 1
        seller_label = store_info.get("store_name", "AliExpress Seller")
        while page <= MAX_PAGES:
            if stop_event and stop_event.is_set():
                break
            if pause_event:
                pause_event.wait()

            url = self._build_search_url(store_info, include_term, page)
            html = self._fetch_via_requests(url)
            if not html:
                break

            page_items = self._parse_html(html, seller_label, include_term, exclude_terms)
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

            if new_found == 0 or len(page_items) < 8:
                break

            page += 1
            time.sleep(random.uniform(1.2, 2.5))

        return items

    def _build_search_url(self, store_info: dict, keyword: str, page: int = 1) -> str:
        """Construct the search URL within an AliExpress store or Global Wholesale search."""
        store_id = store_info.get("store_id", "")
        enc_kw = quote_plus(keyword)

        if store_id == "GLOBAL" or not store_id:
            # AliExpress standard wholesale keyword search
            return f"https://www.aliexpress.com/w/wholesale-{enc_kw}.html?page={page}"

        if store_id and store_id.isdigit():
            # Standard AliExpress store wholesale search format
            base = f"https://www.aliexpress.com/store/all-wholesale-products/{store_id}.html"
            params = {"SearchText": keyword}
            if page > 1:
                params["page"] = str(page)
            return f"{base}?{urlencode(params)}"

        elif store_id and not store_id.startswith("http"):
            base = f"https://www.aliexpress.com/store/{store_id}/search"
            params = {"SearchText": keyword}
            if page > 1:
                params["page"] = str(page)
            return f"{base}?{urlencode(params)}"

        # If full URL given
        orig = store_info.get("original", "")
        if "aliexpress.com" in orig:
            sep = "&" if "?" in orig else "?"
            return f"{orig}{sep}SearchText={enc_kw}"

        # Global fallback if not recognized
        return f"https://www.aliexpress.com/w/wholesale-{enc_kw}.html?page={page}"

    def _search_via_playwright(self, store_info: dict,
                               include_term: str, excludes: list[str],
                               condition: str, seen_ids: set,
                               stop_event: threading.Event = None,
                               pause_event: threading.Event = None) -> list[dict]:
        """Execute stealth Playwright browser scraping for AliExpress with anti-slider session persistence."""
        items = []
        page_num = 1
        seller_label = store_info.get("store_name", "AliExpress Seller")

        with sync_playwright() as p:
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials"
            ]
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"

            # Launch persistent Edge or Chromium context
            try:
                browser_context = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_dir,
                    channel="msedge",
                    headless=self.headless,
                    args=launch_args,
                    user_agent=ua,
                    viewport={"width": 1440, "height": 900},
                    locale="en-US"
                )
            except Exception:
                browser_context = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_dir,
                    headless=self.headless,
                    args=launch_args,
                    user_agent=ua,
                    viewport={"width": 1440, "height": 900},
                    locale="en-US"
                )

            page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()

            # Inject CDP stealth overrides
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            """)

            try:
                while page_num <= MAX_PAGES:
                    if stop_event and stop_event.is_set():
                        break
                    if pause_event:
                        pause_event.wait()

                    url = self._build_search_url(store_info, include_term, page_num)

                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    except Exception:
                        pass

                    # Human-like delay & smooth progressive scroll to trigger dynamic lazy loaded products
                    for _ in range(4):
                        time.sleep(0.5)
                        try:
                            page.evaluate("window.scrollBy(0, 800)")
                        except Exception:
                            pass
                    time.sleep(1.0)

                    html = page.content()
                    page_items = self._parse_html(html, seller_label, include_term, excludes)

                    if not page_items:
                        # Try evaluating DOM directly inside Playwright if HTML structure was dynamic
                        page_items = self._extract_dom_items(page, seller_label, include_term, excludes)

                    if not page_items:
                        break

                    new_found = 0
                    for it in page_items:
                        iid = it.get("item_id")
                        dedup_key = iid if iid else it.get("url")
                        if dedup_key and dedup_key not in seen_ids:
                            seen_ids.add(dedup_key)
                            items.append(it)
                            new_found += 1

                    if new_found == 0 or len(page_items) < 8:
                        break

                    page_num += 1

            finally:
                try:
                    browser_context.close()
                except Exception:
                    pass

        return items

    def _extract_dom_items(self, page, seller_label: str, include_term: str, excludes: list[str]) -> list[dict]:
        """Extract product cards directly via Playwright JS evaluation."""
        try:
            raw_cards = page.evaluate("""
                () => {
                    const results = [];
                    const links = document.querySelectorAll('a[href*="/item/"]');
                    const seen = new Set();

                    links.forEach(a => {
                        const href = a.href;
                        const m = href.match(/\\/item\\/(\\d+)\\.html/);
                        if (!m) return;
                        const itemId = m[1];
                        if (seen.has(itemId)) return;
                        seen.add(itemId);

                        const card = a.closest('div[class*="search-item-card"]') ||
                                     a.closest('div[class*="card-out-wrapper"]') ||
                                     a.closest('div[class*="multi--content--"]') || 
                                     a.closest('div[class*="gallery"]') || 
                                     a.closest('div[class*="item"]') || 
                                     a.parentElement;
                        
                        let title = a.innerText || a.getAttribute('title') || '';
                        let img = '';
                        let price = '';
                        let seller = '';

                        if (card) {
                            const imgEl = card.querySelector('img');
                            if (imgEl) img = imgEl.src || imgEl.getAttribute('data-src') || '';
                            
                            const priceEl = card.querySelector('div[class*="price"], span[class*="price"], div[class*="sale"]');
                            if (priceEl) price = priceEl.innerText.trim();

                            const titleEl = card.querySelector('h1, h3, h2, div[class*="title"], span[class*="title"]');
                            if (titleEl && titleEl.innerText.trim().length > 4) {
                                title = titleEl.innerText.trim();
                            }

                            const storeEl = card.querySelector('a[href*="/store/"], span[class*="store--name--"]');
                            if (storeEl && storeEl.innerText.trim()) seller = storeEl.innerText.trim();
                        }

                        results.push({
                            title: title,
                            url: href.split('?')[0],
                            item_id: itemId,
                            image_url: img,
                            price: price,
                            seller: seller
                        });
                    });
                    return results;
                }
            """)

            parsed = []
            for c in raw_cards:
                title = c.get("title", "").strip()
                if not title:
                    continue

                # Apply exclusion filtering
                title_lower = title.lower()
                if any(ex in title_lower for ex in excludes):
                    continue

                parsed.append({
                    "title": title,
                    "url": c.get("url", ""),
                    "image_url": c.get("image_url", ""),
                    "item_id": c.get("item_id", ""),
                    "price": c.get("price", "N/A"),
                    "seller": c.get("seller") or seller_label,
                    "location": "CN / Global",
                    "marketplace": "aliexpress.com",
                    "keyword": include_term,
                    "product_type": "",
                    "brand": ""
                })
            return parsed
        except Exception:
            return []

    def _parse_html(self, html: str, seller_label: str, include_term: str, excludes: list[str]) -> list[dict]:
        """Parse raw HTML for AliExpress product listings and apply exclusion filters."""
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        items = []
        seen_ids = set()

        # Find all item links matching /item/{id}.html
        item_links = soup.find_all("a", href=re.compile(r"/item/(\d+)\.html"))

        for link in item_links:
            href = link.get("href", "")
            if not href.startswith("http"):
                href = "https:" + href if href.startswith("//") else f"https://www.aliexpress.com{href}"

            clean_url = href.split("?")[0]
            m = re.search(r"/item/(\d+)\.html", clean_url)
            if not m:
                continue

            item_id = m.group(1)
            if item_id in seen_ids:
                continue

            # Extract parent product container
            card = (
                link.find_parent(class_=re.compile(r"search-item-card|card-out-wrapper|multi--content--|gallery|item|product-snippet|store-product"))
                or link.parent
            )

            # 1. Price extraction
            raw_text = link.get_text(separator=" ", strip=True)
            m_p = re.search(r"(?:US\s*\$|\$|€|£)\s*[\d,]+(?:\.\d+)?", raw_text)
            price = m_p.group(0) if m_p else "N/A"

            # 2. Title extraction
            title = link.get("title", "").strip()
            if not title and card:
                title_el = card.find(["h1", "h3", "h2"]) or card.find(class_=re.compile(r"title|name|header"))
                if title_el:
                    title = title_el.get_text(strip=True)

            if not title:
                # Split out price & trailing promo text from raw link text
                t_clean = re.split(r"(?:US\s*\$|\$|€|£)\s*\d", raw_text)[0].strip()
                t_clean = re.sub(r"(?:See preview|Similar items|New shoppers|sold|off|Delivery).*$", "", t_clean, flags=re.I).strip()
                if len(t_clean) > 4:
                    title = t_clean

            if not title and card:
                img_el = card.find("img")
                if img_el and img_el.get("alt") and img_el.get("alt").lower() != "product":
                    title = img_el.get("alt").strip()

            if not title or len(title) < 4:
                continue

            # Check client-side exclusion filter
            title_lower = title.lower()
            if any(ex in title_lower for ex in excludes):
                continue

            # 3. Image extraction
            img_url = ""
            if card:
                img_tag = card.find("img")
                if img_tag:
                    img_url = img_tag.get("src") or img_tag.get("data-src") or ""
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url

            # 4. Per-card seller extraction
            card_seller = seller_label
            if card:
                store_link = card.find("a", href=re.compile(r"/store/"))
                if store_link:
                    card_seller = store_link.get_text(strip=True) or store_link.get("title", "") or card_seller

            seen_ids.add(item_id)
            items.append({
                "title": title,
                "url": clean_url,
                "image_url": img_url,
                "item_id": item_id,
                "price": price,
                "seller": card_seller,
                "location": "CN / Global",
                "marketplace": "aliexpress.com",
                "keyword": include_term,
                "product_type": "",
                "brand": ""
            })

        return items

    def _load_cache(self) -> dict:
        cache_file = os.path.join(tempfile.gettempdir(), "aliexpress_store_cache.json")
        try:
            if os.path.exists(cache_file):
                import json
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_cache(self, cache: dict):
        cache_file = os.path.join(tempfile.gettempdir(), "aliexpress_store_cache.json")
        try:
            import json
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def enrich_seller_info(self, items: list[dict],
                           progress_callback=None,
                           stop_event: threading.Event = None,
                           chunk_size: int = 15) -> list[dict]:
        """
        Adaptive Batch Resolver for AliExpress item seller names and store IDs with:
        1. Persistent local disk cache (instantly resolves previously seen items)
        2. Human micro-jitter pacing (1.8s - 3.2s) to prevent velocity flags
        3. Cool-down breathing intervals every chunk (15 items)
        4. Anti-bot CAPTCHA detection & recovery window
        """
        if not HAS_PLAYWRIGHT or not items:
            return items

        cache = self._load_cache()
        items_to_fetch = []

        # Pass 1: Resolve from local cache first (0ms latency, zero rate-limit impact)
        for idx, it in enumerate(items):
            item_id = it.get("item_id")
            if item_id and item_id in cache:
                cached_info = cache[item_id]
                it["seller"] = cached_info.get("seller", it.get("seller"))
                if cached_info.get("store_id"):
                    it["store_id"] = cached_info.get("store_id")
                if progress_callback:
                    progress_callback(idx + 1, len(items), it)
            else:
                current_seller = it.get("seller", "")
                if not current_seller or any(g in current_seller.lower() for g in ("global", "seller", "aliexpress store")):
                    items_to_fetch.append((idx, it))

        if not items_to_fetch:
            return items

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars"
        ]
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"

        with sync_playwright() as p:
            try:
                browser_context = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_dir,
                    channel="msedge",
                    headless=self.headless,
                    args=launch_args,
                    user_agent=ua,
                    viewport={"width": 1440, "height": 900},
                    locale="en-US"
                )
            except Exception:
                browser_context = p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_dir,
                    headless=self.headless,
                    args=launch_args,
                    user_agent=ua,
                    viewport={"width": 1440, "height": 900},
                    locale="en-US"
                )

            page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()

            try:
                processed_in_chunk = 0
                for fetch_idx, (orig_idx, it) in enumerate(items_to_fetch):
                    if stop_event and stop_event.is_set():
                        break

                    # Chunking: Take a 4.5 - 6.5s breathing pause every chunk to reset velocity score
                    if processed_in_chunk >= chunk_size:
                        time.sleep(random.uniform(4.5, 6.5))
                        processed_in_chunk = 0

                    item_id = it.get("item_id")
                    if not item_id:
                        continue

                    url = f"https://www.aliexpress.us/item/{item_id}.html"
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=15000)
                        page.wait_for_selector('a[href*="/store/"]', timeout=3000)
                    except Exception:
                        pass

                    store_res = page.evaluate("""
                        () => {
                            const captcha = document.querySelector('div[class*="baxia-dialog"], div[id*="nc_1_wrapper"], iframe[src*="punish"], div[class*="punish"]');
                            const isCaptcha = !!captcha;

                            const storeLinks = document.querySelectorAll('a[href*="/store/"]');
                            let foundName = '';
                            let foundId = '';
                            
                            storeLinks.forEach(a => {
                                const text = a.innerText.trim();
                                const href = a.href;
                                if (text && text.length > 2 && 
                                    !text.toLowerCase().includes('cart') && 
                                    !text.toLowerCase().includes('feedback') &&
                                    !text.toLowerCase().includes('help')) {
                                    const lines = text.split('\\n').map(l => l.trim()).filter(l => l && !l.toLowerCase().includes('sold by') && !l.includes('('));
                                    if (lines.length > 0 && !foundName) {
                                        foundName = lines[0];
                                    }
                                }
                                const m = href.match(/\\/store\\/(\\d+)/);
                                if (m && !foundId) {
                                    foundId = m[1];
                                }
                            });
                            return { storeName: foundName, storeId: foundId, isCaptcha: isCaptcha };
                        }
                    """)

                    # If CAPTCHA is encountered, wait up to 15s for clearance
                    if store_res.get("isCaptcha"):
                        time.sleep(3.0)
                        # Re-check once after brief delay
                        store_res = page.evaluate("""
                            () => {
                                const storeLinks = document.querySelectorAll('a[href*="/store/"]');
                                let foundName = '';
                                let foundId = '';
                                storeLinks.forEach(a => {
                                    const text = a.innerText.trim();
                                    const m = a.href.match(/\\/store\\/(\\d+)/);
                                    if (m && !foundId) foundId = m[1];
                                    if (text && text.length > 2 && !foundName) foundName = text;
                                });
                                return { storeName: foundName, storeId: foundId };
                            }
                        """)

                    current_seller = it.get("seller", "")
                    s_name = store_res.get("storeName") or (f"Store {store_res.get('storeId')}" if store_res.get('storeId') else current_seller)
                    if s_name:
                        it["seller"] = s_name
                        store_id = store_res.get("storeId", "")
                        if store_id:
                            it["store_id"] = store_id
                        # Cache the resolved item
                        cache[item_id] = {"seller": s_name, "store_id": store_id}

                    processed_in_chunk += 1
                    if progress_callback:
                        progress_callback(orig_idx + 1, len(items), it)

                    # Human-like micro-jitter delay between individual items
                    time.sleep(random.uniform(1.8, 3.2))

                # Persist updated cache to disk
                self._save_cache(cache)

            finally:
                try:
                    browser_context.close()
                except Exception:
                    pass

        return items
