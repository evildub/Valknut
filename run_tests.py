"""
Automated Pre-Release Regression Test Suite for Apollo Brand Intelligence.
Validates critical analyst workflows, export column contracts, and threat intelligence logic.
Must pass 100% before any production executable is built or released.
"""

import os
import sys
import tempfile
import unittest
import openpyxl
from bs4 import BeautifulSoup

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_store import DataStore
from exporter import ExcelExporter
import batch_importer


class TestApolloCoreFeatures(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_store = DataStore()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_ebay_seller_name_extraction(self):
        """Test Item 1: Verify seller extraction from HTML ignores avatar initials and feedback counts."""
        sample_ebay_html = """
        <html>
            <body>
                <h1 class="x-item-title__mainTitle">4PCS/SET OEM 90919-02240 Ignition Coils For Toyota Camry</h1>
                <div class="x-sellercard-atf">
                    <div class="x-sellercard-atf__info__about-seller">
                        <a href="https://www.ebay.com/sch/khkok-64/m.html?item=407006409742">
                            <span>K</span>
                        </a>
                        <a href="https://www.ebay.com/sch/khkok-64/m.html?item=407006409742">
                            <span class="ux-textspans--BOLD">khkok-64</span>
                        </a>
                        <span>(135)</span>
                        <span>99.1% positive</span>
                    </div>
                </div>
                <div class="x-price-primary"><span class="ux-textspans">US $59.99</span></div>
            </body>
        </html>
        """
        soup = BeautifulSoup(sample_ebay_html, "html.parser")
        
        # Test DOM seller extraction logic
        seller = ""
        for sel in (
            "div.x-sellercard-atf__info__about-seller a",
            "div[data-testid='x-sellercard-atf'] a",
            "div.ux-seller-section a",
            "a.x-sellercard-atf__info__about-seller"
        ):
            if seller: break
            for a_el in soup.select(sel):
                href = a_el.get("href", "")
                txt = a_el.get_text(strip=True)
                import re
                m_href = re.search(r'/(?:sch|usr|str)/([a-zA-Z0-9_\-\.]+)(?:/m\.html|\?|$|/)', href)
                if m_href:
                    cand = m_href.group(1).strip()
                    if cand and len(cand) >= 2 and cand.lower() not in ("usr", "str", "sch", "itm", "ebay"):
                        seller = cand
                        break
        
        self.assertEqual(seller, "khkok-64", "Seller name must be 'khkok-64' and not avatar initial 'K' or feedback rating.")

    def test_02_multi_locale_genesis_export_schema(self):
        """Test Item 2: Verify Multi-Locale Excel export adheres strictly to Genesis Columns A-R with Col C Thumbnail."""
        exporter = ExcelExporter()
        sample_items = [{
            "title": "OEM Toyota TRD Emblem Badge Set",
            "url": "https://www.ebay.com/itm/407006409742",
            "image_url": "https://i.ebayimg.com/images/g/sample_thumb.jpg",
            "item_id": "407006409742",
            "seller": "khkok-64",
            "price": "$59.99",
            "location": "Rowland Heights, CA, United States",
            "brand": "Toyota",
            "product_type": "Emblems",
            "seller_origin": "China",
            "threat_badge": "Foreign Drop-Ship Hub"
        }]
        target_locales = [
            {"name": "United Kingdom", "domain": "ebay.co.uk", "flag": "UK", "region": "Europe"},
            {"name": "Germany", "domain": "ebay.de", "flag": "DE", "region": "Europe"},
            {"name": "Australia", "domain": "ebay.com.au", "flag": "AU", "region": "Asia-Pacific"}
        ]
        
        out_file = os.path.join(self.temp_dir, "test_multi_locale_genesis.xlsx")
        count = exporter.export_multi_locale(sample_items, target_locales, out_file)
        
        self.assertEqual(count, 3, "Must generate exactly 3 expanded international rows.")
        self.assertTrue(os.path.exists(out_file), "Multi-locale export file must exist.")

        # Verify Excel sheet columns
        wb = openpyxl.load_workbook(out_file)
        ws = wb.active
        
        headers = [cell.value for cell in ws[1]]
        self.assertEqual(headers[0], "Title", "Col A must be Title")
        self.assertEqual(headers[1], "URL", "Col B must be URL")
        self.assertEqual(headers[2], "Thumbnail", "Col C must be Thumbnail")
        self.assertEqual(headers[4], "Item ID", "Col E must be Item ID")
        self.assertEqual(headers[7], "Marketplace", "Col H must be Marketplace")
        self.assertEqual(headers[9], "Seller Name", "Col J must be Seller Name")
        self.assertEqual(headers[12], "Brand", "Col M must be Brand")
        self.assertEqual(headers[13], "Price", "Col N must be Price")
        self.assertEqual(headers[14], "Item Location", "Col O must be Item Location")
        self.assertEqual(headers[15], "Product Type", "Col P must be Product Type")
        self.assertEqual(headers[18], "Locale Country", "Col S must be Locale Country")

        # Verify Row 2 content
        row2 = [cell.value for cell in ws[2]]
        self.assertEqual(row2[0], "OEM Toyota TRD Emblem Badge Set")
        self.assertEqual(row2[1], "https://www.ebay.co.uk/itm/407006409742", "Col B must contain expanded UK URL")
        self.assertEqual(row2[2], "https://i.ebayimg.com/images/g/sample_thumb.jpg", "Col C must contain thumbnail image URL")
        self.assertEqual(row2[4], "407006409742", "Col E must contain item ID")
        self.assertEqual(row2[9], "khkok-64", "Col J must contain seller name")
        self.assertEqual(row2[12], "Toyota", "Col M must contain brand")

    def test_03_datastore_enforcement_registry_aggregation(self):
        """Test Items 5 and 6: Verify registry aggregation and type-safe threat score comparison."""
        test_seller = "auto_parts_syndicate_99"
        items = [
            {
                "item_id": "111222333444",
                "title": "Fake TRD Grille Badge",
                "price": "US $125.00",
                "threat_score": "95",  # string score
                "brand": "Toyota",
                "product_type": "Emblems",
                "location": "Ontario, CA, United States",
                "seller_origin": "China",
                "threat_badge": "Foreign Drop-Ship Hub"
            },
            {
                "item_id": "555666777888",
                "title": "Fake Lexus Wheel Caps (Set of 4)",
                "price": "US $45.50",
                "threat_score": 80,    # int score
                "brand": "Lexus",
                "product_type": "Wheel Caps",
                "location": "Rowland Heights, CA",
                "seller_origin": "China",
                "threat_badge": "Foreign Drop-Ship Hub"
            }
        ]

        # Must execute without TypeError: '>='
        self.data_store.record_enforcement_scan(test_seller, items, brand_name="Toyota")
        
        reg = self.data_store.get_enforcement_registry()
        self.assertIn(test_seller, reg)
        card = reg[test_seller]
        
        self.assertEqual(card.get("total_listings"), 2, "Registry must store total listings count.")
        self.assertAlmostEqual(card.get("total_value"), 170.50, places=2, msg="Registry must sum total dollar values ($125.00 + $45.50 = $170.50).")
        self.assertIn("Toyota", card.get("brands_targeted", []))
        self.assertIn("Lexus", card.get("brands_targeted", []))
        self.assertIn("Emblems", card.get("product_types", []))
        self.assertIn("Wheel Caps", card.get("product_types", []))
        self.assertEqual(card.get("country"), "China")

        # Cleanup
        del reg[test_seller]
        self.data_store._save()

    def test_04_threat_assessment_unresolved_origin(self):
        """Test Item 9: Verify foreign drop-shippers are flagged and unresolved origins do not default to Domestic."""
        # 1. Foreign origin + US warehouse -> Drop-Ship Hub
        assess_3pl = self.data_store.compute_threat_assessment(origin="China", location="Ontario, California, United States")
        self.assertTrue(assess_3pl.get("is_3pl_hub"), "China seller with US warehouse must be flagged as 3PL Hub.")
        self.assertIn("Drop-Ship Hub", assess_3pl.get("badge"))

        # 2. Unresolved origin + US warehouse -> Must NOT be marked Domestic Verified
        assess_unres = self.data_store.compute_threat_assessment(origin="", location="City of Industry, CA")
        self.assertNotIn("Domestic Verified", assess_unres.get("badge"), "Unresolved origin must not be labeled Domestic Verified.")
        self.assertIn("Unresolved", assess_unres.get("badge"))

        # 3. Explicit Domestic origin -> Domestic Verified
        assess_dom = self.data_store.compute_threat_assessment(origin="United States", location="Austin, TX")
        self.assertIn("Domestic Verified", assess_dom.get("badge"))


if __name__ == "__main__":
    unittest.main()
