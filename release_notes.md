# Apollo Brand Intelligence v1.5.0 — Multi-Platform Vinted & Mercado Libre Enterprise Suite

## 👗 Vinted Multi-Region Harvesting & P2P Threat Heuristics
- **10 Regional Marketplaces**: Full direct-harvesting support across:
  - 🇬🇧 United Kingdom (`vinted.co.uk`)
  - 🇫🇷 France (`vinted.fr`)
  - 🇩🇪 Germany (`vinted.de`)
  - 🇪🇸 Spain (`vinted.es`)
  - 🇮🇹 Italy (`vinted.it`)
  - 🇵🇱 Poland (`vinted.pl`)
  - 🇺🇸 United States (`vinted.com`)
  - 🇳🇱 Netherlands (`vinted.nl`)
  - 🇧🇪 Belgium (`vinted.be`)
  - 🌍 Global Cross-Border Sweeps (`All Locales`)
- **Automated Cloudflare Evasion & Session Sync**: 
  - Integrated `curl_cffi` TLS client impersonation with strict domain cookie filtering.
  - Dedicated `👗 Vinted Connect` 1-click human browser verification helper for persistent session synchronization.
- **Deep Scan Pagination**: Configurable scan depth presets: 1 Page (96), 2 Pages (192), 4 Pages (384), 8 Pages (768).
- **Specialized Threat Intelligence Flags**:
  - `🚨 NWT Counterfeit Risk`: Algorithmic detection of luxury streetwear/apparel listed "New With Tags" 50%+ below retail by zero-feedback accounts.
  - `🚩 Suspicious Burner Handle`: Identifies machine-generated and disposable storefront accounts used by replica syndicates.
  - **Zero-Feedback Loop Detection**: Flags newly minted unverified seller profiles.

---

## 🌎 Mercado Libre Latin America Ecosystem
- **Multi-Country Direct Harvesting**: Full support for single-region and Latin America multi-sweeps across:
  - 🇲🇽 **Mexico (MLM)**
  - 🇧🇷 **Brazil (MLB)**
  - 🇦🇷 **Argentina (MLA)**
  - 🇨🇴 **Colombia (MCO)**
  - 🇨🇱 **Chile (MLC)**
  - 🇵🇪 **Peru (MPE)**
  - 🌎 **All Latin America (Regional Cross-Border)**
- **Deep Buy Box & Catalog Disentanglement**: Advanced `/p/` catalog DOM parsing extracts Buy Box winners, specific winner IDs (`wid=`), and competing catalog merchants.
- **Real-Time Storefront & Origin Enrichment**: Multi-line parser with active React hydration polling extracts verified seller handles, dispatch location (e.g. USA, Mexico), and MercadoLíder Platinum badges.
- **Connected Seller Network Hunter**: Maps syndicate sister accounts across *Publicaciones del vendedor*, *Quienes vieron este producto también compraron*, and competing buy box listings.

---

## 🖼️ Visual Threat Catalog & Reverse Visual Dredge
- **64-Bit DCT Perceptual Hashing (`pHash`)**: Mathematical image fingerprinting invariant to compression, watermarks, resizing, and subtle cropping (Hamming distance $\le 6$).
- **Multi-Image Variant Clustering**:
  - 🔴 **Red Catalog (Known Counterfeits)**: Clusters replica factory promotional photography across parallel worker threads.
  - 🟢 **Green Catalog (Verified Benign Packaging)**: Whitelists authentic distributor stock photography to suppress false positives.
- **Cross-Platform Reverse Visual Dredge**: Right-click any table row to sweep by image across the active platform or directly target specific Vinted / MeLi regions.

---

## 📚 Searchable Analyst Field Guide & Threat Glossary (`F1`)
- **Interactive In-App Documentation**: Press `F1` anywhere or access via `⚙️ Settings ▾`.
- **Tab 1: 🚨 Threat Signals & Acronyms**: Detailed definitions for `NWT`, `NWOT`, `BNIB`, `3PL Forwarding Hubs`, `Burner Handles`, `pHash`, `VeRO`, and `BPP`.
- **Tab 2: 🔍 Search Syntax & Live Filtering**: Guidance for `+term` (mandatory inclusion), `-term` (exclusion), multi-token query expressions, and column targeting.
- **Tab 3: 🛠️ Apollo Tools & Modal Guide**: End-to-end workflows for all platform reconnaissance modules.

---

## ⚙️ Unified Settings Menu & UI Optimization
- **Streamlined Toolbar**: Consolidated settings into a unified `⚙️ Settings ▾` menubutton.
- **Dynamic 11-Column Visibility**: Toggle checkboxes to show/hide any table column (`Brand`, `Product Type`, `Title`, `Item ID`, `Price`, `Seller`, `Origin`, `Threat Intel`, `Location`, `Thumbnail`, `URL`).
- **Analyst Micro-Hints**: Toggleable 450ms hover tooltips across all inputs and controls.
- **Expanded High-Risk Filter**: The `🚨 High-Risk` checkbox now isolates 3PL forwarding hubs, Vinted replica candidates, burner handles, and visual clones in 1 click.
- **Zero-Lag UI Performance**: Decoupled layout event loops and stabilized Windows DWM titlebar rendering.