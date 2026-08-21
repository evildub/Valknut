# Valknut Brand Intelligence — Analyst Quickstart Guide

**Version:** Standalone Windows Portable Application  
**Author:** Jerry Seidenstucker  
**Intended For:** Brand Protection Analysts, Investigators, and IP Enforcement Teams  

---

## ⚡ Zero Installation Required
This package is fully portable and self-contained. **No Python installation, administrator rights, or external browser drivers are required.**

To launch the tool, double-click:
```
ValknutBrandIntelligence.exe
```

---

## 🔍 Core Features & Workflows

### 1. Multi-Marketplace Catalog & Store Harvesting
- **Supported Marketplaces:** eBay, AliExpress, Temu, Wish, Printerval, Redbubble, Mercado Libre.
- **Search Modes:**
  - **Full Marketplace Sweeps:** Leave the Stores box on `Global Search` or blank to sweep across all public platform listings.
  - **Store/Seller Targeting:** Enter one or more specific store URLs or seller handles (one per line) to scrape targeted seller storefronts.

### 2. Brand Library & Portfolio Presets
- **Brand Tree:** Manage 3-tier brand hierarchies: Parent Brand → Sub-Brand / Division → Model.
- **Brand Targeting States:**
  - `🎯 Target` (Green): Included in sweeps and auto-generates keyword search jobs.
  - `🚫 Exclude` (Red): Automatically excluded using marketplace Boolean exclusion operators.
  - `⚪ Neutral` (White): Saved in library but skipped during scans.
- **1-Click Portfolio Sweeps:** Select a preset (e.g. *General Motors Full Lineup*, *Toyota Automotive*) and click **`⚡ 1-Click Sweep`** to queue all associated brands automatically.
- **Clean Brand Sweeps:** Click **`🎯 Clean Brand Sweep`** to queue single-term searches without complex term conjunctions.

### 3. Adhoc Batch URL & Excel Importer (`📂 Import URLs / Excel`)
When clients send adhoc lists of URLs or investigation spreadsheets:
1. Click **`📂 Import URLs / Excel`** in the top navigation bar.
2. **Direct Paste:** Paste 5, 10, or 100+ raw listing URLs from any supported marketplace.
3. **Excel File Import:** Click **`Browse Excel (.xlsx)`** to import spreadsheets. Valknut auto-detects listing URL columns.
4. Click **`⚡ Import & Scrape Listings`** to extract titles, sellers, prices, and thumbnails automatically into your active investigation table.

### 4. Seller & Creator Enrichment (`⚡ Enrich Sellers`)
- For POD (Print-on-Demand) and e-commerce platforms like **Printerval**, **AliExpress**, **Wish**, and **Temu**, search cards often display default or generic creator placeholders.
- Click **`⚡ Enrich Sellers`** (or right-click selected rows) to run deep seller/shop resolution. 
- Results are cached locally in `%LOCALAPPDATA%` for **0ms instant re-resolution** on subsequent sweeps.

### 5. Threat Intelligence & Seller Deduplication
- The right-side **Threat Intel** panel tracks:
  - **Active Threat Actors:** Total unique infringing sellers identified.
  - **Top High-Volume Repeat Offenders:** Ranked list of sellers with the highest listing counts.
  - **Total Potential Counterfeit Volume:** Aggregated listing catalog value.

### 6. Excel Dossier Export (`💾 Export to Excel`)
- Generates standardized brand protection reports formatted for platform notice-and-takedown actions (A2C2 / MarkMonitor compatible).
- Features:
  - Multi-tab organization per brand.
  - Formatted columns: Title, URL, High-Res Thumbnail Link, Item ID, Marketplace, Seller/Merchant, Product Category, and Price.
  - Auto-generated **Executive Summary** sheet with high-risk seller rollups.

---

## 🛠️ Configuration & Persistence
- All brand library settings, exclusions, presets, and threat metrics are saved automatically to `data.json`.
- To share your brand configuration with another analyst, simply share a copy of `data.json`.

---

## 🔒 Security & Privacy
- Runs 100% locally in user space.
- Zero telemetry, zero third-party cloud connections.
- Outbound network calls use encrypted HTTPS (Port 443) strictly to target marketplace endpoints.
- See `SECURITY_AUDIT.md` for full enterprise compliance documentation.
