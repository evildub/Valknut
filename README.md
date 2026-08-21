# eBay Enforcement Harvester — Setup Guide

## Requirements
- Windows 10 or 11
- Python 3.10 or later  
  Download from: https://www.python.org/downloads/
  ⚠️ During install, check "Add Python to PATH"

---

## First-Time Setup

1. **Download / copy** the `ebay_tool` folder to somewhere on your PC
   (e.g. `C:\Users\YourName\Documents\ebay_tool`)

2. **Open a Command Prompt** in that folder
   - Hold Shift + right-click the folder → "Open PowerShell window here"
   - Or open CMD and type: `cd C:\Users\YourName\Documents\ebay_tool`

3. **Install dependencies** (one time only):
   ```
   pip install -r requirements.txt
   ```

4. **Run the tool**:
   ```
   python main.py
   ```

---

## Daily Use

Just double-click `run.bat` (or run `python main.py` from Command Prompt).

---

## How to Use

### 1. Enter a Store URL
Paste the eBay store URL into the Store field.
- e.g. `https://www.ebay.com/str/somestorename`
- Or just the seller name: `somestorename`

### 2. Select a Brand
- Pick from the Brand dropdown (your library is pre-loaded with Toyota, GM, Subaru, Hyundai/Kia)
- The Include Terms box auto-fills with the brand + all its models
- Edit freely — one term per line

### 3. Check Exclusions
- The Exclusion Terms panel shows all saved exclusion terms as checkboxes
- Check the ones you want active for this search
- Add new ones anytime with the text box

### 4. Add to Queue
- Click "Add to Queue" — this saves the store + brand + terms as one job
- Repeat for other brands (Subaru, Camry-only search, etc.)
- You can queue multiple stores too

### 5. Run Queue
- Click "Run Queue" — the tool works through each job sequentially
- Results appear in the right panel as they come in
- Double-click any row to open the listing in your browser

### 6. Export to Excel
- Click "Export to Excel"
- Each brand gets its own tab
- Columns match the required format (A=Title, B=URL, C=Thumbnail, E=Item ID, H=Marketplace, J=Seller, M=Brand)
- Price is in column N

---

## Brand Library Management

- **Parent** = top-level brand (Toyota, General Motors)
- **Sub** = sub-brand (Lexus under Toyota, Chevrolet under GM)
- **Model** = specific model (Camry, Corvette)

When you select a brand to search, all its models auto-populate as include terms.
You can always edit the include terms manually before adding to queue.

---

## API Mode (Optional)

If you have an eBay Developer API key:
1. Check "Use eBay API" in the top bar
2. Enter your App ID (Client ID) and click Save
3. API mode is faster, more reliable, and won't get blocked

Without an API key, the tool uses web scraping (slightly slower, may occasionally
hit rate limits — just wait a minute and retry).

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | Main application |
| `scraper.py` | Web scraping engine |
| `api_client.py` | eBay API client |
| `exporter.py` | Excel export |
| `data_store.py` | Saves your brands/exclusions |
| `data.json` | Your saved data (brands, exclusions, settings) |
| `requirements.txt` | Python package list |

Your brand library and exclusion terms are saved in `data.json` automatically.
Back this file up if you want to preserve your configuration.

---

## Sharing with Other Analysts

To share the tool:
1. Zip the entire `ebay_tool` folder
2. The other analyst installs Python and runs `pip install -r requirements.txt`
3. They get their own `data.json` with your default brand library
4. To share a brand library: copy your `data.json` to their folder
