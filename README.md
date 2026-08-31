# Apollo Brand Intelligence — Enterprise Enforcement Suite

[![Version](https://img.shields.io/badge/Version-1.7.0-blue.svg?style=flat-square)](https://github.com/evildub/Valknut/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20(x64)-0078D6.svg?style=flat-square)](https://github.com/evildub/Valknut)
[![Compliance](https://img.shields.io/badge/Genesis%20Compliance-100%25%20Verified-00C853.svg?style=flat-square)](https://github.com/evildub/Valknut)
[![Security](https://img.shields.io/badge/Security-Local%20Execution%20%7C%20Zero%20Telemetry-38BDF8.svg?style=flat-square)](https://github.com/evildub/Valknut)

**Apollo Brand Intelligence** is a specialized, high-velocity intellectual property protection and anti-counterfeit discovery platform engineered for brand security analysts, legal enforcement teams, and investigative operations.

---

## 🌟 Core Capabilities

### 1. Multi-Platform Market Discovery
Automates high-precision discovery across primary e-commerce marketplaces:
- **Social Commerce & Viral Marketplaces:** Deep inspection, store sweeps, and high-velocity adhoc batch PDP extraction engine for **TikTok Shop** (`shop.tiktok.com`).
- **eBay Ecosystem:** Comprehensive global domain sweeps (`ebay.com`, `ebay.ca`, `ebay.co.uk`, `ebay.de`, `ebay.com.au`, `ebay.fr`, `ebay.it`, `ebay.es`).
- **Global & Asian Marketplaces:** Deep inspection engines for **AliExpress**, **Temu**, **Wish**, **Mercado Libre (LATAM)**, and **Vinted (EU/UK/US)**.
- **Print-on-Demand (POD):** Automated infringement detection across **Redbubble** and **Printerval**.

### 2. Reverse Visual Dredge & Asset Protection
- **64-bit DCT pHash Fingerprinting:** Detects exact photographic asset theft and digital clone listings in seconds using multithreaded parallel visual hashing.
- **Automated Merchant Intel Enrichment:** Instantly extracts registered seller handles, live prices, item locations, and registered origin flags directly from discovered visual clones.

### 3. Cross-Border Threat Intelligence & 3PL Detection
- **Domestic vs. Drop-Ship Heuristics:** Identifies cross-border shell merchants, Asian manufacturing syndicates (China, India, Pakistan, Vietnam), and domestic 3PL fulfillment hubs.
- **Automated Threat Badging:** Flags suspect listings with tactical threat indicators (`🚨 Drop-Ship Hub`, `🇨🇳 Cross-Border Direct`, `🛡️ Dealership Verified`).

### 4. Genesis Platform & A2C2 Export Compliance
- **18-Column Standard Schema:** Formatted to exact enterprise import specifications with normalized platform domains (`ebay.com`, `ebay.ca`, etc.) in Column H.
- **A2C2 Legal Dossier Generator:** Exports audit-ready, structured compliance reports ready for legal submission and platform takedown notices.

---

## 🚀 Quick Start (Analyst Deployment)

### Standalone Executable (Recommended)
1. Download the latest release from [Releases](https://github.com/evildub/Valknut/releases/latest).
2. Extract `Apollo-Brand-Intelligence-v1.6.0-win64.zip`.
3. Launch `Apollo Brand Intelligence.exe`.

### Python Developer Environment
```bash
# Clone the repository
git clone https://github.com/evildub/Valknut.git
cd Valknut

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 🛡️ Architecture & Security Posture

- **100% Local Execution:** All database queries, image hashes, and report generation run strictly on local analyst hardware. Zero third-party telemetry or cloud data leakage.
- **Persistent Anti-Bot Session Engine:** Uses dedicated local browser profiles (`data/browser_session`) with synchronous interactive CAPTCHA recovery to prevent IP throttling during large store audits.
- **Thread-Safe Queue Execution:** Supports live pausing, stop controls, and real-time result streaming.

---

## 📊 Technical Architecture

| Component | Module | Responsibility |
| :--- | :--- | :--- |
| **Orchestrator** | `main.py` | GUI, multi-monitor window management, theme engine, queue runner |
| **eBay Engine** | `scraper.py` | URL-first seller extraction, rate-limit recovery, Playwright driver |
| **Visual Dredge** | `visual_harvester.py` | Multithreaded DCT pHash image clone detection |
| **Catalog DB** | `visual_catalog.py` | Reference asset fingerprint repository |
| **Marketplace Scrapers** | `*_scraper.py` | Scraper modules for AliExpress, Temu, Wish, MercadoLibre, Vinted, POD |
| **Threat Engine** | `data_store.py` | JSON configuration, whitelist registry, 3PL threat heuristics |
| **Compliance Exporter** | `exporter.py` | Genesis single/multi-locale & A2C2 Excel dossier formatting |
| **Batch Importer** | `batch_importer.py` | Ad-hoc URL list ingestion and single-item enrichment |

---

## 🔒 Confidentiality & License
*Proprietary Brand Protection Tooling — For Authorized Corporate Enforcement & Legal Investigation Use Only.*
