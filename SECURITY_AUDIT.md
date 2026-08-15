# Internal Application Security & Architecture Overview
**Application Name:** eBay Enforcement Harvester  
**Lead Author & Creator:** Jerry Seidenstucker  
**Copyright:** © 2026 Jerry Seidenstucker. All Rights Reserved.  
**Intended Use:** Brand Protection, Trademark Compliance, and Store Listing Aggregation  
**Runtime Architecture:** Python 3.12+ (Packaged as Standalone Windows Executable via PyInstaller)  

---

## 1. Security & Compliance Summary

| Category | Status / Policy | Detail |
| :--- | :--- | :--- |
| **Administrative Privileges** | 🟢 **Zero Required** | Runs entirely in standard user-space (`Standard User`). Never prompts for UAC elevation or writes to `C:\Windows` or `C:\Program Files`. |
| **Registry Access** | 🟢 **Zero Writes** | Does not modify Windows Registry keys or system policies. |
| **Telemetry / Tracking** | 🟢 **Zero External Telemetry** | No external analytics, crash reporters, or third-party servers are contacted. All network calls are strictly restricted to eBay endpoints. |
| **Network Protocol** | 🟢 **Encrypted HTTPS Only** | All outbound traffic uses TLS 1.2 / TLS 1.3 over standard port `443`. |
| **Data Storage & Privacy** | 🟢 **100% Local Storage** | Scraped listings, brand registries, and exported `.xlsx` / `.txt` files remain strictly on the local filesystem. |
| **Execution Model** | 🟢 **Fixed Directory (`--onedir`)** | Operates from a designated application folder, avoiding blocked temp execution directories often flagged by corporate EDR (CrowdStrike / Defender ATP). |

---

## 2. Network Destination Whitelist

This application strictly communicates with the following official public endpoints:

1. **`https://www.ebay.com/*`** — Public search result and store catalog pages.
2. **`https://api.ebay.com/*`** — Official eBay Developer Browse API (when optional API keys are provided).
3. **`https://i.ebayimg.com/*`** — eBay official CDN for product image thumbnail previews.

> [!NOTE]
> No incoming network ports are opened. No peer-to-peer connections or socket listeners exist.

---

## 3. Data Flow & Cryptographic Integrity

```mermaid
graph LR
    User[User Desktop / Work PC] -->|HTTPS Requests| eBay[Official eBay Endpoints]
    eBay -->|Encrypted HTML / JSON| User
    User -->|Saved Locally| Excel[Local Excel Reports (.xlsx)]
    User -->|Saved Locally| Config[Local Config (data.json)]
```

* **Credentials:** If eBay Developer API keys (`App ID`, `Cert ID`) are configured, they are saved locally in `data.json` inside the application directory and never transmitted to any third party.
* **Integrity Verification:** A SHA-256 hash of `eBayHarvester.exe` can be generated at build time via PowerShell:
  ```powershell
  Get-FileHash -Algorithm SHA256 dist\eBayHarvester\eBayHarvester.exe
  ```

---

## 4. Why This Architecture is Safe for Corporate Workstations

1. **Self-Contained Portable App:** The application requires no elevated installer or system-level driver dependencies.
2. **Deterministic Behavior:** The full source code is inspectable plain-text Python (`main.py`, `scraper.py`, `api_client.py`, `exporter.py`, `data_store.py`).
3. **No Background Daemons:** The application only runs when actively opened by the user, and terminates all memory footprints immediately upon closing.
