# manomano_scraper.py
# Apollo ManoMano Marketplace Scraper & Merchant Intelligence Engine
# Supports France, Spain, Germany, Italy, and UK with concurrent PDP & merchant location resolution.

import os
import re
import time
import logging
import threading
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from curl_cffi import requests
from playwright.sync_api import sync_playwright

logger = logging.getLogger("Apollo.ManoMano")

LOCALES = {
    "France": {"domain": "www.manomano.fr", "search_slug": "/recherche/", "page_param": "page", "default_origin": "France"},
    "Spain": {"domain": "www.manomano.es", "search_slug": "/busqueda/", "page_param": "page", "default_origin": "Spain"},
    "Germany": {"domain": "www.manomano.de", "search_slug": "/suche/", "page_param": "page", "default_origin": "Germany"},
    "Italy": {"domain": "www.manomano.it", "search_slug": "/ricerca/", "page_param": "page", "default_origin": "Italy"},
    "United Kingdom": {"domain": "www.manomano.co.uk", "search_slug": "/search/", "page_param": "page", "default_origin": "United Kingdom"}
}

COUNTRY_MAP = {
    "allemagne": "Germany",
    "germany": "Germany",
    "deutschland": "Germany",
    "france": "France",
    "espagne": "Spain",
    "spain": "Spain",
    "españa": "Spain",
    "italie": "Italy",
    "italy": "Italy",
    "italia": "Italy",
    "royaume-uni": "United Kingdom",
    "united kingdom": "United Kingdom",
    "uk": "United Kingdom",
    "chine": "China",
    "china": "China",
    "pays-bas": "Netherlands",
    "netherlands": "Netherlands",
    "belgique": "Belgium",
    "belgium": "Belgium",
    "pologne": "Poland",
    "poland": "Poland"
}


class ManoManoScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        self.session_dir = os.path.join(appdata, "Apollo", "manomano_session")
        os.makedirs(self.session_dir, exist_ok=True)
        self.merchant_cache = {}
        self.cookies = {}
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    def _sync_cookies_from_browser(self, domain: str = "www.manomano.fr"):
        """Extract valid cookies from persistent Playwright session."""
        try:
            with sync_playwright() as p:
                args = ["--disable-blink-features=AutomationControlled", "--no-first-run", "--no-default-browser-check"]
                context = p.chromium.launch_persistent_context(
                    self.session_dir,
                    headless=True,
                    channel="msedge",
                    args=args
                )
                raw_cookies = context.cookies(f"https://{domain}")
                self.cookies = {c["name"]: c["value"] for c in raw_cookies}
                context.close()
        except Exception as e:
            logger.debug(f"Cookie sync error: {e}")

    def launch_interactive_auth(self, locale_key: str = "France"):
        """Launch visible Edge to clear Cloudflare Turnstile and store clearance cookies."""
        loc = LOCALES.get(locale_key, LOCALES["France"])
        target_url = f"https://{loc['domain']}"
        try:
            with sync_playwright() as p:
                args = ["--disable-blink-features=AutomationControlled", "--no-first-run", "--no-default-browser-check"]
                context = p.chromium.launch_persistent_context(
                    self.session_dir,
                    headless=False,
                    channel="msedge",
                    viewport={"width": 1280, "height": 850},
                    args=args
                )
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(target_url)
                
                # Keep open until user closes or up to 60s
                for _ in range(60):
                    time.sleep(1)
                    try:
                        if not page.is_visible("body") or "just a moment" not in page.title().lower():
                            if "just a moment" not in page.title().lower():
                                time.sleep(2)
                                break
                    except Exception:
                        break
                try:
                    context.close()
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Interactive ManoMano session: {e}")
            import webbrowser
            webbrowser.open(target_url)

    def search(self,
               store_raw: str,
               include_term: str,
               excludes: list = None,
               condition: str = "all",
               max_pages: int = 4,
               locale_key: str = "France",
               stop_event: threading.Event = None,
               pause_event: threading.Event = None) -> list:
        """
        Search ManoMano for target term, crawling multiple pages and enriching PDP + merchant info concurrently.
        """
        excludes = excludes or []
        items = []
        loc = LOCALES.get(locale_key, LOCALES["France"])
        domain = loc["domain"]
        slug = loc["search_slug"]
        default_country = loc["default_origin"]

        if not self.cookies or "cf_clearance" not in self.cookies:
            self._sync_cookies_from_browser(domain)

        headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": f"https://{domain}/"
        }

        clean_term = include_term.strip()
        seen_ids = set()
        raw_items = []

        # 1. Crawl Search Pages
        for page_num in range(1, max_pages + 1):
            if stop_event and stop_event.is_set():
                break
            if pause_event:
                pause_event.wait()

            search_url = f"https://{domain}{slug}{clean_term.replace(' ', '+')}?page={page_num}"
            try:
                r = requests.get(search_url, cookies=self.cookies, headers=headers, impersonate="chrome124", timeout=12)
                if r.status_code == 403 or "just a moment" in r.text.lower():
                    # Attempt refresh cookies
                    self._sync_cookies_from_browser(domain)
                    r = requests.get(search_url, cookies=self.cookies, headers=headers, impersonate="chrome124", timeout=12)
                    if r.status_code != 200:
                        break

                soup = BeautifulSoup(r.text, "html.parser")
                page_found = 0
                for a in soup.find_all("a", href=re.compile(r"/p/")):
                    href = a.get("href", "")
                    if href in seen_ids or "recherche" in href:
                        continue
                    title = a.get_text(" ", strip=True)
                    if len(title) > 8 and not title.startswith("Page"):
                        m_id = re.search(r"-(\d+)$", href.split("?")[0])
                        item_id = m_id.group(1) if m_id else ""
                        if item_id in seen_ids:
                            continue
                        seen_ids.add(item_id if item_id else href)

                        full_url = f"https://{domain}{href}" if href.startswith("/") else href
                        raw_items.append({
                            "item_id": item_id,
                            "title": title,
                            "url": full_url,
                            "domain": domain,
                            "marketplace": domain,
                            "price": "",
                            "image_url": "",
                            "seller": "",
                            "seller_origin": default_country,
                            "location": default_country,
                            "threat_badge": f"🌍 {default_country}",
                            "threat_score": 10,
                            "brand": clean_term.title(),
                            "product_type": "Hardware / Pet / Home"
                        })
                        page_found += 1

                if page_found == 0:
                    break
                time.sleep(0.3)
            except Exception as e:
                logger.debug(f"ManoMano page {page_num} error: {e}")
                break

        if not raw_items:
            return []

        # 2. Enrich PDP & Merchant in Parallel
        def _enrich(item):
            if stop_event and stop_event.is_set():
                return item
            try:
                rp = requests.get(item["url"], cookies=self.cookies, headers=headers, impersonate="chrome124", timeout=10)
                if rp.status_code == 200:
                    p_soup = BeautifulSoup(rp.text, "html.parser")
                    # Price
                    pm = re.search(r'(\d+[\.,]\d{2})\s*€', rp.text)
                    if pm:
                        item["price"] = pm.group(0).replace("", "€").strip()
                    # High-res Image
                    og_img = p_soup.select_one('meta[property="og:image"]')
                    if og_img and og_img.get("content"):
                        item["image_url"] = og_img["content"]

                    # Merchant URL resolution
                    mm = re.search(r'/(marchand-\d+)', rp.text)
                    if mm:
                        m_slug = mm.group(1)
                        if m_slug in self.merchant_cache:
                            s_name, loc = self.merchant_cache[m_slug]
                            item["seller"] = s_name
                            item["seller_origin"] = loc
                            item["location"] = loc
                        else:
                            rm = requests.get(f"https://{domain}/{m_slug}", cookies=self.cookies, headers=headers, impersonate="chrome124", timeout=10)
                            if rm.status_code == 200:
                                m_title = re.search(r'<title data-next-head="">(.*?)</title>', rm.text)
                                s_name = m_title.group(1).strip() if m_title else m_slug
                                
                                # Extract physical location e.g. 'situés à , Germany'
                                loc_match = re.search(r'situ[ée]s?\s+[àa]\s*,\s*([^\n<]+)', rm.text, re.I)
                                raw_country = loc_match.group(1).split("Parole")[0].strip() if loc_match else default_country
                                clean_c = COUNTRY_MAP.get(raw_country.lower().strip(), raw_country.title())
                                
                                self.merchant_cache[m_slug] = (s_name, clean_c)
                                item["seller"] = s_name
                                item["seller_origin"] = clean_c
                                item["location"] = clean_c

                        # Threat badge
                        country = item.get("seller_origin", default_country)
                        if country == "China":
                            item["threat_badge"] = "🇨🇳 Cross-Border Direct"
                            item["threat_score"] = 85
                        else:
                            flag = "🇩🇪" if country == "Germany" else ("🇫🇷" if country == "France" else ("🇪🇸" if country == "Spain" else ("🇮🇹" if country == "Italy" else ("🇬🇧" if "Kingdom" in country else "🌍"))))
                            item["threat_badge"] = f"{flag} {country}"
            except Exception as e:
                logger.debug(f"Error enriching ManoMano item {item.get('item_id')}: {e}")
            return item

        with ThreadPoolExecutor(max_workers=8) as executor:
            enriched_items = list(executor.map(_enrich, raw_items))

        return enriched_items

    def resolve_store_info(self, raw_input: str) -> dict:
        raw = raw_input.strip() if raw_input else ""
        return {
            "store_name": "ManoMano European Search",
            "seller": "",
            "is_store": False,
            "original": raw
        }
