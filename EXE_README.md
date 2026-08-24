# Apollo Brand Intelligence — Analyst Quickstart Guide

**Version:** v1.5.0 Standalone Windows Portable Application  
**Author:** Jerry Seidenstucker  
**Intended For:** Brand Protection Analysts, Investigators, and IP Enforcement Teams  

---

## ⚡ Zero Installation Required
This package is fully portable and self-contained. **No Python installation, administrator rights, or external browser drivers are required.**

To launch the tool, double-click:
```
Apollo Brand Intelligence.exe
```

---

## 🔍 Core Modules & Capabilities

### 1. Multi-Marketplace Ecosystems
- **Supported Marketplaces:**
  - **🛒 eBay (Global)**: High-speed scraping + optional REST API mode.
  - **👗 Vinted (10 Regions)**: UK, France, Germany, Spain, Italy, Poland, US, Netherlands, Belgium, All Locales.
  - **🛍 Mercado Libre (7 Regions)**: Mexico, Brazil, Argentina, Colombia, Chile, Peru, All Latin America.
  - **🌐 AliExpress**, **🌠 Wish**, **🟠 Temu**, **🎨 Redbubble**, **👕 Printerval**.
- **Search Modes:**
  - **Global sweeps**: Leave the Stores box blank or on `Global Search`.
  - **Storefront Targeting**: Enter one or more storefront handles or URLs (one per line).

### 2. Visual Threat Catalog & Reverse Search (`F2`)
- **64-Bit DCT Perceptual Hashing**: Detects identical replica stock photos across all platforms regardless of watermarks or slight cropping.
- **Red Catalog**: Known counterfeit imagery for automated visual matching.
- **Green Catalog**: Authentic manufacturer packaging to hide benign listings from queues.
- **Right-Click Dredge**: Right-click any row to sweep by photo across platforms and specific regional locales.

### 3. Searchable Analyst Field Guide (`F1`)
- Press **`F1`** anywhere or open via **`⚙️ Settings ▾`** for real-time searchable documentation on:
  - **Threat Signals**: `NWT`, `NWOT`, `BNIB`, `3PL Hubs`, `Burner Handles`, `pHash`, `VeRO`, `BPP`.
  - **Search Syntax**: Live filtering with `+inclusion` and `-exclusion` modifiers.
  - **Tool Directory**: Quick reference workflows for all Apollo sub-modules.

### 4. Threat Intelligence & Origin Resolution
- **Cross-Border Discrepancy Detection**: Compares seller registration country against dispatch location to flag domestic 3PL drop-shipping hubs.
- **Connected Seller Network Hunter**: Uncovers syndicate sister storefronts sharing business registrations, contact info, or master stock photos.

### 5. Standardized Excel Dossier Export
- Generates formatted spreadsheets ready for notice-and-takedown platform submissions.
- Includes multi-tab brand segregation and executive summary threat rollups.

---

## 🛠️ Configuration & Persistence
- All brand library settings, exclusions, presets, and threat metrics are saved automatically to `data.json`.
- Back up or share `data.json` to transfer configurations across analyst workstations.
