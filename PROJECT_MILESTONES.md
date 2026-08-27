# Apollo Brand Intelligence — Development History & Project Milestones

**Lead Analyst & Architect:** Jerry Seidenstucker (Senior Brand Protection Analyst)  
**Platform Evolution:** Half-start single-query eBay scraper -> Multi-Marketplace Enterprise Threat Intelligence & Reverse-Image Clustering Suite  
**Date of Milestone Audit:** August 26, 2026

---

## 📊 Project Scope & Metric Summary

* **Codebase Scale:**
  * **Starting Point:** ~600 lines (single script, frequent UI thread locking, basic 5-column unformatted spreadsheet output)
  * **Current State:** **16,500+ lines of robust Python** across 11 modular subsystems (main.py, scraper.py, isual_catalog.py, isual_catalog_modal.py, atch_importer.py, exporter.py, intel_pack_manager.py, data_store.py, inted_scraper.py, mercadolibre_scraper.py, 
un_tests.py).
* **Total Engineering & Architectural Changes:** **300+ discrete improvements & fixes**
  * ~75 major functional capabilities (Perceptual Hashing visual catalog, multi-hash threat clusters, Genesis 18-column export, multi-locale cross-border projections, 3PL warehouse threat heuristics, connected seller network hunter, adhoc batch spreadsheet ingestion, dealership whitelist shielding, in-table cell editing, .apollo intelligence sharing).
  * ~280+ edge-case bug fixes and reliability optimizations.
* **Hours Invested:**
  * **Jerry Seidenstucker Direct Investment:** ~**70 to 80+ concentrated evening/night hours** (regularly 6:00 PM to 2:00-3:00 AM) driving architecture, domain expertise, real-world data validation, and iterative testing.
  * **Commercial Equivalent:** Standard agency / corporate IT equivalent of a **3-person software engineering team working for 3 to 4 months (~400-500 billable engineering hours)**.

---

## 🏆 Key Milestones & Version Trajectory

### v1.0.0 – Foundations & Anti-Hang Architecture
* Rebuilt scraper pipeline with background threading and Playwright stealth engine.
* Added persistent data.json storage in %LOCALAPPDATA% to prevent user settings wipe on updates.
* Implemented live results table with thumbnail previews.

### v1.2.0 – Threat Intelligence & Genesis Compliance
* Standardized the **Genesis 18-Column Export Template** with image URLs pinned to Column C.
* Built **Foreign Drop-Ship & 3PL Warehouse Threat Heuristics** (tracking domestic warehouse fronts operated by overseas recidivist merchants).
* Added cumulative **Enforcement Registry** tracking total infringing listings and dollar exposure per seller.

### v1.4.0 – Global Expansion & Reverse Image Dredging
* Added **Mercado Libre (MLM, MLB, MLA, MLC, MCO)** Latin American scraper engine.
* Added **Vinted (UK, FR, DE, IT, ES)** European peer-to-peer scraper engine.
* Built **Multi-Locale Expander** generating international localized queries across European and American domains.
* Built **Visual Threat Catalog** with 64-bit Perceptual Hashing (pHash) and multi-variant threat clusters.

### v1.5.0 – v1.5.2 – Enterprise Workflow Polish & Reliability
* Added **Ad-Hoc Batch Excel / CSV / URL Importer** with multi-marketplace auto-detection.
* Built **Authorized Dealership Whitelist Shielding** preventing scans on approved dealers.
* Added **In-Table Double-Click & Context Menu Editing** for direct brand, title, seller, and category corrections.
* Added **Live Listing Rescraping / Refreshing (F5)** and **Merchant Handle Enrichment**.
* Implemented the **Mandatory Automated Regression Test Harness (
un_tests.py)**.

### v1.6.0 – Knowledge Sharing, Dynamic Sensitivity & Enterprise Scaling
* Built **Analyst Intelligence Packs (.apollo bundles)** for 1-click sharing of brand trees, negative exclusions, whitelists, presets, and visual threat cards across analysts and workstations.
* Connected **Dynamic Visual Sensitivity Slider** allowing real-time Hamming distance threshold tuning and 1-click fast OEM benign cleanups.
* Added **Anti-Bot & Rate-Limit Diagnostics** (detecting eBay 429 throttles & CAPTCHA challenges).
* Added **In-App Analyst Operations Guide & Tooltips** with 💡 Help & Guide top bar button.
* Expanded test suite to **12 automated regression tests passing 100% in <0.5s**.
