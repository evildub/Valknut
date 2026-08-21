"""
Mercado Libre Scraper Module for Valknut Anti-Counterfeit Harvester.
Specialized in automated retrieval of Latin American automotive counterfeit listings
across Mexico (MLM), Brazil (MLB), Argentina (MLA), and Colombia (MCO).

Features:
- Playwright + Native Microsoft Edge Stealth automation.
- Persistent session profile at %LOCALAPPDATA%\\Valknut_Meli_Session to preserve trust cookies.
- Intelligent reCAPTCHA / DataDome wall detection with interactive clearance.
- Mandatory Account Authentication detection ("Hello! To continue, log in to your account") with 1-time persistent login saving.
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

logger = logging.getLogger("Valknut.MercadoLibreScraper")

# Approximate Latin American currency conversion rates to USD (updated baseline)
EXCHANGE_RATES_TO_USD = {
    "MXN": 0.053,   # Mexican Peso (~18.8 MXN / USD)
    "BRL": 0.180,   # Brazilian Real (~5.55 BRL / USD)
    "ARS": 0.0010,  # Argentine Peso
    "COP": 0.00025, # Colombian Peso
    "USD": 1.000,
}

# Regional domain mappings
REGIONAL_DOMAINS = {
    "MLM": {"domain": "listado.mercadolibre.com.mx", "home": "https://www.mercadolibre.com.mx", "currency": "MXN", "country": "Mexico"},
    "MLB": {"domain": "lista.mercadolivre.com.br", "home": "https://www.mercadolivre.com.br", "currency": "BRL", "country": "Brazil"},
    "MLA": {"domain": "listado.mercadolibre.com.ar", "home": "https://www.mercadolibre.com.ar", "currency": "ARS", "country": "Argentina"},
    "MCO": {"domain": "listado.mercadolibre.com.co", "home": "https://www.mercadolibre.com.co", "currency": "COP", "country": "Colombia"},
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
            "Valknut_Meli_Session"
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

    def _get_context(self, force_visible: bool = False):
        """Initialize or return existing persistent Playwright context with stealth evasions."""
        from playwright.sync_api import sync_playwright
        if self._context is None:
            self._pw = sync_playwright().start()
            edge_path = self._find_edge_path()

            args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--lang=es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
            ]

            is_headless = False if force_visible else self.headless

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

            self._context = self._pw.chromium.launch_persistent_context(**kwargs)

        return self._context

    def close(self):
        """Safely close browser context and Playwright instance."""
        try:
            if self._context:
                self._context.close()
                self._context = None
            if self._pw:
                self._pw.stop()
                self._pw = None
        except Exception as e:
            logger.debug(f"Error closing Mercado Libre browser context: {e}")

    def launch_interactive_auth(self, site_code: str = "MLM"):
        """
        Open a visible browser session for the user to sign in or solve
        the initial security challenge, persisting cookies permanently.
        """
        def _run():
            try:
                self.close()
                context = self._get_context(force_visible=True)
                page = context.pages[0] if context.pages else context.new_page()
                site_info = REGIONAL_DOMAINS.get(site_code, REGIONAL_DOMAINS["MLM"])
                home_url = site_info["home"]
                page.goto(home_url, wait_until="domcontentloaded")
            except Exception as e:
                logger.error(f"Error launching interactive auth for Mercado Libre: {e}")

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def _extract_item_id(self, url: str) -> str:
        """Extract canonical Mercado Libre listing ID (e.g. MLM-1234567890 or MLM1234567890)."""
        if not url:
            return ""
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
                    log_func("⚠️ [Mercado Libre] Security captcha challenge presented. Please solve the captcha in the browser window...")
                    for sec in range(45):
                        cur_url = page.url.lower()
                        cur_title = page.title().lower()
                        if "captcha/wall" not in cur_url and "seguridad" not in cur_title:
                            log_func("✅ [Mercado Libre] Security captcha passed!")
                            page.wait_for_timeout(2000)
                            break
                        page.wait_for_timeout(1000)
                else:
                    log_func("⚠️ [Mercado Libre] Security verification prompt (reCAPTCHA wall) active.")
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
                    log_func(f"⚠️ Search navigation after login: {ex}")

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
                    _log(f"⚠️ Page load timeout on Mercado Libre: {ex}")

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
                    _log(f"ℹ️ [Mercado Libre] No additional listing cards found on page {page_num}.")
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
                        "condition": "New" if condition == "new" else ("Used" if condition == "used" else "Unspecified"),
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
            if self.headless:
                self.close()

        _log(f"✅ [Mercado Libre] Search complete: Retrieved {len(results)} listings.")
        return results
