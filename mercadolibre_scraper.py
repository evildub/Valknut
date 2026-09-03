"""
Mercado Libre Scraper Module for Apollo Brand Intelligence Suite.
Specialized in automated retrieval of Latin American automotive counterfeit listings
across Mexico (MLM), Brazil (MLB), Argentina (MLA), and Colombia (MCO).

Features:
- Playwright + Native Microsoft Edge Stealth automation.
- Persistent session profile to preserve trust cookies.
- Intelligent reCAPTCHA / DataDome wall detection with interactive clearance.
- Mandatory Account Authentication detection with 1-time persistent login saving.
- Structured DOM extraction for both classic (ui-search-layout) and modern (poly-card) layouts.
- Currency normalization (MXN/BRL/ARS to USD) for seamless threat intel and ROI valuation.
"""

import os
import re
import time
import logging
import threading
import urllib.parse
from typing import List, Dict, Optional

logger = logging.getLogger("Apollo.MercadoLibreScraper")

# Approximate Latin American currency conversion rates to USD (updated baseline)
EXCHANGE_RATES_TO_USD = {
    "MXN": 0.053,   # Mexican Peso (~18.8 MXN / USD)
    "BRL": 0.180,   # Brazilian Real (~5.55 BRL / USD)
    "ARS": 0.0010,  # Argentine Peso
    "COP": 0.00025, # Colombian Peso
    "CLP": 0.0011,  # Chilean Peso
    "PEN": 0.27,    # Peruvian Sol
    "UYU": 0.025,   # Uruguayan Peso
    "USD": 1.000,
}

# Regional domain mappings
REGIONAL_DOMAINS = {
    "MLM": {"domain": "listado.mercadolibre.com.mx", "home": "https://www.mercadolibre.com.mx", "currency": "MXN", "country": "Mexico", "flag": "🇲🇽", "rate": 0.053},
    "MLB": {"domain": "lista.mercadolivre.com.br", "home": "https://www.mercadolivre.com.br", "currency": "BRL", "country": "Brazil", "flag": "🇧🇷", "rate": 0.180},
    "MLA": {"domain": "listado.mercadolibre.com.ar", "home": "https://www.mercadolibre.com.ar", "currency": "ARS", "country": "Argentina", "flag": "🇦🇷", "rate": 0.0010},
    "MCO": {"domain": "listado.mercadolibre.com.co", "home": "https://www.mercadolibre.com.co", "currency": "COP", "country": "Colombia", "flag": "🇨🇴", "rate": 0.00025},
    "MLC": {"domain": "listado.mercadolibre.cl", "home": "https://www.mercadolibre.cl", "currency": "CLP", "country": "Chile", "flag": "🇨🇱", "rate": 0.0011},
    "MPE": {"domain": "listado.mercadolibre.com.pe", "home": "https://www.mercadolibre.com.pe", "currency": "PEN", "country": "Peru", "flag": "🇵🇪", "rate": 0.27},
    "MLU": {"domain": "listado.mercadolibre.com.uy", "home": "https://www.mercadolibre.com.uy", "currency": "UYU", "country": "Uruguay", "flag": "🇺🇾", "rate": 0.025},
}


