"""
Printerval Scraper Module for Apollo Brand Intelligence Suite.
Specialized in automated retrieval of Print-on-Demand (POD) merchandise,
apparel, stickers, and custom creator products on Printerval (printerval.com).

Features:
- Playwright + Native Microsoft Edge Stealth automation.
- Structured product card extraction (Title, Price, Creator, Product ID, Image).
- High-reliability Seller/Artist Enrichment engine with persistent local disk caching.
- Per-item fault isolation preventing single-item failures from interrupting batch runs.
"""

import os
import re
import json
import time
import random
import logging
import threading
import urllib.parse
from typing import List, Dict, Optional

logger = logging.getLogger("Apollo.PrintervalScraper")


class PrintervalScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._pw = None
        self._browser = None
        self._context = None
        self.profile_dir = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "Apollo_Printerval_Session"
        )
        os.makedirs(self.profile_dir, exist_ok=True)
        self.cache_file = os.path.join(self.profile_dir, "printerval_seller_cache.json")

    def _load_cache(self) -> dict:
        """Load persistent item_id -> {seller, title, price} cache."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self, cache: dict):
        """Save persistent seller cache."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
        except Exception:
            pass

    def _find_edge_path(self) -> Optional[str]:
        """Locate native Microsoft Edge executable on Windows."""
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        ]
        return next((p for p in edge_paths if os.path.exists(p)), None)

    def _get_context(self):
        """Initialize or return existing Playwright context with stealth evasions."""
        from playwright.sync_api import sync_playwright
        if self._pw is None:
            self._pw = sync_playwright().start()

        if self._browser is None:
            edge_path = self._find_edge_path()
            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
            ]

            kwargs = {
                "headless": self.headless,
                "args": args,
            }
            if edge_path:
                kwargs["executable_path"] = edge_path
            else:
                kwargs["channel"] = "msedge"

            try:
                self._browser = self._pw.chromium.launch(**kwargs)
            except Exception:
                kwargs.pop("executable_path", None)
                kwargs["channel"] = "msedge"
                self._browser = self._pw.chromium.launch(**kwargs)

        if self._context is None:
            self._context = self._browser.new_context(
                viewport={"width": 1366, "height": 850},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                locale="en-US",
            )

        return self._context

    def close(self):
        """Safely close browser context and Playwright instance."""
        try:
            if self._context:
                self._context.close()
                self._context = None
            if self._browser:
                self._browser.close()
                self._browser = None
            if self._pw:
                self._pw.stop()
                self._pw = None
        except Exception as e:
            logger.debug(f"Error closing Printerval browser context: {e}")

    def resolve_store_info(self, raw_input: str) -> dict:
        """Parse Printerval shop URL, creator name, or Global Search."""
        raw = raw_input.strip() if raw_input else ""
        if not raw or any(g in raw.lower() for g in ("global", "marketplace", "all", "wholesale", "catalog")):
            return {
                "store_name": "Printerval Global Catalog",
                "original": "https://printerval.com"
            }

        # Check for shop URL (e.g. printerval.com/shop/creatorname)
        m = re.search(r'/shop/([a-zA-Z0-9_\-]+)', raw)
        if m:
            creator = m.group(1)
            return {
                "store_name": f"Printerval Shop ({creator})",
                "original": raw
            }

        clean_name = raw.split("/")[-1].replace("?.*", "").strip()
        return {
            "store_name": f"Printerval Shop ({clean_name})",
            "original": f"https://printerval.com/shop/{clean_name}"
        }

    def search(self, query: str, max_items: int = 50, condition: str = "all", log_callback=None) -> List[Dict]:
        """
        Execute search on Printerval using stealth automation.
        
        Args:
            query: Keyword string (e.g., 'Toyota TRD')
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
        page_num = 1

        encoded_q = urllib.parse.quote(query.strip())
        _log(f"👕 [Printerval] Initiating stealth search for '{query}'...")

        context = self._get_context()
        page = context.pages[0] if context.pages else context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """)

        try:
            while len(results) < max_items and page_num <= 4:
                if page_num == 1:
                    target_url = f"https://printerval.com/search?q={encoded_q}"
                else:
                    target_url = f"https://printerval.com/search?q={encoded_q}&page={page_num}"

                _log(f"🌐 [Printerval] Loading page {page_num}...")
                try:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=22000)
                    page.wait_for_timeout(2500)
                except Exception as ex:
                    _log(f"⚠ Page load timeout on Printerval: {ex}")

                # Extract product cards
                page_items = page.evaluate("""
                    () => {
                        const items = [];
                        const cards = document.querySelectorAll(
                            '.product-item, .item, [class*="product-card"], a[href*="-p"], div[data-product-id]'
                        );
                        
                        for (let c of cards) {
                            const link = c.tagName === 'A' ? c : c.querySelector('a');
                            if (!link) continue;
                            const href = link.href || '';
                            if (!href.includes('-p')) continue;

                            const titleEl = c.querySelector('[class*="title"], h3, h2, span.title') || link;
                            const priceEl = c.querySelector('[class*="price"], .product-price, span[class*="price"]');
                            const sellerEl = c.querySelector('[class*="author"], [class*="artist"], [class*="store"], [class*="seller"]');

                            const title = titleEl ? (titleEl.innerText || '').trim() : '';
                            const price = priceEl ? (priceEl.innerText || '').trim() : '';
                            const seller = sellerEl ? (sellerEl.innerText || '').trim() : '';

                            // Find real image (ignoring svgs and heart icons)
                            let img = '';
                            const allImgs = Array.from(c.querySelectorAll('img')).map(i => i.src || i.getAttribute('data-src') || i.getAttribute('data-original') || '');
                            for (let im of allImgs) {
                                if (im && !im.includes('.svg') && !im.includes('heart') && (im.includes('cdn.printerval.com') || im.startsWith('http'))) {
                                    img = im;
                                    break;
                                }
                            }

                            if (href && (title || price || img)) {
                                items.push({
                                    title: title,
                                    url: href,
                                    price: price,
                                    seller: seller || 'Printerval Creator',
                                    image_url: img
                                });
                            }
                        }
                        return items;
                    }
                """)

                if not page_items:
                    _log(f"ℹ [Printerval] No listing cards found on page {page_num}.")
                    break

                new_count = 0
                for raw_it in page_items:
                    u = raw_it.get("url", "").split("?")[0]
                    m_id = re.search(r'-p(\d+)', u)
                    if not m_id:
                        continue
                    item_id = m_id.group(1)

                    if not item_id or item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)

                    title = raw_it.get("title", "")
                    if not title or title.startswith("$") or len(title) < 3:
                        # Derive title from url slug
                        slug_part = u.split("/")[-1].split("-p")[0].replace("-", " ").title()
                        title = slug_part if slug_part else f"Printerval Product #{item_id}"

                    price = raw_it.get("price", "")
                    if not price or not price.startswith("$"):
                        price = "$19.95"

                    results.append({
                        "brand": "",
                        "product_type": "Merchandise",
                        "title": title,
                        "item_id": item_id,
                        "price": price,
                        "seller": raw_it.get("seller") or "Printerval Creator",
                        "location": "United States",
                        "image_url": raw_it.get("image_url", ""),
                        "url": u,
                        "marketplace": "Printerval",
                        "condition": "New",
                        "keyword": query
                    })
                    new_count += 1

                    if len(results) >= max_items:
                        break

                _log(f"📦 [Printerval] Harvested {new_count} listings from page {page_num} ({len(results)}/{max_items} total).")

                if len(results) >= max_items or new_count == 0:
                    break

                page_num += 1
                time.sleep(1.5)

        except Exception as e:
            _log(f"❌ Error during Printerval scraping: {e}")
            logger.exception("Printerval search failure")
        finally:
            if self.headless:
                self.close()

        _log(f"✅ [Printerval] Search complete: Retrieved {len(results)} listings.")
        return results

    def enrich_seller_info(self, items: List[Dict],
                           progress_callback=None,
                           stop_event: threading.Event = None,
                           chunk_size: int = 15) -> List[Dict]:
        """
        Enrich real creator / artist / shop names and exact pricing for Printerval items.
        Uses persistent disk cache to resolve previously seen items in 0ms.
        """
        if not items:
            return items

        cache = self._load_cache()
        items_to_fetch = []

        # Pass 1: Resolve from local cache
        for idx, it in enumerate(items):
            item_id = str(it.get("item_id", "")).strip()
            if item_id and item_id in cache and cache[item_id].get("image_url"):
                cached = cache[item_id]
                it["seller"] = cached.get("seller", it.get("seller"))
                if cached.get("price"):
                    it["price"] = cached.get("price")
                if cached.get("title") and (not it.get("title") or it.get("title").startswith("Printerval")):
                    it["title"] = cached.get("title")
                if cached.get("image_url") and not it.get("image_url"):
                    it["image_url"] = cached.get("image_url")
                if progress_callback:
                    progress_callback(idx + 1, len(items), it)
            else:
                items_to_fetch.append((idx, it))

        if not items_to_fetch:
            return items

        context = self._get_context()
        page = context.pages[0] if context.pages else context.new_page()

        try:
            processed_in_chunk = 0
            for fetch_idx, (orig_idx, it) in enumerate(items_to_fetch):
                if stop_event and stop_event.is_set():
                    break

                if processed_in_chunk >= chunk_size:
                    time.sleep(random.uniform(2.0, 3.5))
                    processed_in_chunk = 0

                item_id = str(it.get("item_id", "")).strip()
                raw_url = it.get("url", "")
                url = raw_url if raw_url.startswith("http") else f"https://printerval.com/product-p{item_id}"

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=18000)
                    page.wait_for_timeout(1800)

                    # Extract exact creator, price, and canonical title
                    res = page.evaluate("""() => {
                        let seller = '';
                        let price = '';
                        let title = '';

                        // 1. Author / Creator element
                        const authorEls = document.querySelectorAll(
                            'span.author, .author, .design-pod-seller, .other-product-heading-author, .other-product-heading-author-info, [class*="shop-name"], a[href*="/shop/"]'
                        );
                        for (let el of authorEls) {
                            let raw = el ? (el.innerText || '') : '';
                            let txt = raw.trim()
                                .replace(/^Designed\\s+(?:and\\s+sold\\s+)?by\\s*/i, '')
                                .replace(/More\\s+/i, '')
                                .replace(/'s\\s+products.*/i, '')
                                .trim();
                            if (txt && txt.length > 1 && !txt.toLowerCase().includes('printerval') && !txt.toLowerCase().includes('designed')) {
                                seller = txt.split('\\n')[0].trim();
                                break;
                            }
                        }

                        // 2. Fallback via regex across full body text
                        if (!seller && document.body) {
                            const fullText = document.body.innerText || '';
                            const m = fullText.match(/Designed\\s+(?:and\\s+sold\\s+)?by\\s*\\n?\\s*([^\\n\\r]+)/i);
                            if (m && m[1]) {
                                let candidate = m[1].trim();
                                if (candidate && !candidate.toLowerCase().includes('printerval')) {
                                    seller = candidate;
                                }
                            }
                        }

                        // 3. Fallback for "More <Artist>'s products"
                        if (!seller && document.body) {
                            const fullText = document.body.innerText || '';
                            const m2 = fullText.match(/More\\s+([^\\n\\r']+)'s\\s+products/i);
                            if (m2 && m2[1]) {
                                seller = m2[1].trim();
                            }
                        }

                        // Canonical Title from H1
                        const h1 = document.querySelector('h1');
                        if (h1 && h1.innerText) title = h1.innerText.trim();

                        // Price from JSON-LD or DOM
                        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                        for (let s of scripts) {
                            try {
                                const j = JSON.parse(s.innerText || '{}');
                                if (j['@type'] === 'Product' && j.offers && j.offers.price) {
                                    price = '$' + j.offers.price;
                                    break;
                                }
                            } catch(e) {}
                        }

                        if (!price) {
                            const priceEl = document.querySelector('.product-price-current, .pdp-price, .price, [class*="product-price"]');
                            if (priceEl && priceEl.innerText) {
                                const mP = priceEl.innerText.match(/\\$\\s*[\\d,]+(?:\\.\\d+)?/);
                                if (mP) price = mP[0];
                            }
                        }

                        // 4. Extract High-Resolution Product Image
                        let img = '';
                        const og = document.querySelector('meta[property="og:image"], meta[name="og:image"]');
                        if (og && og.content && og.content.startsWith('http')) {
                            img = og.content;
                        }
                        if (!img) {
                            for (let s of scripts) {
                                try {
                                    const j = JSON.parse(s.innerText || '{}');
                                    if (j['image']) {
                                        if (Array.isArray(j['image']) && j['image'].length > 0) {
                                            img = j['image'][0];
                                        } else if (typeof j['image'] === 'string') {
                                            img = j['image'];
                                        }
                                        if (img) break;
                                    }
                                } catch(e) {}
                            }
                        }
                        if (!img) {
                            const domImgs = Array.from(document.querySelectorAll('img')).map(i => i.src || i.getAttribute('data-src') || '');
                            for (let di of domImgs) {
                                if (di && di.includes('cdn.printerval.com') && !di.includes('.svg')) {
                                    img = di;
                                    break;
                                }
                            }
                        }

                        return { seller: seller, price: price, title: title, image_url: img };
                    }""")

                    if res.get("seller"):
                        it["seller"] = res["seller"]
                    if res.get("price"):
                        it["price"] = res["price"]
                    if res.get("title") and (not it.get("title") or it.get("title").startswith("Printerval")):
                        it["title"] = res["title"]
                    if res.get("image_url") and (not it.get("image_url") or "unsafe/540" in it.get("image_url", "")):
                        it["image_url"] = res["image_url"]

                    # Cache result
                    if item_id:
                        cache[item_id] = {
                            "seller": it.get("seller"),
                            "price": it.get("price"),
                            "title": it.get("title"),
                            "image_url": it.get("image_url")
                        }

                except Exception as item_err:
                    logger.debug(f"Error enriching item {item_id} ({url}): {item_err}")

                processed_in_chunk += 1
                if progress_callback:
                    progress_callback(orig_idx + 1, len(items), it)

                time.sleep(random.uniform(0.5, 1.0))

        except Exception as e:
            logger.error(f"Error during Printerval seller enrichment batch: {e}")
        finally:
            self._save_cache(cache)
            if self.headless:
                self.close()

        return items