class MercadoLibreScraper:
    def __init__(self, headless: bool = True, site_code: str = "MLM"):
        self.headless = headless
        self.site_code = site_code if site_code in REGIONAL_DOMAINS else "MLM"
        self._pw = None
        self._context = None
        
        # Persistent profile directory to store trust cookies & login credentials
        self.profile_dir = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "Apollo_Meli_Session"
        )
        os.makedirs(self.profile_dir, exist_ok=True)

    def _find_edge_path(self) -> Optional[str]:
        """Locate native Microsoft Edge executable on Windows."""
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        ]
        return next((p for p in edge_paths if os.path.exists(p)), None)

    def _clean_profile_locks(self):
        """Clean any stale Chromium singleton lock files and terminate orphaned Edge processes to avoid ProcessSingleton errors."""
        lock_files = [os.path.join(self.profile_dir, lk) for lk in ("SingletonLock", "SingletonSocket", "SingletonCookie", "lockfile")]
        has_locks = any(os.path.exists(lf) for lf in lock_files)
        if has_locks:
            try:
                import subprocess
                subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            except Exception:
                pass
            for lock_file in lock_files:
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                    except Exception:
                        pass

    def _get_context(self, force_visible: bool = False):
        """Initialize or return existing persistent Playwright context with stealth evasions."""
        from playwright.sync_api import sync_playwright
        if self._context is None:
            self._clean_profile_locks()
            if self._pw is None:
                self._pw = sync_playwright().start()
            edge_path = self._find_edge_path()

            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--lang=es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
            ]

            # Cloudflare Evasion: Never run headless=True on Mercado Libre. Position window offscreen when stealth mode is requested.
            is_headless = False
            if self.headless and not force_visible:
                args.extend(["--window-position=-2400,-2400", "--window-size=1366,850"])

            kwargs = {
                "user_data_dir": self.profile_dir,
                "headless": is_headless,
                "args": args,
                "viewport": {"width": 1366, "height": 850},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "locale": "es-MX",
                "timezone_id": "America/Mexico_City",
            }
            if edge_path:
                kwargs["executable_path"] = edge_path

            try:
                self._context = self._pw.chromium.launch_persistent_context(**kwargs)
            except Exception as e:
                logger.warning(f"Persistent context launch retry after process cleanup: {e}")
                self._clean_profile_locks()
                time.sleep(0.6)
                self._context = self._pw.chromium.launch_persistent_context(**kwargs)

        return self._context

    def close(self):
        """Safely close browser context and Playwright instance."""
        try:
            if self._context:
                try:
                    self._context.close()
                except Exception:
                    pass
                self._context = None
            if self._pw:
                try:
                    self._pw.stop()
                except Exception:
                    pass
                self._pw = None
        except Exception as e:
            logger.debug(f"Error closing Mercado Libre browser context: {e}")
        finally:
            self._clean_profile_locks()

    def launch_interactive_auth(self, site_code: str = "MLM"):
        """
        Open a visible browser session for the user to sign in or solve
        the initial security challenge, persisting cookies permanently.
        """
        def _run():
            try:
                self.close()
                self._clean_profile_locks()
                context = self._get_context(force_visible=True)
                
                # Close duplicate restored tabs
                while len(context.pages) > 1:
                    try:
                        context.pages[-1].close()
                    except Exception:
                        break

                page = context.pages[0] if context.pages else context.new_page()
                site_info = REGIONAL_DOMAINS.get(site_code, REGIONAL_DOMAINS.get("MLM", {}))
                home_url = site_info.get("home", "https://www.mercadolibre.com.mx")
                login_url = f"https://www.mercadolibre.com/jms/{site_code.lower()}/lgz/login"

                try:
                    page.goto(login_url, wait_until="domcontentloaded", timeout=15000)
                except Exception:
                    page.goto(home_url, wait_until="domcontentloaded")

                # Wait for user to interact or close browser window
                try:
                    page.wait_for_event("close", timeout=600000)
                except Exception:
                    pass
            except Exception as e:
                logger.error(f"Error launching interactive auth for Mercado Libre: {e}")
            finally:
                self.close()
                self._clean_profile_locks()

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def _extract_item_id(self, url: str) -> str:
        """
        Extract canonical Mercado Libre listing ID.
        Prioritizes winner ID 'wid=' (per-seller specific listing ID on catalog items)
        and 'item_id=' before falling back to master path ID.
        """
        if not url:
            return ""
        # 1. Check for wid= (Winner ID / Specific Catalog Seller Item ID)
        m_wid = re.search(r'[?&#]wid=(ML[A-Z0-9_-]+|\d+)', url, re.IGNORECASE)
        if m_wid:
            wid_val = m_wid.group(1).replace("-", "").upper()
            if not wid_val.startswith("ML"):
                wid_val = f"{self.site_code}{wid_val}"
            return wid_val

        # 2. Check for item_id=
        m_item = re.search(r'[?&#]item_id=(ML[A-Z0-9_-]+|\d+)', url, re.IGNORECASE)
        if m_item:
            it_val = m_item.group(1).replace("-", "").upper()
            if not it_val.startswith("ML"):
                it_val = f"{self.site_code}{it_val}"
            return it_val

        # 3. Direct listing or catalog ID in URL path
        m = re.search(r"/(ML[A-Z]-?\d+)", url, re.IGNORECASE)
        if m:
            return m.group(1).replace("-", "").upper()
        m_num = re.search(r"(\d{8,15})", url)
        if m_num:
            return f"{self.site_code}{m_num.group(1)}"
        return ""

    def _convert_price_to_usd(self, price_raw: str, currency_code: str = "MXN") -> tuple:
        """
        Parse raw localized price string and calculate estimated USD value.
        Returns (display_price_str, numeric_usd_val).
        """
        if not price_raw:
            return "$0.00", 0.0

        clean = re.sub(r"[^\d.,]", "", str(price_raw))
        if "." in clean and "," in clean:
            if clean.rfind(",") > clean.rfind("."):
                clean = clean.replace(".", "").replace(",", ".")
            else:
                clean = clean.replace(",", "")
        elif "," in clean:
            parts = clean.split(",")
            if len(parts) == 2 and len(parts[1]) == 2:
                clean = parts[0] + "." + parts[1]
            else:
                clean = clean.replace(",", "")

        try:
            local_val = float(clean)
        except ValueError:
            local_val = 0.0

        rate = EXCHANGE_RATES_TO_USD.get(currency_code.upper(), 0.053)
        usd_val = round(local_val * rate, 2)
        
        display_str = f"${usd_val:.2f} USD (${local_val:,.0f} {currency_code})"
        return display_str, usd_val

    def _ensure_search_page_loaded(self, page, target_url: str, log_func) -> bool:
        """
        Handle cookie banners, Captcha walls, and mandatory Account Sign-In gates,
        ensuring the page reaches the search results with verified session cookies.
        """
        for cycle in range(3):
            cur_url = page.url.lower()
            cur_title = page.title().lower()

            # 1. Dismiss cookie banner if present
            try:
                cookie_btn = page.query_selector("button[data-testid='action:understood-button'], button:has-text('Aceptar cookies')")
                if cookie_btn and cookie_btn.is_visible():
                    cookie_btn.click()
                    page.wait_for_timeout(500)
            except Exception:
                pass

            # 2. Captcha Wall Handling
            if "captcha/wall" in cur_url or "seguridad" in cur_title:
                if not self.headless:
                    log_func("⚠ [Mercado Libre] Security captcha challenge presented. Please solve the captcha in the browser window...")
                    for sec in range(45):
                        cur_url = page.url.lower()
                        cur_title = page.title().lower()
                        if "captcha/wall" not in cur_url and "seguridad" not in cur_title:
                            log_func("✅ [Mercado Libre] Security captcha passed!")
                            page.wait_for_timeout(2000)
                            break
                        page.wait_for_timeout(1000)
                else:
                    log_func("⚠ [Mercado Libre] Security verification prompt (reCAPTCHA wall) active.")
                    log_func("💡 Tip: Toggle off '👻 Stealth Mode' in top bar to solve once and store trust cookies.")
                    for sec in range(6):
                        cur_url = page.url.lower()
                        cur_title = page.title().lower()
                        if "captcha/wall" not in cur_url and "seguridad" not in cur_title:
                            break
                        page.wait_for_timeout(1000)

            # Update current state
            cur_url = page.url.lower()
            cur_title = page.title().lower()

            # 3. Account Login Gate Detection ("Hello! To continue, log in to your account" / "Para continuar, ingresa a tu cuenta")
            is_login_gate = False
            try:
                body_text = page.inner_text("body").lower()
                if ("to continue, log in" in body_text or 
                    "i already have an account" in body_text or 
                    "para continuar, ingresa" in body_text or 
                    "inicia sesión" in body_text or 
                    "/login" in cur_url or 
                    "auth.mercadolibre" in cur_url):
                    is_login_gate = True
            except Exception:
                pass

            if is_login_gate:
                if not self.headless:
                    log_func("🔑 [Mercado Libre] Account sign-in required ('Hello! To continue, log in to your account').")
                    log_func("👉 Please click 'I already have an account' (or 'I'm new') in the open browser to sign in. The session will be saved permanently!")
                    
                    # Wait up to 90 seconds for user to complete sign-in
                    for wait_sec in range(90):
                        cur_url = page.url.lower()
                        cur_title = page.title().lower()
                        try:
                            body_check = page.inner_text("body").lower()
                            if ("to continue, log in" not in body_check and 
                                "i already have an account" not in body_check and 
                                "/login" not in cur_url and 
                                "auth.mercadolibre" not in cur_url):
                                log_func("✅ [Mercado Libre] Account login verified! Session permanently stored.")
                                page.wait_for_timeout(2000)
                                break
                        except Exception:
                            pass
                        page.wait_for_timeout(1000)
                else:
                    log_func("🔑 [Mercado Libre] Mandatory login prompt encountered.")
                    log_func("💡 Tip: Toggle off '👻 Stealth Mode' in top bar to sign in once. Your session will persist for all future searches.")

                # Re-navigate directly to target search results with the authenticated session
                try:
                    log_func(f"🌐 [Mercado Libre] Navigating to search results: {target_url}")
                    page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
                    page.wait_for_timeout(3000)
                except Exception as ex:
                    log_func(f"⚠ Search navigation after login: {ex}")

            # 4. Check if listing cards are present on page
            cards_count = page.evaluate("""() => {
                return document.querySelectorAll(
                    '.ui-search-layout__item, .poly-card, li.ui-search-layout__item, div.poly-card__content, .ui-search-result, ol.ui-search-layout li'
                ).length;
            }""")

            if cards_count > 0:
                return True

            # If we're on the search URL and cards are still rendering, wait briefly
            if "listado.mercadolibre" in cur_url or "lista.mercadolivre" in cur_url:
                page.wait_for_timeout(2000)
                cards_count = page.evaluate("""() => {
                    return document.querySelectorAll(
                        '.ui-search-layout__item, .poly-card, li.ui-search-layout__item, div.poly-card__content, .ui-search-result, ol.ui-search-layout li'
                    ).length;
                }""")
                if cards_count > 0:
                    return True

        return True

    def search(self, query: str, max_items: int = 50, condition: str = "all", log_callback=None) -> List[Dict]:
        """
        Execute search on Mercado Libre using persistent stealth automation.
        
        Args:
            query: Keyword string (e.g., 'Toyota emblem')
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
        site_info = REGIONAL_DOMAINS.get(self.site_code, REGIONAL_DOMAINS["MLM"])
        domain = site_info["domain"]
        currency = site_info["currency"]
        country = site_info["country"]

        slug = urllib.parse.quote(query.strip().replace(" ", "-"))
        raw_query = urllib.parse.quote(query.strip())
        base_search_url = f"https://{domain}/{slug}#D[A:{raw_query}]"

        _log(f"🇲🇽 [Mercado Libre {country}] Initiating stealth search for '{query}'...")

        context = self._get_context()
        page = context.pages[0] if context.pages else context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

        current_offset = 1
        page_num = 1
        seen_urls = set()

        try:
            while len(results) < max_items and page_num <= 4:
                if page_num == 1:
                    target_url = base_search_url
                else:
                    target_url = f"https://{domain}/{slug}_Desde_{current_offset}#D[A:{raw_query}]"

                _log(f"🌐 [Mercado Libre] Loading page {page_num}...")
                try:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
                    page.wait_for_timeout(2500)
                except Exception as ex:
                    _log(f"⚠ Page load timeout on Mercado Libre: {ex}")

                # Ensure page has cleared security challenge, login redirects, and reached search results
                self._ensure_search_page_loaded(page, target_url, _log)

                # Extract listing cards via DOM evaluation
                page_items = page.evaluate("""
                    () => {
                        const items = [];
                        const cards = document.querySelectorAll(
                            '.ui-search-layout__item, .poly-card, li.ui-search-layout__item, div.poly-card__content, .ui-search-result, ol.ui-search-layout li'
                        );
                        
                        for (let c of cards) {
                            const titleEl = c.querySelector(
                                '.ui-search-item__title, .poly-component__title, h2, a.poly-component__title, .ui-search-item__group__element, h3.poly-component__title-wrapper'
                            );
                            const linkEl = c.querySelector(
                                'a.ui-search-link, a.poly-component__title, a[href*="articulo.mercadolibre"], a.ui-search-result__link, a[href*="mercadolibre.com"]'
                            );
                            const priceEl = c.querySelector(
                                '.andes-money-amount__fraction, .ui-search-price__second-line .andes-money-amount__fraction, .poly-price__current .andes-money-amount__fraction'
                            );
                            const imgEl = c.querySelector('img');
                            const sellerEl = c.querySelector(
                                '.ui-search-official-store-label, .poly-component__seller, span.poly-component__seller, .ui-search-item__brand-discoverability'
                            );
                            const locEl = c.querySelector(
                                '.ui-search-item__location, .ui-search-item__group__element--location, .poly-component__location'
                            );
                            
                            if (titleEl && linkEl) {
                                const title = titleEl.innerText.trim();
                                const url = linkEl.href;
                                const price = priceEl ? priceEl.innerText.trim() : '';
                                const seller = sellerEl ? sellerEl.innerText.trim().replace(/^Por\\s+/i, '') : '';
                                const location = locEl ? locEl.innerText.trim() : '';
                                const img = imgEl ? (imgEl.src || imgEl.getAttribute('data-src') || '') : '';
                                
                                if (title && url) {
                                    items.push({
                                        title: title,
                                        url: url,
                                        price_raw: price,
                                        seller: seller,
                                        location: location,
                                        image_url: img
                                    });
                                }
                            }
                        }
                        return items;
                    }
                """)

                if not page_items:
                    _log(f"ℹ [Mercado Libre] No additional listing cards found on page {page_num}.")
                    break

                new_count = 0
                for raw_it in page_items:
                    item_url = raw_it.get("url", "").split("?")[0]
                    if not item_url or item_url in seen_urls:
                        continue
                    seen_urls.add(item_url)

                    item_id = self._extract_item_id(item_url)
                    price_display, price_usd = self._convert_price_to_usd(raw_it.get("price_raw", ""), currency)
                    seller_name = raw_it.get("seller") or "Mercado Libre Seller"
                    item_loc = raw_it.get("location") or country
                    is_catalog = "/p/" in item_url

                    results.append({
                        "brand": "",
                        "product_type": "",
                        "title": raw_it.get("title", ""),
                        "item_id": item_id,
                        "price": price_display,
                        "price_usd": price_usd,
                        "seller": seller_name,
                        "location": item_loc,
                        "image_url": raw_it.get("image_url", ""),
                        "url": raw_it.get("url", ""),
                        "marketplace": "Mercado Libre",
                        "condition": "Catalog Buy Box" if is_catalog else ("New" if condition == "new" else ("Used" if condition == "used" else "Unspecified")),
                        "keyword": query
                    })
                    new_count += 1

                    if len(results) >= max_items:
                        break

                _log(f"📦 [Mercado Libre] Harvested {new_count} unique listings from page {page_num} ({len(results)}/{max_items} total).")

                if len(results) >= max_items or new_count == 0:
                    break

                page_num += 1
                current_offset += 50
                time.sleep(1.5)

        except Exception as e:
            _log(f"❌ Error during Mercado Libre scraping: {e}")
            logger.exception("Mercado Libre search failure")
        finally:
            self.close()

        _log(f"✅ [Mercado Libre] Search complete: Retrieved {len(results)} listings.")
        return results

    def extract_catalog_sellers(self, catalog_url: str, title: str = "", default_brand: str = "") -> List[Dict]:
        """
        Deep Catalog Multi-Seller Expansion.
        Extracts Buy Box winner and all competing catalog merchants from /p/ product pages.
        """
        catalog_items = []
        site_info = REGIONAL_DOMAINS.get(self.site_code, REGIONAL_DOMAINS["MLM"])
        currency = site_info["currency"]
        country = site_info["country"]

        try:
            context = self._get_context()
            page = context.new_page()
            page.goto(catalog_url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(2000)

            data = page.evaluate("""
                () => {
                    const res = [];
                    const seen = new Set();
                    
                    const tEl = document.querySelector('h1.ui-pdp-title, h1');
                    const title = tEl ? tEl.innerText.trim() : '';
                    const imgEl = document.querySelector('.ui-pdp-image, .ui-pdp-gallery__figure img, img.ui-pdp-image');
                    const img = imgEl ? (imgEl.src || imgEl.getAttribute('data-src') || '') : '';

                    // 1. Primary Buy Box Winner
                    let mainSeller = '';
                    const selNodes = document.querySelectorAll('.ui-pdp-seller__link-trigger, .ui-seller-info a, a.ui-pdp-seller__header__title, span.ui-pdp-color--BLUE, .ui-pdp-seller__link, .ui-seller-data-header__title-wrapper');
                    for (let n of selNodes) {
                        const txt = n.innerText.trim();
                        if (txt && !txt.includes('Mercado Puntos') && !txt.includes('Devolución') && !txt.includes('Garantía') && !txt.includes('Medios de pago') && !txt.includes('Ver más')) {
                            mainSeller = txt.replace(/^Vendido por\\s+/i, '').replace(/^Por\\s+/i, '').trim();
                            break;
                        }
                    }
                    if (!mainSeller) {
                        const allNodes = document.querySelectorAll('p, span, div, a');
                        for (let n of allNodes) {
                            const text = n.innerText ? n.innerText.trim() : '';
                            if (text.startsWith('Vendido por')) {
                                const lines = text.split('\\n').map(x => x.trim()).filter(x => x.length > 0);
                                if (lines.length >= 2) {
                                    let candidate = lines[1].replace(/^por\\s+/i, '').trim();
                                    if (candidate && !['mercado libre', 'ir a la página', 'seguir', 'mercado puntos'].some(b => candidate.toLowerCase().includes(b))) {
                                        mainSeller = candidate;
                                        break;
                                    }
                                }
                            }
                        }
                    }

                    const mainPriceEl = document.querySelector('.ui-pdp-price__second-line .andes-money-amount__fraction, .andes-money-amount__fraction');
                    const mainPrice = mainPriceEl ? mainPriceEl.innerText.trim() : '';

                    if (mainSeller && !seen.has(mainSeller.toLowerCase())) {
                        seen.add(mainSeller.toLowerCase());
                        res.push({
                            title: title,
                            seller: mainSeller,
                            price_raw: mainPrice,
                            role: 'Buy Box Winner',
                            image_url: img,
                            url: window.location.href,
                            item_id: ''
                        });
                    }

                    // 2. Competing Sellers in 'Otras opciones de compra'
                    const otherLinks = document.querySelectorAll('a[href*=\"_CustId_\"], a[href*=\"seller_id=\"], .ui-pdp-other-sellers a');
                    for (let a of otherLinks) {
                        let sName = a.innerText.trim().replace(/^Vendido por\\s+/i, '').replace(/^Por\\s+/i, '').trim();
                        const href = a.href || '';
                        
                        if (sName.startsWith('+') || sName.toLowerCase().includes('producto') || sName.toLowerCase().includes('ver más')) {
                            const custMatch = href.match(/_CustId_(\\d+)/);
                            if (custMatch) {
                                sName = 'Seller_CustId_' + custMatch[1];
                            }
                        }

                        let cPrice = '';
                        let cItemId = '';
                        const container = a.closest('section') || a.closest('div.ui-pdp-other-sellers') || a.closest('div');
                        if (container) {
                            const pEl = container.querySelector('.andes-money-amount__fraction');
                            if (pEl) cPrice = pEl.innerText.trim();
                        }
                        const mItem = href.match(/item_id=(ML[A-Z]-?\\d+)/i);
                        if (mItem) cItemId = mItem[1].replace('-', '').toUpperCase();

                        if (sName && !seen.has(sName.toLowerCase()) && !['ver más', 'comprar', 'agregar', 'mercado'].some(x => sName.toLowerCase().includes(x))) {
                            seen.add(sName.toLowerCase());
                            res.push({
                                title: title,
                                seller: sName,
                                price_raw: cPrice || mainPrice,
                                role: 'Catalog Competitor',
                                image_url: img,
                                url: href || window.location.href,
                                item_id: cItemId
                            });
                        }
                    }

                    return { title: title, img: img, sellers: res };
                }
            """)
            page.close()

            p_title = data.get("title") or title or "Mercado Libre Catalog Product"
            p_img = data.get("img") or ""
            sellers_list = data.get("sellers") or []
            base_item_id = self._extract_item_id(catalog_url)

            if not sellers_list:
                price_disp, price_usd = self._convert_price_to_usd("", currency)
                catalog_items.append({
                    "brand": default_brand,
                    "product_type": "Consumer Product",
                    "title": p_title,
                    "item_id": base_item_id,
                    "price": price_disp,
                    "price_usd": price_usd,
                    "seller": "Mercado Libre Seller",
                    "location": country,
                    "image_url": p_img,
                    "url": catalog_url,
                    "marketplace": "Mercado Libre",
                    "condition": "Catalog Product",
                    "keyword": ""
                })
            else:
                for s in sellers_list:
                    price_disp, price_usd = self._convert_price_to_usd(s.get("price_raw") or "", currency)
                    s_id = s.get("item_id") or base_item_id
                    catalog_items.append({
                        "brand": default_brand,
                        "product_type": "Consumer Product",
                        "title": f"{p_title} [{s.get('role', 'Catalog')}: {s.get('seller')}]",
                        "item_id": s_id,
                        "price": price_disp,
                        "price_usd": price_usd,
                        "seller": s.get("seller", "Mercado Libre Seller"),
                        "location": country,
                        "image_url": p_img,
                        "url": s.get("url", catalog_url),
                        "marketplace": "Mercado Libre",
                        "condition": s.get("role", "Catalog Listing"),
                        "keyword": ""
                    })

        except Exception as ex:
            logger.debug(f"Error expanding catalog item {catalog_url}: {ex}")
            price_disp, price_usd = self._convert_price_to_usd("", currency)
            catalog_items.append({
                "brand": default_brand,
                "product_type": "Consumer Product",
                "title": title or "Mercado Libre Catalog Listing",
                "item_id": self._extract_item_id(catalog_url),
                "price": price_disp,
                "price_usd": price_usd,
                "seller": "Mercado Libre Seller",
                "location": country,
                "image_url": "",
                "url": catalog_url,
                "marketplace": "Mercado Libre",
                "condition": "Catalog Listing",
                "keyword": ""
            })
        finally:
            self.close()

        return catalog_items

    def enrich_seller_info(self, items: List[Dict], progress_callback=None, stop_event=None):
        """
        Enrich Mercado Libre listings in-place with verified seller handle, location, and reputation.
        """
        if not items:
            return

        total = len(items)
        context = self._get_context()

        try:
            for idx, it in enumerate(items, 1):
                if stop_event and stop_event.is_set():
                    break

                url = it.get("url", "")
                if not url:
                    continue

                try:
                    page = context.new_page()
                    page.goto(url, wait_until="domcontentloaded", timeout=20000)

                    # Dynamic React Hydration polling: Wait until 'Vendido por' or seller triggers appear
                    for _ in range(8):
                        try:
                            has_seller = page.evaluate("() => document.body.innerText.includes('Vendido por') || !!document.querySelector('.ui-pdp-seller__link-trigger, .ui-seller-info a, a.ui-pdp-seller__header__title')")
                            if has_seller:
                                break
                        except Exception:
                            pass
                        page.wait_for_timeout(500)

                    info = page.evaluate("""
                        () => {
                            let sName = '';
                            let sLoc = '';
                            let sRep = '';

                            // 1. Check direct seller trigger link
                            const selNodes = document.querySelectorAll('.ui-pdp-seller__link-trigger, .ui-seller-info a, a.ui-pdp-seller__header__title, span.ui-pdp-color--BLUE, .ui-pdp-seller__link, .ui-seller-data-header__title-wrapper');
                            for (let n of selNodes) {
                                const txt = n.innerText.trim();
                                if (txt && !txt.includes('Mercado Puntos') && !txt.includes('Devolución') && !txt.includes('Garantía') && !txt.includes('Medios de pago') && !txt.includes('Ver más')) {
                                    sName = txt.replace(/^Vendido por\\s+/i, '').replace(/^Por\\s+/i, '').trim();
                                    break;
                                }
                            }

                            // 2. Check multiline "Vendido por" (e.g. "Vendido por\\nNocnoc Us Shop\\n...")
                            if (!sName) {
                                const allNodes = document.querySelectorAll('p, span, div, a');
                                for (let n of allNodes) {
                                    const text = n.innerText ? n.innerText.trim() : '';
                                    if (text.startsWith('Vendido por')) {
                                        const lines = text.split('\\n').map(x => x.trim()).filter(x => x.length > 0);
                                        if (lines.length >= 2) {
                                            let candidate = lines[1].replace(/^por\\s+/i, '').trim();
                                            if (candidate && !['mercado libre', 'ir a la página', 'seguir', 'mercado puntos'].some(b => candidate.toLowerCase().includes(b))) {
                                                sName = candidate;
                                                break;
                                            }
                                        }
                                    }
                                }
                            }

                            const locEl = document.querySelector('.ui-seller-info__location, .ui-pdp-seller__location, .poly-component__location');
                            if (locEl) sLoc = locEl.innerText.trim();

                            if (!sLoc) {
                                const allTextNodes = document.querySelectorAll('p, span, div');
                                for (let n of allTextNodes) {
                                    const txt = n.innerText ? n.innerText.trim() : '';
                                    if (txt.startsWith('Envío desde') || txt.startsWith('Envio desde')) {
                                        sLoc = txt.replace(/^Envío desde\\s+/i, '').replace(/^Envio desde\\s+/i, '').trim();
                                        break;
                                    }
                                    if (txt.includes('Ubicación del vendedor') || txt.includes('Ubicacion del vendedor')) {
                                        sLoc = txt.replace(/Ubicaci[oó]n del vendedor/i, '').trim();
                                        break;
                                    }
                                }
                            }

                            const repEl = document.querySelector('.ui-seller-info__status-info, .ui-pdp-seller__reputation, .ui-seller-info__subtitle');
                            if (repEl) sRep = repEl.innerText.trim();

                            if (!sRep) {
                                const repNodes = document.querySelectorAll('span, p, div, h3');
                                for (let n of repNodes) {
                                    const txt = n.innerText ? n.innerText.trim() : '';
                                    if (txt.includes('MercadoLíder') || txt.includes('MercadoLider') || txt.includes('Tienda oficial') || txt.includes('Uno de los mejores')) {
                                        sRep = txt.split('\\n')[0].trim();
                                        break;
                                    }
                                }
                            }

                            return { seller: sName, location: sLoc, reputation: sRep };
                        }
                    """)
                    page.close()

                    if info.get("seller"):
                        it["seller"] = info["seller"]
                    if info.get("location"):
                        it["seller_origin"] = info["location"]
                        it["location"] = info["location"]
                    if info.get("reputation"):
                        it["threat_badge"] = f"MeLi: {info['reputation']}"

                except Exception as e:
                    logger.debug(f"Error enriching Mercado Libre item {url}: {e}")

                if progress_callback:
                    progress_callback(idx, total, it)
        finally:
            self.close()

    def search_multi_region(self, query: str, site_codes: List[str] = None, max_items_per_region: int = 25, condition: str = "all", log_callback=None) -> List[Dict]:
        """
        Execute multi-regional sweep across selected Latin American Mercado Libre domains.
        """
        if not site_codes:
            site_codes = ["MLM", "MLB", "MLA", "MCO"]

        all_results = []
        for code in site_codes:
            if code not in REGIONAL_DOMAINS:
                continue
            orig_site = self.site_code
            self.site_code = code
            reg_info = REGIONAL_DOMAINS[code]
            if log_callback:
                log_callback(f"🌎 [{reg_info['flag']} {reg_info['country']}] Initiating scan for '{query}'...")
            try:
                res = self.search(query, max_items=max_items_per_region, condition=condition, log_callback=log_callback)
                for r in res:
                    r["country"] = reg_info["country"]
                    r["marketplace"] = f"Mercado Libre ({reg_info['flag']} {reg_info['country']})"
                all_results.extend(res)
            except Exception as e:
                logger.debug(f"Error in multi-region scan for {code}: {e}")
            finally:
                self.site_code = orig_site

        return all_results

    def find_connected_network(self, item_id: str, item_url: str, target_img: str = "") -> List[Dict]:
        """
        On-Demand Visual Syndicate & Connected Seller Hunter for Mercado Libre.
        Scans product page carousels:
        - "Publicaciones del vendedor" (Seller's other storefront items)
        - "Quienes vieron este producto también compraron" (Competitor & related items)
        - "Otras opciones de compra" (Competing catalog merchants)
        """
        results = []
        if not item_url:
            return results

        site_info = REGIONAL_DOMAINS.get(self.site_code, REGIONAL_DOMAINS["MLM"])
        currency = site_info["currency"]
        country = site_info["country"]

        try:
            context = self._get_context()
            page = context.new_page()
            page.goto(item_url, wait_until="domcontentloaded", timeout=25000)

            # Dynamic React Hydration polling: Wait until recommendations carousels render
            for _ in range(8):
                try:
                    has_carousels = page.evaluate("() => !!document.querySelector('.ui-recommendations-card, .poly-card, div.ui-pdp-recommendations, div.ui-recommendations-carousel')")
                    if has_carousels:
                        break
                except Exception:
                    pass
                page.wait_for_timeout(500)

            carousels_data = page.evaluate("""
                () => {
                    const discovered = [];
                    const seen = new Set();

                    const sections = document.querySelectorAll('section, div.ui-pdp-recommendations, div.ui-recommendations-carousel, div[class*=\"recommendations\"], div[class*=\"carousel\"], div.ui-pdp-other-sellers');
                    for (let sec of sections) {
                        const hEl = sec.querySelector('h2, h3, .ui-recommendations-title, .ui-pdp-container__title');
                        let secTitle = hEl ? hEl.innerText.trim() : '';
                        let secType = '👥 Related / Competitor Product';

                        if (secTitle.toLowerCase().includes('vendedor')) {
                            secType = '🏪 Seller\\'s Other Products';
                        } else if (secTitle.toLowerCase().includes('opciones de compra') || secTitle.toLowerCase().includes('otras opciones')) {
                            secType = '⚔ Buy Box Competitor';
                        } else if (secTitle.toLowerCase().includes('vieron') || secTitle.toLowerCase().includes('compraron')) {
                            secType = '👥 Customers Also Viewed';
                        }

                        const cards = sec.querySelectorAll('.ui-recommendations-card, .poly-card, .ui-search-result, a[href*=\"mercadolibre\"], a[href*=\"mercadolivre\"]');
                        for (let card of cards) {
                            const tEl = card.querySelector('.ui-recommendations-card__title, .poly-component__title, h2, h3, p');
                            const pEl = card.querySelector('.andes-money-amount__fraction');
                            const sEl = card.querySelector('.ui-recommendations-card__seller, .poly-component__seller, span.poly-component__seller');
                            const imgEl = card.querySelector('img');
                            const href = card.tagName === 'A' ? card.href : (card.querySelector('a') ? card.querySelector('a').href : '');

                            if (href && (tEl || pEl)) {
                                const cleanHref = href.split('#')[0];
                                if (!seen.has(cleanHref)) {
                                    seen.add(cleanHref);
                                    discovered.push({
                                        title: tEl ? tEl.innerText.trim() : 'Mercado Libre Listing',
                                        price_raw: pEl ? pEl.innerText.trim() : '',
                                        seller: sEl ? sEl.innerText.trim().replace(/^Por\\s+/i, '') : '',
                                        url: href,
                                        image_url: imgEl ? (imgEl.src || imgEl.getAttribute('data-src') || '') : '',
                                        network_type: secType
                                    });
                                }
                            }
                        }
                    }
                    return discovered;
                }
            """)
            page.close()

            for d in carousels_data:
                c_url = d.get("url", "")
                c_id = self._extract_item_id(c_url)
                p_disp, p_usd = self._convert_price_to_usd(d.get("price_raw", ""), currency)
                s_name = d.get("seller") or "Mercado Libre Merchant"

                results.append({
                    "brand": "",
                    "product_type": "",
                    "title": d.get("title", ""),
                    "item_id": c_id,
                    "price": p_disp,
                    "price_usd": p_usd,
                    "seller": s_name,
                    "location": country,
                    "seller_origin": country,
                    "image_url": d.get("image_url", ""),
                    "url": c_url,
                    "marketplace": f"Mercado Libre ({country})",
                    "condition": d.get("network_type", "Connected Listing"),
                    "similarity": "Carousel Asset",
                    "match_type": d.get("network_type", "Connected Listing"),
                })

        except Exception as e:
            logger.debug(f"Error finding connected network for Mercado Libre item {item_url}: {e}")
        finally:
            self.close()

        return results
