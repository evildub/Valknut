import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import re
import io
import time
import threading
import urllib.request
from datetime import datetime
import webbrowser
import winsound
from PIL import Image, ImageTk
import ctypes

from scraper import EbayScraper
from aliexpress_scraper import AliExpressScraper
from wish_scraper import WishScraper
from temu_scraper import TemuScraper
from mercadolibre_scraper import MercadoLibreScraper
from redbubble_scraper import RedbubbleScraper
from printerval_scraper import PrintervalScraper
from api_client import EbayAPIClient
from exporter import ExcelExporter
from data_store import DataStore
import batch_importer

# ── Color Palette Definitions ─────────────────────────────────────────────────
THEMES = {
    "midnight": {
        "name": "🌌 Midnight Slate",
        "bg": "#1e1e2e",
        "panel": "#2a2a3e",
        "accent": "#7c6af7",
        "accent2": "#5a9fd4",
        "success": "#50fa7b",
        "warning": "#f1fa8c",
        "danger": "#ff5555",
        "text": "#f8f8f2",
        "subtext": "#a6adc8",
        "entry_bg": "#313145",
        "border": "#44475a",
        "btn_normal_bg": "#44475a",
        "btn_normal_fg": "#f8f8f2",
        "select_bg": "#7c6af7",
        "select_fg": "#ffffff",
    },
    "catppuccin": {
        "name": "☕ Catppuccin Mocha",
        "bg": "#1e1e2e",
        "panel": "#181825",
        "accent": "#cba6f7",
        "accent2": "#89b4fa",
        "success": "#a6e3a1",
        "warning": "#f9e2af",
        "danger": "#f38ba8",
        "text": "#cdd6f4",
        "subtext": "#9399b2",
        "entry_bg": "#313244",
        "border": "#45475a",
        "btn_normal_bg": "#313244",
        "btn_normal_fg": "#cdd6f4",
        "select_bg": "#cba6f7",
        "select_fg": "#11111b",
    },
    "synthwave": {
        "name": "🎮 Retro Synthwave 80s",
        "hidden": True,
        "bg": "#1a0b2e",
        "panel": "#26123d",
        "accent": "#ff007f",
        "accent2": "#00f0ff",
        "success": "#05ffa1",
        "warning": "#ffe600",
        "danger": "#ff2a6d",
        "text": "#fefefe",
        "subtext": "#b49bcb",
        "entry_bg": "#2d1647",
        "border": "#4b2373",
        "btn_normal_bg": "#2d1647",
        "btn_normal_fg": "#00f0ff",
        "select_bg": "#ff007f",
        "select_fg": "#ffffff",
    },
    "cyberpunk": {
        "name": "⚡ Cyberpunk 2077",
        "bg": "#08080a",
        "panel": "#121218",
        "accent": "#fee500",
        "accent2": "#00f0ff",
        "success": "#00ff9f",
        "warning": "#ff9900",
        "danger": "#ff003c",
        "text": "#ffffff",
        "subtext": "#71717a",
        "entry_bg": "#1a1a24",
        "border": "#323242",
        "btn_normal_bg": "#1a1a24",
        "btn_normal_fg": "#00f0ff",
        "select_bg": "#fee500",
        "select_fg": "#000000",
    },
    "matrix": {
        "name": "💻 Matrix CRT",
        "bg": "#030804",
        "panel": "#071409",
        "accent": "#00ff41",
        "accent2": "#008f11",
        "success": "#00ff41",
        "warning": "#a7ff00",
        "danger": "#ff0033",
        "text": "#00ff41",
        "subtext": "#008f11",
        "entry_bg": "#0a1c0d",
        "border": "#00590c",
        "btn_normal_bg": "#0a1c0d",
        "btn_normal_fg": "#00ff41",
        "select_bg": "#00ff41",
        "select_fg": "#030804",
    },
    "matcha": {
        "name": "🍵 Matcha Zen",
        "bg": "#1b2421",
        "panel": "#24302c",
        "accent": "#70a980",
        "accent2": "#95d5b2",
        "success": "#52b788",
        "warning": "#d8b168",
        "danger": "#e76f51",
        "text": "#e9f5ed",
        "subtext": "#8fa89b",
        "entry_bg": "#2c3b36",
        "border": "#3d514a",
        "btn_normal_bg": "#2c3b36",
        "btn_normal_fg": "#e9f5ed",
        "select_bg": "#70a980",
        "select_fg": "#1b2421",
    },
    "nyancat": {
        "name": "🌈 Nyan Cosmic RGB",
        "bg": "#0d0f2b",
        "panel": "#161942",
        "accent": "#ff3399",
        "accent2": "#00e5ff",
        "success": "#39ff14",
        "warning": "#ffe600",
        "danger": "#ff0055",
        "text": "#ffffff",
        "subtext": "#99a8ff",
        "entry_bg": "#202456",
        "border": "#3d448c",
        "btn_normal_bg": "#202456",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#ff3399",
        "select_fg": "#ffffff",
    },
    "pastel": {
        "name": "🌸 Sakura Blossom",
        "bg": "#23181a",
        "panel": "#2d1f23",
        "accent": "#f48fb1",
        "accent2": "#ffd54f",
        "success": "#66bb6a",
        "warning": "#ffd54f",
        "danger": "#e57373",
        "text": "#fff0f5",
        "subtext": "#9ec39a",
        "entry_bg": "#38252b",
        "border": "#c89b7b",
        "btn_normal_bg": "#38252b",
        "btn_normal_fg": "#ffd54f",
        "select_bg": "#f48fb1",
        "select_fg": "#23181a",
    },
    "ocean": {
        "name": "🌊 Deep Ocean",
        "bg": "#0f172a",
        "panel": "#1e293b",
        "accent": "#38bdf8",
        "accent2": "#0284c7",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#f87171",
        "text": "#f8fafc",
        "subtext": "#94a3b8",
        "entry_bg": "#334155",
        "border": "#475569",
        "btn_normal_bg": "#334155",
        "btn_normal_fg": "#f8fafc",
        "select_bg": "#0284c7",
        "select_fg": "#ffffff",
    },
    "obsidian": {
        "name": "🖤 Obsidian Cyber",
        "bg": "#121214",
        "panel": "#1e1e24",
        "accent": "#10b981",
        "accent2": "#059669",
        "success": "#22c55e",
        "warning": "#eab308",
        "danger": "#ef4444",
        "text": "#f4f4f5",
        "subtext": "#a1a1aa",
        "entry_bg": "#272730",
        "border": "#3f3f46",
        "btn_normal_bg": "#272730",
        "btn_normal_fg": "#f4f4f5",
        "select_bg": "#10b981",
        "select_fg": "#ffffff",
    },
    "arctic": {
        "name": "❄️ Nordic Arctic",
        "bg": "#242933",
        "panel": "#2e3440",
        "accent": "#88c0d0",
        "accent2": "#81a1c1",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "danger": "#bf616a",
        "text": "#eceff4",
        "subtext": "#d8dee9",
        "entry_bg": "#3b4252",
        "border": "#4c566a",
        "btn_normal_bg": "#3b4252",
        "btn_normal_fg": "#eceff4",
        "select_bg": "#81a1c1",
        "select_fg": "#2e3440",
    },
    # ── Client-Inspired Corporate Themes ──────────────────────────────────────
    "lego": {
        "name": "🧱 LEGO Classic",
        "bg": "#1c1d22",
        "panel": "#252730",
        "accent": "#ffd500",
        "accent2": "#ffea75",
        "success": "#00a651",
        "warning": "#ff9900",
        "danger": "#d11013",
        "text": "#ffffff",
        "subtext": "#ffd500",
        "entry_bg": "#2e313d",
        "border": "#3d4252",
        "btn_normal_bg": "#2e313d",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#d11013",
        "select_fg": "#ffffff",
    },
    "nfl": {
        "name": "🏈 NFL Gridiron",
        "bg": "#0a1128",
        "panel": "#121e3d",
        "accent": "#3a86ff",
        "accent2": "#006494",
        "success": "#2a9d8f",
        "warning": "#ffb703",
        "danger": "#d50a0a",
        "text": "#f8f9fa",
        "subtext": "#8da9c4",
        "entry_bg": "#1a274d",
        "border": "#25365e",
        "btn_normal_bg": "#1a274d",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#d50a0a",
        "select_fg": "#ffffff",
    },
    "black_decker": {
        "name": "🔨 Black & Decker",
        "bg": "#141414",
        "panel": "#1f1f1f",
        "accent": "#ff6f00",
        "accent2": "#ffa040",
        "success": "#00e676",
        "warning": "#ffab00",
        "danger": "#ff1744",
        "text": "#ffffff",
        "subtext": "#9e9e9e",
        "entry_bg": "#292929",
        "border": "#3d3d3d",
        "btn_normal_bg": "#292929",
        "btn_normal_fg": "#ff6f00",
        "select_bg": "#ff6f00",
        "select_fg": "#000000",
    },
    "taylor_swift": {
        "name": "✨ Taylor Swift Eras",
        "bg": "#181124",
        "panel": "#221834",
        "accent": "#c084fc",
        "accent2": "#f472b6",
        "success": "#a7f3d0",
        "warning": "#fde047",
        "danger": "#f43f5e",
        "text": "#fdf4ff",
        "subtext": "#c4b5fd",
        "entry_bg": "#2e2047",
        "border": "#43325e",
        "btn_normal_bg": "#2e2047",
        "btn_normal_fg": "#fdf4ff",
        "select_bg": "#c084fc",
        "select_fg": "#181124",
    },
    "sprayground": {
        "name": "🎒 Sprayground Shark",
        "bg": "#111111",
        "panel": "#1a1a1a",
        "accent": "#ff0033",
        "accent2": "#ffd600",
        "success": "#00f59b",
        "warning": "#ffd600",
        "danger": "#ff0033",
        "text": "#ffffff",
        "subtext": "#ffcc00",
        "entry_bg": "#242424",
        "border": "#363636",
        "btn_normal_bg": "#242424",
        "btn_normal_fg": "#ffd600",
        "select_bg": "#ff0033",
        "select_fg": "#ffffff",
    },
    # ── Automotive & Motorsport Legends ───────────────────────────────────────
    "toyota_gr": {
        "name": "🏁 Toyota GR",
        "bg": "#151619",
        "panel": "#1e2025",
        "accent": "#eb0a1e",
        "accent2": "#ff3344",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#eb0a1e",
        "text": "#ffffff",
        "subtext": "#9ca3af",
        "entry_bg": "#282a30",
        "border": "#383c47",
        "btn_normal_bg": "#282a30",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#eb0a1e",
        "select_fg": "#ffffff",
    },
    "subaru_wrc": {
        "name": "⭐ Subaru Rally",
        "bg": "#0c1322",
        "panel": "#141e33",
        "accent": "#ffd100",
        "accent2": "#0055b8",
        "success": "#10b981",
        "warning": "#ffd100",
        "danger": "#ef4444",
        "text": "#f8fafc",
        "subtext": "#93c5fd",
        "entry_bg": "#1a2744",
        "border": "#24375e",
        "btn_normal_bg": "#1a2744",
        "btn_normal_fg": "#ffd100",
        "select_bg": "#0055b8",
        "select_fg": "#ffffff",
    },
    "gm_heritage": {
        "name": "💎 GM & ACDelco",
        "bg": "#0d1726",
        "panel": "#152238",
        "accent": "#0066cc",
        "accent2": "#ffb81c",
        "success": "#00c853",
        "warning": "#ffb81c",
        "danger": "#d50000",
        "text": "#ffffff",
        "subtext": "#8cb8ff",
        "entry_bg": "#1d2c47",
        "border": "#253757",
        "btn_normal_bg": "#1d2c47",
        "btn_normal_fg": "#ffb81c",
        "select_bg": "#0066cc",
        "select_fg": "#ffffff",
    },
    "eleanor": {
        "name": "🐎 1967 Shelby GT500",
        "hidden": True,
        "bg": "#181a1c",
        "panel": "#222528",
        "accent": "#cbd5e1",
        "accent2": "#94a3b8",
        "success": "#00e676",
        "warning": "#ffb703",
        "danger": "#e50914",
        "text": "#f8fafc",
        "subtext": "#94a3b8",
        "entry_bg": "#2b2f33",
        "border": "#43494f",
        "btn_normal_bg": "#2b2f33",
        "btn_normal_fg": "#f8fafc",
        "select_bg": "#e50914",
        "select_fg": "#ffffff",
    },
    "kia_gt": {
        "name": "⚡ Kia GT & Stinger",
        "bg": "#171216",
        "panel": "#241b22",
        "accent": "#e60026",
        "accent2": "#ff4d6a",
        "success": "#00e676",
        "warning": "#ffc107",
        "danger": "#e60026",
        "text": "#ffffff",
        "subtext": "#d19ca8",
        "entry_bg": "#2e232c",
        "border": "#3d2d3a",
        "btn_normal_bg": "#2e232c",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#e60026",
        "select_fg": "#ffffff",
    },
    "ford_racing": {
        "name": "🔵 Ford Performance",
        "bg": "#0a1526",
        "panel": "#102038",
        "accent": "#00a3e0",
        "accent2": "#0050b3",
        "success": "#00e676",
        "warning": "#ffc107",
        "danger": "#ff3d00",
        "text": "#f0f8ff",
        "subtext": "#82b1ff",
        "entry_bg": "#182e4d",
        "border": "#22406b",
        "btn_normal_bg": "#182e4d",
        "btn_normal_fg": "#00a3e0",
        "select_bg": "#0050b3",
        "select_fg": "#ffffff",
    },
    "hyundai_n": {
        "name": "⚡ Hyundai N-Line",
        "bg": "#14171d",
        "panel": "#1b2028",
        "accent": "#90caf9",
        "accent2": "#e53935",
        "success": "#00e676",
        "warning": "#ffb74d",
        "danger": "#e53935",
        "text": "#ffffff",
        "subtext": "#90caf9",
        "entry_bg": "#252b36",
        "border": "#2d3645",
        "btn_normal_bg": "#252b36",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#e53935",
        "select_fg": "#ffffff",
    },
    "jeep_trail": {
        "name": "🚙 Jeep Trail Rated",
        "bg": "#192116",
        "panel": "#232d1e",
        "accent": "#f77f00",
        "accent2": "#fcbf49",
        "success": "#588157",
        "warning": "#f77f00",
        "danger": "#d62828",
        "text": "#fefae0",
        "subtext": "#a3b18a",
        "entry_bg": "#2e3b28",
        "border": "#36452e",
        "btn_normal_bg": "#2e3b28",
        "btn_normal_fg": "#fefae0",
        "select_bg": "#f77f00",
        "select_fg": "#192116",
    },
    "dodge_hellcat": {
        "name": "🔥 Dodge SRT Hellcat",
        "bg": "#161219",
        "panel": "#211b26",
        "accent": "#d90429",
        "accent2": "#8338ec",
        "success": "#06d6a0",
        "warning": "#ffb703",
        "danger": "#d90429",
        "text": "#ffffff",
        "subtext": "#c77dff",
        "entry_bg": "#2d2433",
        "border": "#3d2b38",
        "btn_normal_bg": "#2d2433",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#d90429",
        "select_fg": "#ffffff",
    },
    "bmw_m": {
        "name": "🏁 BMW Motorsport",
        "bg": "#0f141c",
        "panel": "#161e29",
        "accent": "#0099ff",
        "accent2": "#e0001b",
        "success": "#00cc66",
        "warning": "#ffcc00",
        "danger": "#e0001b",
        "text": "#ffffff",
        "subtext": "#80c1ff",
        "entry_bg": "#1f2937",
        "border": "#26354a",
        "btn_normal_bg": "#1f2937",
        "btn_normal_fg": "#0099ff",
        "select_bg": "#0099ff",
        "select_fg": "#ffffff",
    },
    "continental": {
        "name": "🪙 The Continental",
        "hidden": True,
        "bg": "#0A0B0E",
        "panel": "#12141A",
        "entry_bg": "#060709",
        "accent": "#D4AF37",
        "accent2": "#E63946",
        "success": "#4EBA6F",
        "warning": "#D4AF37",
        "danger": "#730608",
        "text": "#F2F4F8",
        "subtext": "#8C93A3",
        "border": "#2E3342",
        "btn_normal_bg": "#12141A",
        "btn_normal_fg": "#D4AF37",
        "btn_accent_fg": "#0A0B0E",
        "select_bg": "#D4AF37",
        "select_fg": "#0A0B0E",
    }
}

FONT      = ("Segoe UI", 10)
FONT_SM   = ("Segoe UI", 9)
FONT_LG   = ("Segoe UI", 12, "bold")
FONT_HEAD = ("Segoe UI", 11, "bold")

THUMB_CONFIG = {
    "Off (Text Only)":     {"rowheight": 24,  "img_size": 0,   "col_width": 0,   "show": "headings"},
    "Small (50px)":        {"rowheight": 56,  "img_size": 50,  "col_width": 64,  "show": "tree headings"},
    "Medium (100px)":      {"rowheight": 110, "img_size": 100, "col_width": 116, "show": "tree headings"},
    "Large (180px)":       {"rowheight": 194, "img_size": 180, "col_width": 196, "show": "tree headings"},
    "Extra Large (250px)": {"rowheight": 266, "img_size": 250, "col_width": 268, "show": "tree headings"},
}

QUOTES = [
    "🛡️ Tenet 1: Zero-Tolerance Brand Perimeter — Defending genuine OEM craftsmanship worldwide.",
    "🎯 Tenet 2: Evidence-First Enforcement — Verified seller provenance & bulletproof chain of custody.",
    "🌐 Tenet 3: Cross-Marketplace Threat Intelligence — Unmasking international 3PL drop-shipping rings.",
    "🔍 Tenet 4: Perceptual Visual Fingerprinting — Eliminating counterfeit syndicates and cloned assets.",
    "⚡ Tenet 5: High-Octane Precision — Empowering brand protection analysts with autonomous speed.",
    "📊 Tenet 6: Measurable ROI & Revenue Defense — Quantifying genuine market value protected.",
    "🤝 Tenet 7: Built by Analysts, for Analysts — Purpose-engineered for front-line IP enforcement.",
    "🏛️ Tenet 8: Multi-Jurisdiction Compliance — Structuring clean A2C2 & marketplace enforcement dossiers.",
    "⚔️ Tenet 9: Proactive Recidivism Tracking — Permanently dismantling repeat counterfeit operations.",
    "💎 Valknut Motto: 'Vigilance in Protection, Precision in Enforcement.'",
    "🎖️ Analyst Recognition: Front-line protection defending consumer safety from rogue components.",
]

EASTER_EGG_QUOTES = [
    "🏎️ 'I live my life a quarter mile at a time. For those 10 seconds or less... I'm free.' — Dom Toretto",
    "💨 'Too soon, Junior! You didn't double-clutch like you should!'",
    "🔥 'DANGER TO MANIFOLD: Floor pan intact, scraping at maximum velocity!'",
    "🏁 'It don't matter if you win by an inch or a mile. Winning's winning.'",
    "🐎 'Eleanor... Don't you stall on me now, girl!' — Memphis Raines",
    "☕ Converting Caffeine into Intellectual Property Compliance...",
    "⚡ Searching through the eBay Matrix with Supercharged Precision!",
    "🚗 'I need NOS. One of the big ones. No, make it two. By tonight.'",
    "🧱 Careful! Stepped on a red 2x4 Lego brick! Enforcement Defense +100.",
    "✨ 'I knew you were counterfeit when you walked in...' 🎶",
    "🤖 Heimvis Core Online: All-seeing eye tracking rogue syndicates across all dimensions!",
]

EBAY_LOCALES = [
    {"code": "US", "name": "United States", "domain": "ebay.com", "region": "North America", "flag": "🇺🇸"},
    {"code": "CA", "name": "Canada", "domain": "ebay.ca", "region": "North America", "flag": "🇨🇦"},
    {"code": "CA_FR", "name": "Canada (French)", "domain": "cafr.ebay.ca", "region": "North America", "flag": "🇨🇦"},
    {"code": "UK", "name": "United Kingdom", "domain": "ebay.co.uk", "region": "Europe", "flag": "🇬🇧"},
    {"code": "DE", "name": "Germany", "domain": "ebay.de", "region": "Europe", "flag": "🇩🇪"},
    {"code": "AU", "name": "Australia", "domain": "ebay.com.au", "region": "APAC", "flag": "🇦🇺"},
    {"code": "FR", "name": "France", "domain": "ebay.fr", "region": "Europe", "flag": "🇫🇷"},
    {"code": "IT", "name": "Italy", "domain": "ebay.it", "region": "Europe", "flag": "🇮🇹"},
    {"code": "ES", "name": "Spain", "domain": "ebay.es", "region": "Europe", "flag": "🇪🇸"},
    {"code": "NL", "name": "Netherlands", "domain": "ebay.nl", "region": "Europe", "flag": "🇳🇱"},
    {"code": "IE", "name": "Ireland", "domain": "ebay.ie", "region": "Europe", "flag": "🇮🇪"},
    {"code": "AT", "name": "Austria", "domain": "ebay.at", "region": "Europe", "flag": "🇦🇹"},
    {"code": "CH", "name": "Switzerland", "domain": "ebay.ch", "region": "Europe", "flag": "🇨🇭"},
    {"code": "BE_FR", "name": "Belgium (FR)", "domain": "befr.ebay.be", "region": "Europe", "flag": "🇧🇪"},
    {"code": "BE_NL", "name": "Belgium (NL)", "domain": "benl.ebay.be", "region": "Europe", "flag": "🇧🇪"},
    {"code": "PL", "name": "Poland", "domain": "ebay.pl", "region": "Europe", "flag": "🇵🇱"},
]

THEME_QUOTES = {
    "lego": "🧱 Careful! Stepped on a red 2x4 Lego brick! Enforcement Defense +100.",
    "taylor_swift": "✨ 'I knew you were counterfeit when you walked in...' 🎶",
    "toyota_gr": "🏁 Toyota Gazoo Racing: Twin-turbo spooling at 8,500 RPM on the Nürburgring!",
    "dodge_hellcat": "🔥 6.2L Supercharged HEMI V8 idling at 797 Horsepower. Zero infringement allowed!",
    "bmw_m": "🏁 BMW M shift lights flashing red... Ultimate Driving Machine compliance active!",
    "subaru_wrc": "⭐ Symmetrical AWD launching through muddy stages at 120 MPH!",
    "ford_racing": "🔵 Ford Performance EcoBoost twin-turbos delivering high-octane enforcement!",
    "hyundai_n": "⚡ Hyundai N Corner Rascal mode engaged... Zero slip compliance!",
    "jeep_trail": "🚙 Trail-Rated 4x4 crawling through rocky listings... Nothing gets past.",
    "black_decker": "🔨 High-torque brushless impact driver drilling through database records!",
    "sprayground": "🎒 Shark mouth teeth exposed... Biting down on unauthorized listings!",
    "pastel": "🌸 Cherry blossoms drifting gently across the brand library... Zen mode active.",
    "nfl": "🏈 4th & inches on the goal line... Defense holds the perimeter!",
    "gm_heritage": "💎 General Motors & ACDelco: Protecting genuine American craftsmanship from Detroit to the world!",
    "eleanor": "🐎 'Eleanor: The unicorn of muscle cars. Push the Go-Baby-Go button and hold on tight!' — Memphis Raines",
    "kia_gt": "⚡ Kia GT-Line & Stinger: Twin-turbo 368 HP compliance scanning running at full boost!",
    "matrix": "💻 'You take the blue pill—the story ends. You run this tool—you stay in Wonderland.'",
    "cyberpunk": "⚡ 'Wake up, Samurai. We have counterfeit listings to harvest.'",
    "catppuccin": "☕ A velvety warm mocha brewed to perfection. Smooth and cozy.",
    "synthwave": "🕹️ High Score: 999,999 PTS! Insert coin to continue.",
    "continental": "🪙 Winston: 'Rules... without them, we live with the animals.'",
}

THEME_SUBHEADERS = {
    "continental": "🪙 THE CONTINENTAL — HIGH TABLE EXCOMMUNICADO & SYNDICATE ELIMINATION SUITE",
    "toyota_gr": "🏁 TOYOTA GAZOO RACING & LEXUS — BRAND PROTECTION SUITE",
    "gm_heritage": "💎 GENERAL MOTORS & ACDELCO — IP COMPLIANCE HARVESTER",
    "subaru_wrc": "⭐ SUBARU MOTORSPORTS — SYMMETRICAL COMPLIANCE SHIELD",
    "kia_gt": "⚡ KIA GT-LINE & STINGER — HIGH-BOOST TRADEMARK DEFENSE",
    "hyundai_n": "⚡ HYUNDAI N PERFORMANCE — CORNER RASCAL COMPLIANCE",
    "ford_racing": "🔵 FORD PERFORMANCE RACING — ECOBOOST DEFENSE SUITE",
    "dodge_hellcat": "🔥 DODGE SRT HELLCAT & MOPAR — SUPERCHARGED TRADEMARK SHIELD",
    "jeep_trail": "🚙 JEEP TRAIL RATED 4x4 — ALL-TERRAIN BRAND PROTECTION",
    "bmw_m": "🏁 BMW M MOTORSPORT — ULTIMATE COMPLIANCE MACHINE",
    "lego": "🧱 THE LEGO GROUP — GLOBAL TRADEMARK GUARDIAN",
    "black_decker": "🔨 BLACK & DECKER — INDUSTRIAL BRAND COMPLIANCE",
    "nfl": "🏈 NFL GRIDIRON — OFFICIAL MERCHANDISE ENFORCEMENT",
    "taylor_swift": "✨ TAYLOR SWIFT ERAS — OFFICIAL TRADEMARK DEFENSE",
    "sprayground": "🎒 SPRAYGROUND SHARK — STREETWEAR AUTHENTICITY SHIELD",
    "pastel": "🌸 SAKURA BLOSSOM — ZEN BRAND HARVESTER",
    "eleanor": "🐎 1967 SHELBY GT500 ELEANOR — GO-BABY-GO UNICORN EDITION",
    "synthwave": "🕹️ RETRO SYNTHWAVE 80s — ARCADE COMPLIANCE SPECIAL",
    "cyberpunk": "⚡ CYBERPUNK 2077 — NIGHT CITY BRAND RUNNER",
    "matrix": "💻 THE MATRIX HARVESTER — ZERO INFRINGEMENT CONSTRUCT",
    "midnight": "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER",
    "dark": "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER",
    "slate": "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER",
    "navy": "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER",
    "catppuccin": "☕ MOCHA VELVET — ARTISAN BRAND ENFORCEMENT",
    "forest": "🌲 FOREST CANOPY — SUSTAINABLE IP COMPLIANCE",
    "nord": "❄️ NORDIC ARCTIC — PRECISION ICE DEFENSE",
}

CONTINENTAL_QUOTES = [
    "🪙 Winston: 'Rules... without them, we live with the animals.'",
    "🪙 Charon: 'Always a pleasure having you with us, Mr. Wick.'",
    "🪙 John Wick: 'Yeah, I'm thinkin' I'm back.'",
    "🪙 The Bowery King: 'Somebody please... get this man a brand library.'",
    "🪙 The Sommelier: 'Something robust, precise... may I suggest a full 16-locale sweep?'",
    "🪙 Winston: 'Si vis pacem, para bellum.'",
    "🪙 Charon: 'Storefronts completely sanitized, sir.'",
    "🪙 Winston: 'Contract fulfilled. High Table dossier compiled.'",
    "🪙 John Wick: 'Whoever comes, whoever it is... I'll kill them. I'll kill them all (from the marketplace).'",
    "🪙 Charon: 'How may I be of service this evening, sir?'",
    "🪙 Winston: 'You have your target. Execute with discretion.'"
]


class EbayTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔺 Valknut Brand Intelligence — Multi-Marketplace Threat Harvester & Enforcement Suite")

        self.data_store     = DataStore()
        # Scraper background/headless mode (Default: True / Silent Background)
        self.headless_var   = tk.BooleanVar(value=bool(self.data_store.get_setting("headless", True)))
        self.scraper        = EbayScraper(headless=self.headless_var.get())
        self.aliexpress_scraper = AliExpressScraper(headless=self.headless_var.get())
        self.wish_scraper   = WishScraper(headless=self.headless_var.get())
        self.temu_scraper   = TemuScraper(headless=self.headless_var.get())
        self.mercadolibre_scraper = MercadoLibreScraper(headless=self.headless_var.get())
        self.redbubble_scraper = RedbubbleScraper(headless=self.headless_var.get())
        self.printerval_scraper = PrintervalScraper(headless=self.headless_var.get())
        self.marketplace_var= tk.StringVar(value="🛒 eBay.com")
        self.exporter       = ExcelExporter()

        # Load saved theme
        saved_theme_key = self.data_store.get_setting("theme", "midnight")
        if saved_theme_key not in THEMES:
            saved_theme_key = "midnight"
        self.current_theme_key = saved_theme_key
        self.theme = THEMES[self.current_theme_key]

        # Responsive window sizing (Optimized for 1080p, laptop scaling & widescreen displays)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = min(1680, max(1024, int(screen_w * 0.90)))
        win_h = min(1060, max(740, int(screen_h * 0.92)))
        pos_x = max(10, (screen_w - win_w) // 2)
        pos_y = max(10, (screen_h - win_h - 40) // 2)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(980, 600)
        self.configure(bg=self.theme["bg"])

        self.use_api        = tk.BooleanVar(value=bool(self.data_store.get_setting("use_api", False)))
        self.api_app_id_var = tk.StringVar(value=self.data_store.get_setting("api_app_id", ""))
        self.api_cert_id_var= tk.StringVar(value=self.data_store.get_setting("api_cert_id", ""))
        self.condition_var  = tk.StringVar(value="all")
        self.theme_var      = tk.StringVar(value=self.theme["name"])
        saved_thumb_size    = self.data_store.get_setting("thumb_size", "Medium (100px)")
        if saved_thumb_size not in THUMB_CONFIG:
            saved_thumb_size = "Medium (100px)"
        self.thumb_size_var = tk.StringVar(value=saved_thumb_size)
        self.show_preview_var = tk.BooleanVar(value=(saved_thumb_size != "Off (Text Only)"))
        self.sound_enabled_var = tk.BooleanVar(value=True)

        # Brand targeting states: { item_id: "target" | "exclude" | "neutral" }
        self.brand_states   = {}

        self.results        = []          # all harvested rows this session
        self.seen_item_ids  = set()       # session deduplication
        self.queue          = []          # list of jobs
        self.executed_jobs  = []          # record of executed jobs for audit log
        self.sort_directions= {}          # col -> bool (True = descending)

        # Image thumbnail caches & Hover popup window
        self.raw_img_cache      = {}          # url -> PIL.Image (source image)
        self.inline_img_cache   = {}          # (size_key, url) -> PhotoImage (resized for treeview)
        self.img_cache          = {}          # url -> PhotoImage (large hover popup)
        self._placeholders      = {}          # size_px -> PhotoImage
        self.preview_win        = None
        self.last_hovered_iid   = None
        self.preview_cancel_id  = None
        self._drag_data         = None

        # Konami & Secret Easter Egg buffers
        self.konami_sequence = ["Up", "Up", "Down", "Down", "Left", "Right", "Left", "Right", "b", "a"]
        self.konami_buffer   = []
        self.word_buffer     = ""
        self.quote_idx       = 0
        self.achieved_milestones = set()

        self.col_labels = {
            "brand": "Brand",
            "product_type": "Product Type",
            "title": "Title",
            "item_id": "Item ID",
            "price": "Price",
            "seller": "Seller",
            "seller_origin": "Origin",
            "threat_badge": "Threat Intel (3PL / Origin)",
            "location": "Item Location",
            "thumbnail": "Thumbnail URL",
            "url": "Listing URL"
        }
        self.field_map = {
            "brand": "brand",
            "product_type": "product_type",
            "title": "title",
            "item_id": "item_id",
            "price": "price",
            "seller": "seller",
            "seller_origin": "seller_origin",
            "threat_badge": "threat_badge",
            "location": "location",
            "thumbnail": "image_url",
            "url": "url"
        }
        
        # Thread & Execution Control
        self.running        = False
        self.paused         = False
        self.stop_event     = threading.Event()
        self.pause_event    = threading.Event()
        self.pause_event.set()            # Set = unpaused
        # Widget registry for dynamic theme updates
        self.themed_widgets = {
            "bg_frames": [],
            "panel_frames": [],
            "section_labels": [],
            "dividers": [],
            "text_labels": [],
            "subtext_labels": [],
            "text_inputs": [],
            "accent_btns": [],
            "danger_btns": [],
            "normal_btns": [],
            "checks": [],
        }

        # Track open modeless windows
        self._win_registry = None
        self._win_threat_intel = None
        self._win_importer = None
        self._win_whitelist = None

        self._build_ui()
        self._refresh_brand_tree()
        self._refresh_exclusion_list()
        # Global Keyboard Shortcuts
        self.bind_all("<Control-e>", lambda e: self._export())
        self.bind_all("<Control-E>", lambda e: self._export())

        # Listen globally for Konami Code
        self.bind_all("<Key>", self._check_konami)

        # Restore saved window geometry if present
        saved_geo = self.data_store.get_setting("window_geometry", "")
        if saved_geo:
            try:
                self.geometry(saved_geo)
            except Exception:
                pass

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(50, self._apply_dark_titlebar)

    def _on_closing(self):
        try:
            self.data_store.set_setting("window_geometry", self.geometry())
            if hasattr(self, "result_tree"):
                col_w = {c: self.result_tree.column(c, "width") for c in self.result_tree["columns"]}
                self.data_store.set_setting("column_widths", col_w)
        except Exception:
            pass
        self.destroy()

    # ══════════════════════════════════════════════════════════════════════════
    #  UI BUILD
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        t = self.theme
        # ── top bar ──────────────────────────────────────────────────────────
        self.top_bar = tk.Frame(self, bg=t["panel"], pady=6)
        self.top_bar.pack(fill="x")
        self.themed_widgets["panel_frames"].append(self.top_bar)

        # Title & Sub-header container frame
        title_box = tk.Frame(self.top_bar, bg=t["panel"])
        title_box.pack(side="left", padx=16)
        self.themed_widgets["panel_frames"].append(title_box)

        # Clickable interactive title logo (Easter Egg)
        self.title_lbl = tk.Label(title_box, text="🔺 Valknut Brand Intelligence",
                                  font=("Segoe UI", 12, "bold"), bg=t["panel"], fg=t["accent"],
                                  cursor="hand2")
        self.title_lbl.pack(anchor="w")
        self.title_lbl.bind("<Button-1>", self._on_title_click)
        self.themed_widgets["section_labels"].append(self.title_lbl)

        # Dynamic official client/portfolio sub-header
        sub_text = THEME_SUBHEADERS.get(self.current_theme_key, "🛡️ CROSS-BORDER THREAT HARVESTING & SUPPLY CHAIN DEFENSE")
        self.subtitle_lbl = tk.Label(title_box, text=sub_text, font=("Segoe UI", 8, "bold"),
                                     bg=t["panel"], fg=t.get("accent2", t["subtext"]))
        self.subtitle_lbl.pack(anchor="w")
        self.themed_widgets["subtext_labels"].append(self.subtitle_lbl)

        # Right side controls: Professional > Additional > Fun / Info
        top_right = tk.Frame(self.top_bar, bg=t["panel"])
        top_right.pack(side="right", padx=12)
        self.themed_widgets["panel_frames"].append(top_right)

        # 1. Professional / Core Operations
        market_lbl = tk.Label(top_right, text="Platform:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        market_lbl.pack(side="left", padx=(0, 2))
        self.themed_widgets["subtext_labels"].append(market_lbl)

        self.market_combo = ttk.Combobox(top_right, textvariable=self.marketplace_var,
                                         values=["🛒 eBay.com", "🌐 AliExpress.com", "🌠 Wish.com", "🟠 Temu.com", "🇲🇽 Mercado Libre", "🎨 Redbubble.com", "👕 Printerval.com"],
                                         state="readonly", width=15, font=FONT_SM)
        self.market_combo.pack(side="left", padx=(0, 4))
        self.market_combo.bind("<<ComboboxSelected>>", self._on_market_changed)

        self.meli_login_btn = self._btn(top_right, "🔑 MeLi Login", self._launch_meli_login)
        # only pack when Mercado Libre is active

        self._btn(top_right, "📥 Import", self._open_adhoc_importer_window, accent=True).pack(side="left", padx=(0, 2))
        self._btn(top_right, "🛡 Registry", self._open_enforcement_registry_window).pack(side="left", padx=(0, 2))
        self._btn(top_right, "🛡 Whitelist", self._open_whitelist_manager_window).pack(side="left", padx=(0, 2))
        self._btn(top_right, "🕵 Threat Intel", self._open_threat_intel_window, accent=True).pack(side="left", padx=(0, 4))

        # 2. Additional Automation Settings
        bg_cb = tk.Checkbutton(top_right, text="👻 Stealth",
                               variable=self.headless_var, command=self._toggle_headless,
                               bg=t["panel"], fg=t["text"], selectcolor=t["entry_bg"],
                               activebackground=t["panel"], font=FONT_SM)
        bg_cb.pack(side="left", padx=(0, 2))
        self.themed_widgets["checks"].append(bg_cb)

        self.api_cb = tk.Checkbutton(top_right, text="API Mode",
                                     variable=self.use_api, command=self._toggle_api,
                                     bg=t["panel"], fg=t["text"], selectcolor=t["entry_bg"],
                                     activebackground=t["panel"], font=FONT_SM)
        self.api_cb.pack(side="left", padx=(0, 4))
        self.themed_widgets["checks"].append(self.api_cb)

        self.app_id_lbl = tk.Label(top_right, text="App ID:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        self.themed_widgets["subtext_labels"].append(self.app_id_lbl)

        self.app_id_entry = tk.Entry(top_right, textvariable=self.api_app_id_var, width=10,
                                     bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                     relief="flat", font=FONT_SM)
        self.themed_widgets["text_inputs"].append(self.app_id_entry)

        self.cert_id_lbl = tk.Label(top_right, text="Cert ID:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        self.themed_widgets["subtext_labels"].append(self.cert_id_lbl)

        self.cert_id_entry = tk.Entry(top_right, textvariable=self.api_cert_id_var, width=10,
                                      bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                      relief="flat", font=FONT_SM, show="•")
        self.themed_widgets["text_inputs"].append(self.cert_id_entry)

        self.save_keys_btn = self._btn(top_right, "Save", self._save_api_keys, accent=True)

        # 3. Customization & System Info (Rightmost)
        theme_lbl = tk.Label(top_right, text="🎨 Theme:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        theme_lbl.pack(side="left", padx=(2, 2))
        self.themed_widgets["subtext_labels"].append(theme_lbl)

        current_key = self.current_theme_key
        theme_names = [th["name"] for k, th in THEMES.items() if not th.get("hidden", False) or k == current_key or (k == "continental" and self.data_store.is_wick_unlocked())]
        self.theme_combo = ttk.Combobox(top_right, textvariable=self.theme_var, values=theme_names,
                                        state="readonly", width=22, font=FONT_SM)
        self.theme_combo.pack(side="left", padx=(0, 3))
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_changed)

        self.about_btn = self._btn(top_right, "ℹ", self._show_about_dialog)
        self.about_btn.pack(side="left", padx=(0, 0))

        self._toggle_api()

        # ── status bar (Packed FIRST at bottom so it is permanently pinned to the floor) ───────────
        self.status_bar = tk.Frame(self, bg=t["panel"], pady=4)
        self.status_bar.pack(fill="x", side="bottom")
        self.themed_widgets["panel_frames"].append(self.status_bar)

        self.status_var = tk.StringVar(value="Ready.")
        self.status_lbl = tk.Label(self.status_bar, textvariable=self.status_var,
                                   bg=t["panel"], fg=t["text"], font=FONT_SM)
        self.status_lbl.pack(side="left", padx=12)
        self.themed_widgets["text_labels"].append(self.status_lbl)

        # Chime toggle checkbox in status bar
        sound_cb = tk.Checkbutton(self.status_bar, text="🔔 Sound Alert",
                                  variable=self.sound_enabled_var,
                                  bg=t["panel"], fg=t["subtext"], selectcolor=t["entry_bg"],
                                  activebackground=t["panel"], font=FONT_SM)
        sound_cb.pack(side="right", padx=(0, 12))
        self.themed_widgets["checks"].append(sound_cb)

        # Style and create Progressbar with vibrant accent animation
        style = ttk.Style()
        style.configure("Valknut.Horizontal.TProgressbar",
                        troughcolor=t["entry_bg"],
                        background=t["accent"],
                        bordercolor=t.get("border", t["entry_bg"]))
        self.progress = ttk.Progressbar(self.status_bar, mode="indeterminate", length=200, style="Valknut.Horizontal.TProgressbar")
        self.progress.pack(side="right", padx=12)

        # Globally prevent ttk.Combobox from intercepting mousewheel scroll and clear text selection on change
        self.bind_class("TCombobox", "<MouseWheel>", lambda e: "break")
        def _clear_combobox_selection(e):
            try:
                e.widget.selection_clear()
                self.focus_set()
            except Exception:
                pass
        self.bind_class("TCombobox", "<<ComboboxSelected>>", _clear_combobox_selection, add="+")

        # ── main paned layout (Expands to fill everything between top and bottom bars) ───────────────
        self.paned = tk.PanedWindow(self, orient="horizontal", bg=t["bg"], sashwidth=6,
                                    sashrelief="flat", bd=0)
        self.paned.pack(fill="both", expand=True, padx=8, pady=6)
        self.themed_widgets["bg_frames"].append(self.paned)

        left  = self._build_left_panel(self.paned)
        right = self._build_right_panel(self.paned)

        self.paned.add(left,  minsize=440, width=490)
        self.paned.add(right, minsize=620)

    # ── LEFT PANEL ────────────────────────────────────────────────────
    def _build_left_panel(self, parent):
        t = self.theme
        container = tk.Frame(parent, bg=t["bg"])
        self.themed_widgets["bg_frames"].append(container)

        canvas = tk.Canvas(container, bg=t["bg"], highlightthickness=0, bd=0)
        self.themed_widgets["bg_frames"].append(canvas)
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame = tk.Frame(canvas, bg=t["bg"])
        self.themed_widgets["bg_frames"].append(frame)

        frame_window = canvas.create_window((0, 0), window=frame, anchor="nw")

        def _on_left_config(e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(frame_window, width=canvas.winfo_width())

        frame.bind("<Configure>", _on_left_config)
        canvas.bind("<Configure>", _on_left_config)
        self._update_left_scrollregion = _on_left_config

        def _on_left_mousewheel(event):
            bbox = canvas.bbox("all")
            if bbox and bbox[3] > canvas.winfo_height():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_left_mousewheel)
        frame.bind("<MouseWheel>", _on_left_mousewheel)

        # ── Stores / Sellers input (Multi-store support) ──────────────────────
        store_hdr = tk.Frame(frame, bg=t["bg"])
        store_hdr.pack(fill="x", padx=8, pady=(4, 2))
        self.themed_widgets["bg_frames"].append(store_hdr)

        lbl = tk.Label(store_hdr, text="🏪 Stores / Sellers (One per line or URL)",
                       font=FONT_HEAD, bg=t["bg"], fg=t["text"], cursor="hand2")
        lbl.pack(side="left")
        self.themed_widgets["section_labels"].append(lbl)

        def _clear_stores_input():
            self.store_text.delete("1.0", "end")
            self._restore_store_ph()

        self._btn(store_hdr, "✕ Clear", _clear_stores_input).pack(side="right")
        
        store_frame = tk.Frame(frame, bg=t["bg"])
        store_frame.pack(fill="x", padx=8, pady=(0, 2))
        self.themed_widgets["bg_frames"].append(store_frame)
        
        self.store_text = tk.Text(store_frame, height=2, bg=t["entry_bg"], fg=t["text"],
                                  insertbackground=t["text"], relief="flat", font=FONT_SM,
                                  wrap="none")
        store_vsb = ttk.Scrollbar(store_frame, orient="vertical", command=self.store_text.yview)
        self.store_text.configure(yscrollcommand=store_vsb.set)
        self.store_text.pack(side="left", fill="both", expand=True)
        store_vsb.pack(side="right", fill="y")
        self.themed_widgets["text_inputs"].append(self.store_text)
        
        toggle_stores = self._create_resize_grip(frame, self.store_text, widget_type="lines", min_val=1, max_val=25, default_val=2, max_toggle=10, name="stores")
        
        max_stores_btn = tk.Button(store_hdr, text="⤢", command=toggle_stores, bg=t["bg"], fg=t["subtext"],
                                   relief="flat", bd=0, font=("Segoe UI", 8, "bold"), cursor="hand2",
                                   padx=4, pady=0, activebackground=t["bg"], activeforeground=t["accent"])
        max_stores_btn.pack(side="right", padx=(0, 4))
        self.themed_widgets["text_labels"].append(max_stores_btn)
        lbl.bind("<Double-Button-1>", lambda e: toggle_stores())
        
        self.store_placeholder = "https://www.ebay.com/str/store1\nhttps://www.aliexpress.com/store/110123456\nseller3"
        self.store_text.insert("1.0", self.store_placeholder)
        self.store_text.config(fg=t["subtext"])
        self.store_text.bind("<FocusIn>", self._clear_store_ph)
        self.store_text.bind("<FocusOut>", self._restore_store_ph)

        # Condition filter
        cond_row = tk.Frame(frame, bg=t["bg"])
        cond_row.pack(fill="x", padx=8, pady=(0, 3))
        self.themed_widgets["bg_frames"].append(cond_row)

        cond_lbl = tk.Label(cond_row, text="Condition:", bg=t["bg"], fg=t["subtext"], font=FONT_SM)
        cond_lbl.pack(side="left")
        self.themed_widgets["subtext_labels"].append(cond_lbl)

        ttk.Radiobutton(cond_row, text="All", variable=self.condition_var, value="all").pack(side="left", padx=6)
        ttk.Radiobutton(cond_row, text="New Only", variable=self.condition_var, value="new").pack(side="left", padx=6)
        ttk.Radiobutton(cond_row, text="Used Only", variable=self.condition_var, value="used").pack(side="left", padx=6)

        # ── Brand Library & Targeting ─────────────────────────────────────────
        toggle_brands_holder = []
        def _toggle_brands_proxy():
            if toggle_brands_holder:
                toggle_brands_holder[0]()

        self._section(frame, "🏷  Brand Library (Target & Exclude)", toggle_cmd=_toggle_brands_proxy)

        # Target / Exclude State Selection Toolbar (Row 1)
        target_tools_1 = tk.Frame(frame, bg=t["bg"])
        target_tools_1.pack(fill="x", padx=8, pady=(0, 2))
        self.themed_widgets["bg_frames"].append(target_tools_1)

        self._btn(target_tools_1, "🎯 Target", lambda: self._set_selected_mode("target"), accent=True).pack(side="left", padx=(0, 3))
        self._btn(target_tools_1, "🚫 Exclude", lambda: self._set_selected_mode("exclude"), danger=True).pack(side="left", padx=(0, 3))
        self._btn(target_tools_1, "⚪ Neutral", lambda: self._set_selected_mode("neutral")).pack(side="left", padx=(0, 3))
        self._btn(target_tools_1, "✕ Reset All", self._reset_brand_modes).pack(side="right")

        # Fast Auto-Exclude Action Toolbar (Row 2)
        target_tools_2 = tk.Frame(frame, bg=t["bg"])
        target_tools_2.pack(fill="x", padx=8, pady=(0, 3))
        self.themed_widgets["bg_frames"].append(target_tools_2)

        self._btn(target_tools_2, "⚡ Excl Other Brands", self._auto_exclude_other_brands).pack(side="left", padx=(0, 3))
        self._btn(target_tools_2, "⚡ Excl Other Models", self._auto_exclude_other_models).pack(side="left", padx=(0, 3))
        self._btn(target_tools_2, "⚡ Excl All Others", self._auto_exclude_all_others).pack(side="left")

        brand_ctrl = tk.Frame(frame, bg=t["bg"])
        brand_ctrl.pack(fill="x", padx=8, pady=(0, 2))
        self.themed_widgets["bg_frames"].append(brand_ctrl)

        self.brand_tree = ttk.Treeview(brand_ctrl, height=6, selectmode="extended")
        self.brand_tree["columns"] = ("type", "action")
        self.brand_tree.column("#0",     width=195)
        self.brand_tree.column("type",   width=60, anchor="center")
        self.brand_tree.column("action", width=85, anchor="center")
        self.brand_tree.heading("#0",     text="Brand / Model")
        self.brand_tree.heading("type",   text="Type")
        self.brand_tree.heading("action", text="Action")
        
        self.brand_tree.tag_configure("target", foreground=t["success"])
        self.brand_tree.tag_configure("exclude", foreground=t["danger"])
        self.brand_tree.tag_configure("neutral", foreground=t["text"])
        
        self._style_tree(self.brand_tree)
        self.brand_tree.pack(fill="x")

        self.brand_tree.bind("<Double-1>", self._on_tree_double_click)
        self.brand_tree.bind("<space>", lambda e: self._on_tree_double_click(e))
        self.brand_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.brand_tree.bind("<ButtonPress-1>", self._on_brand_drag_start)
        self.brand_tree.bind("<B1-Motion>", self._on_brand_drag_motion)
        self.brand_tree.bind("<ButtonRelease-1>", self._on_brand_drag_release)
        self.brand_tree.bind("<Alt-Up>", lambda e: self._move_selected_brand(-1))
        self.brand_tree.bind("<Alt-Down>", lambda e: self._move_selected_brand(1))
        self.brand_tree.bind("<Control-Up>", lambda e: self._move_selected_brand(-1))
        self.brand_tree.bind("<Control-Down>", lambda e: self._move_selected_brand(1))

        # Brand Library management buttons
        btn_row = tk.Frame(frame, bg=t["bg"])
        btn_row.pack(fill="x", padx=8, pady=2)
        self.themed_widgets["bg_frames"].append(btn_row)

        self._btn(btn_row, "＋ Parent", self._add_parent_brand).pack(side="left", padx=(0, 3))
        self._btn(btn_row, "＋ Sub",    self._add_sub_brand).pack(side="left", padx=(0, 3))
        self._btn(btn_row, "＋ Model",  self._add_model).pack(side="left", padx=(0, 3))
        self._btn(btn_row, "▲ Up",      lambda: self._move_selected_brand(-1)).pack(side="left", padx=(0, 3))
        self._btn(btn_row, "▼ Down",    lambda: self._move_selected_brand(1)).pack(side="left", padx=(0, 3))
        self._btn(btn_row, "🗑 Remove",  self._remove_brand, danger=True).pack(side="right")

        toggle_brands = self._create_resize_grip(frame, self.brand_tree, widget_type="treeview", min_val=3, max_val=40, default_val=6, max_toggle=22, name="brands")
        toggle_brands_holder.append(toggle_brands)

        # Include terms preview
        prev_lbl = tk.Label(frame, text="Active Target Terms Preview (editable for custom keywords):",
                            bg=t["bg"], fg=t["subtext"], font=FONT_SM, cursor="hand2")
        prev_lbl.pack(anchor="w", padx=8, pady=(3, 1))
        self.themed_widgets["subtext_labels"].append(prev_lbl)

        self.include_text = tk.Text(frame, height=2, bg=t["entry_bg"], fg=t["text"],
                                    insertbackground=t["text"], relief="flat", font=FONT_SM,
                                    wrap="word")
        self.include_text.pack(fill="x", padx=8)
        self.themed_widgets["text_inputs"].append(self.include_text)

        toggle_inc = self._create_resize_grip(frame, self.include_text, widget_type="lines", min_val=1, max_val=20, default_val=2, max_toggle=8, name="includes")
        prev_lbl.bind("<Double-Button-1>", lambda e: toggle_inc())

        # ── Exclusion list ────────────────────────────────────────────────────
        toggle_excl_holder = []
        def _toggle_excl_proxy():
            if toggle_excl_holder:
                toggle_excl_holder[0]()

        self._section(frame, "🚫 Generic Exclusion Terms", toggle_cmd=_toggle_excl_proxy)

        # Select all / unselect all toolbar
        excl_tools = tk.Frame(frame, bg=t["bg"])
        excl_tools.pack(fill="x", padx=8, pady=(0, 2))
        self.themed_widgets["bg_frames"].append(excl_tools)

        self._btn(excl_tools, "☑ Select All", self._select_all_exclusions).pack(side="left", padx=(0, 4))
        self._btn(excl_tools, "☐ Unselect All", self._unselect_all_exclusions).pack(side="left")

        excl_outer = tk.Frame(frame, bg=t["bg"])
        excl_outer.pack(fill="x", padx=8)
        self.themed_widgets["bg_frames"].append(excl_outer)

        self.excl_canvas = tk.Canvas(excl_outer, bg=t["entry_bg"], height=65,
                                     highlightthickness=1,
                                     highlightbackground=t["border"])
        excl_scroll = ttk.Scrollbar(excl_outer, orient="vertical",
                                    command=self.excl_canvas.yview)
        self.excl_canvas.configure(yscrollcommand=excl_scroll.set)
        excl_scroll.pack(side="right", fill="y")
        self.excl_canvas.pack(side="left", fill="both", expand=True)

        self.excl_inner = tk.Frame(self.excl_canvas, bg=t["entry_bg"])
        self._excl_window = self.excl_canvas.create_window(
            (0, 0), window=self.excl_inner, anchor="nw")

        def _on_excl_configure(e):
            self.excl_canvas.configure(
                scrollregion=self.excl_canvas.bbox("all"))
            self.excl_canvas.itemconfig(
                self._excl_window, width=self.excl_canvas.winfo_width())

        self.excl_inner.bind("<Configure>", _on_excl_configure)
        self.excl_canvas.bind("<Configure>", _on_excl_configure)
        self.excl_canvas.bind("<MouseWheel>", self._on_excl_mousewheel)
        self.excl_inner.bind("<MouseWheel>", self._on_excl_mousewheel)

        self.excl_vars = {}   # term -> BooleanVar

        excl_btn_row = tk.Frame(frame, bg=t["bg"])
        excl_btn_row.pack(fill="x", padx=8, pady=4)
        self.themed_widgets["bg_frames"].append(excl_btn_row)

        self.new_excl_entry = self._entry(excl_btn_row, placeholder="New generic exclusion")
        self.new_excl_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.new_excl_entry.bind("<Return>", lambda e: self._add_exclusion())
        self._btn(excl_btn_row, "＋ Add", self._add_exclusion).pack(side="left")
        self._btn(excl_btn_row, "✕", self._remove_exclusion, danger=True).pack(side="left", padx=4)

        toggle_excl = self._create_resize_grip(frame, self.excl_canvas, widget_type="canvas_px", min_val=40, max_val=600, default_val=65, max_toggle=260, name="exclusions")
        toggle_excl_holder.append(toggle_excl)

        # ── Queue / Run Controls ──────────────────────────────────────────────
        toggle_queue_holder = []
        def _toggle_queue_proxy():
            if toggle_queue_holder:
                toggle_queue_holder[0]()

        self._section(frame, "📋 Search Queue & Batch Execution", toggle_cmd=_toggle_queue_proxy)

        # ── 1-Click Client Portfolio Sweep Presets ────────────────────────────
        preset_frame = tk.Frame(frame, bg=t["panel"], padx=6, pady=6)
        preset_frame.pack(fill="x", padx=8, pady=(0, 6))
        self.themed_widgets["panel_frames"].append(preset_frame)

        p_top_row = tk.Frame(preset_frame, bg=t["panel"])
        p_top_row.pack(fill="x")
        self.themed_widgets["panel_frames"].append(p_top_row)

        p_lbl = tk.Label(p_top_row, text="📦 Portfolio Preset:", font=("Segoe UI", 9, "bold"),
                         bg=t["panel"], fg=t["accent"])
        p_lbl.pack(side="left")
        self.themed_widgets["section_labels"].append(p_lbl)

        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(p_top_row, textvariable=self.preset_var, state="readonly",
                                         width=22, font=FONT_SM)
        self.preset_combo.pack(side="left", padx=4, fill="x", expand=True)
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)

        self._btn(p_top_row, "💾 Save", self._save_custom_preset).pack(side="left", padx=2)
        self._btn(p_top_row, "🗑", self._delete_custom_preset, danger=True).pack(side="left", padx=2)

        self.sweep_btn = self._btn(
            preset_frame,
            "⚡ 1-Click Sweep: Queue Portfolio for All Stores",
            self._queue_portfolio_preset,
            accent=True
        )
        self.sweep_btn.pack(fill="x", pady=(4, 0))

        q_actions_row = tk.Frame(frame, bg=t["bg"])
        q_actions_row.pack(fill="x", padx=8, pady=(0, 4))
        self.themed_widgets["bg_frames"].append(q_actions_row)

        self.add_q_btn = self._btn(q_actions_row, "➕ Add to Queue", self._add_to_queue)
        self.add_q_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self.clean_sweep_btn = self._btn(q_actions_row, "🎯 Clean Brand Sweep", self._queue_clean_targeted_brands, accent=True)
        self.clean_sweep_btn.pack(side="right", fill="x", expand=True, padx=(3, 0))

        queue_frame = tk.Frame(frame, bg=t["bg"])
        queue_frame.pack(fill="x", padx=8, pady=(0, 4))
        self.themed_widgets["bg_frames"].append(queue_frame)

        self.queue_list = tk.Listbox(queue_frame, height=4, bg=t["entry_bg"], fg=t["text"],
                                     selectbackground=t["accent"], selectforeground=t.get("select_fg", "white"),
                                     font=FONT_SM, relief="flat", bd=0, highlightthickness=0,
                                     activestyle="none")
        q_vsb = ttk.Scrollbar(queue_frame, orient="vertical", command=self.queue_list.yview)
        self.queue_list.configure(yscrollcommand=q_vsb.set)
        self.queue_list.pack(side="left", fill="both", expand=True)
        q_vsb.pack(side="right", fill="y")
        self.queue_list.bind("<Delete>", lambda e: self._remove_selected_from_queue())
        self.queue_list.bind("<BackSpace>", lambda e: self._remove_selected_from_queue())
        self.themed_widgets["text_inputs"].append(self.queue_list)

        toggle_queue = self._create_resize_grip(frame, self.queue_list, widget_type="lines", min_val=2, max_val=40, default_val=4, max_toggle=20, name="queue")
        toggle_queue_holder.append(toggle_queue)

        q_btn_row = tk.Frame(frame, bg=t["bg"])
        q_btn_row.pack(fill="x", padx=8, pady=5)
        self.themed_widgets["bg_frames"].append(q_btn_row)

        self.run_btn = self._btn(q_btn_row, "▶  Run", self._run_queue, accent=True)
        self.run_btn.pack(side="left", padx=(0, 4))
        self.run_btn.bind("<Double-Button-1>", self._on_run_btn_double_click)

        self.pause_btn = self._btn(q_btn_row, "⏸  Pause", self._toggle_pause)
        self.pause_btn.pack(side="left", padx=(0, 4))
        self.pause_btn.config(state="disabled")

        self.stop_btn = self._btn(q_btn_row, "⏹  Stop", self._stop_scan, danger=True)
        self.stop_btn.pack(side="left", padx=(0, 4))
        self.stop_btn.config(state="disabled")

        self.dedup_q_btn = self._btn(q_btn_row, "🧹 Dedup", self._deduplicate_queue)
        self.dedup_q_btn.pack(side="left", padx=(4, 0))

        self.del_q_btn = self._btn(q_btn_row, "✕ Remove", self._remove_selected_from_queue)
        self.del_q_btn.pack(side="left", padx=(4, 0))

        self.clear_q_btn = self._btn(q_btn_row, "🗑 Clear", self._clear_queue)
        self.clear_q_btn.pack(side="right")

        def _bind_left_mousewheel_recursive(w):
            try:
                w.bind("<MouseWheel>", _on_left_mousewheel, add="+")
            except Exception:
                pass
            for child in w.winfo_children():
                # Avoid overriding special scrollable child widgets
                if child not in (getattr(self, "store_text", None), getattr(self, "excl_canvas", None), getattr(self, "brand_tree", None)):
                    _bind_left_mousewheel_recursive(child)

        self.after(300, lambda: _bind_left_mousewheel_recursive(frame))

        return container

    # ── RIGHT PANEL ───────────────────────────────────────────────────────────
    def _build_right_panel(self, parent):
        t = self.theme
        frame = tk.Frame(parent, bg=t["bg"])
        self.themed_widgets["bg_frames"].append(frame)

        # toolbar
        toolbar = tk.Frame(frame, bg=t["panel"], pady=6)
        toolbar.pack(fill="x")
        self.themed_widgets["panel_frames"].append(toolbar)

        res_lbl = tk.Label(toolbar, text="Results", font=FONT_HEAD, bg=t["panel"], fg=t["text"])
        res_lbl.pack(side="left", padx=12)
        self.themed_widgets["text_labels"].append(res_lbl)

        self.result_count = tk.StringVar(value="0 listings")
        count_lbl = tk.Label(toolbar, textvariable=self.result_count,
                             bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        count_lbl.pack(side="left", padx=8)
        self.themed_widgets["subtext_labels"].append(count_lbl)

        # Thumbnail view size selector
        th_lbl = tk.Label(toolbar, text="Thumbnails:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        th_lbl.pack(side="left", padx=(8, 2))
        self.themed_widgets["subtext_labels"].append(th_lbl)

        self.thumb_size_combo = ttk.Combobox(toolbar, textvariable=self.thumb_size_var,
                                             values=list(THUMB_CONFIG.keys()),
                                             width=14, state="readonly", font=FONT_SM)
        self.thumb_size_combo.pack(side="left", padx=(0, 8))
        self.thumb_size_combo.bind("<<ComboboxSelected>>", self._on_thumb_size_changed)

        # Primary Action: Export to Excel (Packed FIRST on right so it is anchored to the far right and NEVER clipped)
        self._btn(toolbar, "💾 Export to Excel", self._export, accent=True).pack(side="right", padx=(4, 2))
        self._btn(toolbar, "🌐 Multi-Locale", self._open_multi_locale_expander, accent=False).pack(side="right", padx=2)
        self._btn(toolbar, "📋 Copy URLs", self._copy_all_listing_urls).pack(side="right", padx=2)
        self._btn(toolbar, "🌍 Threat Intel", self._enrich_seller_threat_intel, accent=False).pack(side="right", padx=2)
        self._btn(toolbar, "🔗 Network Scan", self._open_connected_network_scanner, accent=False).pack(side="right", padx=2)
        self._btn(toolbar, "🏪 Enrich", self._enrich_sellers).pack(side="right", padx=2)
        self._btn(toolbar, "✕ Remove", self._remove_selected_results).pack(side="right", padx=2)
        self._btn(toolbar, "🗑 Clear", self._clear_results, danger=True).pack(side="right", padx=2)

        # ── 1.5 Live Search Filter Bar ────────────────────────────────────────
        filter_bar = tk.Frame(frame, bg=t["panel"], pady=4, padx=8)
        filter_bar.pack(side="top", fill="x", padx=4, pady=(2, 1))
        self.themed_widgets["panel_frames"].append(filter_bar)

        # Live search filter with column selector & negative modifier syntax
        f_lbl = tk.Label(filter_bar, text="🔍 Filter:", font=FONT_SM, bg=t["panel"], fg=t["accent"])
        f_lbl.pack(side="left", padx=(0, 4))
        self.themed_widgets["section_labels"].append(f_lbl)

        self.filter_col_var = tk.StringVar(value="Title")
        filter_cols = ["Title", "Seller", "Origin", "Threat Intel", "Item ID", "Brand", "Product Type", "Price", "Location", "All Columns"]
        self.filter_col_combo = ttk.Combobox(filter_bar, textvariable=self.filter_col_var,
                                             values=filter_cols, width=12, state="readonly", font=FONT_SM)
        self.filter_col_combo.pack(side="left", padx=(0, 4))
        self.filter_col_combo.bind("<<ComboboxSelected>>", lambda e: self._repopulate_results_table())

        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", self._on_filter_changed)
        self.filter_entry = tk.Entry(filter_bar, textvariable=self.filter_var, width=18,
                                     bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                     relief="flat", font=FONT_SM)
        self.filter_entry.pack(side="left", padx=(0, 4), fill="x", expand=True)
        self.themed_widgets["text_inputs"].append(self.filter_entry)

        self.filter_high_risk_var = tk.BooleanVar(value=False)
        self.hr_cb = tk.Checkbutton(filter_bar, text="🚨 High-Risk / 3PL Only", variable=self.filter_high_risk_var,
                                    command=self._repopulate_results_table, bg=t["panel"], fg=t["danger"],
                                    selectcolor=t["entry_bg"], activebackground=t["panel"], font=FONT_SM)
        self.hr_cb.pack(side="left", padx=(2, 4))
        self.themed_widgets["checks"].append(self.hr_cb)

        self._btn(filter_bar, "✕ Clear", self._clear_filter).pack(side="left", padx=(0, 4))
        self._btn(filter_bar, "✓ Select All Visible", self._select_all_visible).pack(side="left", padx=(0, 4))
        self._btn(filter_bar, "🧹 Dedupe", self._deduplicate_results).pack(side="left", padx=(0, 0))

        # ── 1.6 Bulk Classification & Tagging Toolbar ─────────────────────────
        tag_bar = tk.Frame(frame, bg=t["panel"], pady=4, padx=8)
        tag_bar.pack(side="top", fill="x", padx=4, pady=(1, 2))
        self.themed_widgets["panel_frames"].append(tag_bar)

        tag_lbl = tk.Label(tag_bar, text="🏷️ Bulk Tag Selected:", font=("Segoe UI", 9, "bold"),
                           bg=t["panel"], fg=t["text"])
        tag_lbl.pack(side="left", padx=(0, 8))
        self.themed_widgets["text_labels"].append(tag_lbl)

        b_lbl = tk.Label(tag_bar, text="Brand:", font=FONT_SM, bg=t["panel"], fg=t["subtext"])
        b_lbl.pack(side="left", padx=(0, 3))
        self.themed_widgets["subtext_labels"].append(b_lbl)

        self.bulk_brand_var = tk.StringVar(value="(No change)")
        self.bulk_brand_combo = ttk.Combobox(tag_bar, textvariable=self.bulk_brand_var,
                                             width=16, state="readonly", font=FONT_SM)
        self.bulk_brand_combo.pack(side="left", padx=(0, 10))

        pt_lbl = tk.Label(tag_bar, text="Product Type:", font=FONT_SM, bg=t["panel"], fg=t["subtext"])
        pt_lbl.pack(side="left", padx=(0, 3))
        self.themed_widgets["subtext_labels"].append(pt_lbl)

        self.bulk_product_var = tk.StringVar(value="(Select or type...)")
        product_categories = [
            "(Select or type...)",
            "Accessories",
            "Air Filters",
            "Air Intake & Fuel Delivery",
            "Airbag Components",
            "Airbag Covers",
            "Brakes",
            "Decals",
            "Diagnostic Systems",
            "Emblems",
            "Engines & Components",
            "Exhausts & Exhaust Parts",
            "Exterior Lighting",
            "Exterior Parts",
            "Grilles",
            "Ignition Systems",
            "Interior Parts",
            "Merchandise",
            "Oil Filters",
            "Suspension & Steering",
            "Transmission & Drivetrain",
            "Wheel Caps",
        ]
        self.bulk_product_combo = ttk.Combobox(tag_bar, textvariable=self.bulk_product_var,
                                               values=product_categories, width=22, font=FONT_SM)
        self.bulk_product_combo.pack(side="left", padx=(0, 8))

        self._btn(tag_bar, "⚡ Apply to Selected", self._apply_bulk_tag, accent=True).pack(side="left")

        # ── 1. Activity Log panel (docked firmly to the bottom) ──────────────
        log_frame = tk.Frame(frame, bg=t["bg"])
        log_frame.pack(side="bottom", fill="x", padx=4, pady=(2, 4))
        self.themed_widgets["bg_frames"].append(log_frame)

        log_header = tk.Frame(log_frame, bg=t["bg"])
        log_header.pack(fill="x", padx=4, pady=(2, 0))
        self.themed_widgets["bg_frames"].append(log_header)

        act_lbl = tk.Label(log_header, text="Activity Log", font=FONT_SM, bg=t["bg"], fg=t["subtext"])
        act_lbl.pack(side="left")
        self.themed_widgets["subtext_labels"].append(act_lbl)

        self._btn(log_header, "💾 Export Log", self._export_job_log).pack(side="right")
        self._btn(log_header, "🗑 Clear Log",  self._clear_log).pack(side="right", padx=4)

        log_text_frame = tk.Frame(log_frame, bg=t["bg"])
        log_text_frame.pack(fill="x", padx=4, pady=(2, 0))
        self.themed_widgets["bg_frames"].append(log_text_frame)

        self.log_text = tk.Text(log_text_frame, height=6, bg=t["panel"], fg=t["text"],
                                font=FONT_SM, relief="flat", state="disabled",
                                wrap="word")
        log_vsb = ttk.Scrollbar(log_text_frame, orient="vertical",
                                 command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_vsb.set)
        log_vsb.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)
        self.themed_widgets["text_inputs"].append(self.log_text)

        # ── 2. Results Table Container (takes all remaining upper space) ──────
        table_frame = tk.Frame(frame, bg=t["bg"])
        table_frame.pack(side="top", fill="both", expand=True, padx=4, pady=(2, 0))
        self.themed_widgets["bg_frames"].append(table_frame)

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        cols = ("brand", "product_type", "title", "item_id", "price", "seller", "seller_origin", "threat_badge", "location", "thumbnail", "url")
        init_size = self.thumb_size_var.get()
        init_cfg = THUMB_CONFIG.get(init_size, THUMB_CONFIG["Medium (100px)"])
        self.result_tree = ttk.Treeview(table_frame, columns=cols, show=init_cfg["show"], selectmode="extended", style="Results.Treeview")
        self.result_tree.heading("#0", text="Preview" if init_cfg["img_size"] > 0 else "", anchor="center")
        self.result_tree.column("#0", width=init_cfg["col_width"], minwidth=init_cfg["col_width"], anchor="center")
        saved_col_widths = self.data_store.get_setting("column_widths", {})
        col_widths = {
            "brand": 75,
            "product_type": 110,
            "title": 260,
            "item_id": 100,
            "price": 70,
            "seller": 100,
            "seller_origin": 85,
            "threat_badge": 175,
            "location": 110,
            "thumbnail": 100,
            "url": 120
        }
        for c in cols:
            w = saved_col_widths.get(c, col_widths.get(c, 100)) if isinstance(saved_col_widths, dict) else col_widths.get(c, 100)
            self.result_tree.heading(c, text=self.col_labels[c],
                                     command=lambda _c=c: self._sort_by_column(_c))
            self.result_tree.column(c, width=w, minwidth=45)
        self._style_tree(self.result_tree)

        vsb = ttk.Scrollbar(table_frame, orient="vertical",   command=self.result_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.result_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.result_tree.bind("<Double-1>", self._open_url)
        self.result_tree.bind("<Button-3>", self._show_result_context_menu)
        self.result_tree.bind("<Delete>", lambda e: self._remove_selected_results())
        self.result_tree.bind("<BackSpace>", lambda e: self._remove_selected_results())
        self.result_tree.bind("<Control-a>", self._select_all_results)
        self.result_tree.bind("<Control-A>", self._select_all_results)
        self.result_tree.bind("<<TreeviewSelect>>", self._on_result_tree_select)
        
        # Hover thumbnail event bindings
        self.result_tree.bind("<Motion>", self._on_tree_mouse_motion)
        self.result_tree.bind("<Leave>",  self._hide_preview_popup)

        return frame

    # ══════════════════════════════════════════════════════════════════════════
    #  FULL DYNAMIC THEME ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    def _on_theme_changed(self, event=None):
        selected_name = self.theme_var.get()
        for k, v in THEMES.items():
            if v["name"] == selected_name:
                self.current_theme_key = k
                self.theme = v
                self.data_store.set_setting("theme", k)
                self._apply_full_theme()
                break
        try:
            self.theme_combo.selection_clear()
            self.focus_set()
        except Exception:
            pass

    def _apply_full_theme(self):
        t = self.theme
        self.configure(bg=t["bg"])

        # 1. Background frames
        for f in self.themed_widgets["bg_frames"]:
            try: f.configure(bg=t["bg"])
            except Exception: pass

        # 2. Panel frames
        for f in self.themed_widgets["panel_frames"]:
            try: f.configure(bg=t["panel"])
            except Exception: pass

        # 3. Section labels & Title
        for lbl in self.themed_widgets["section_labels"]:
            try: lbl.configure(fg=t["accent"], bg=lbl.master["bg"])
            except Exception: pass

        if hasattr(self, "subtitle_lbl") and self.subtitle_lbl.winfo_exists():
            sub_text = THEME_SUBHEADERS.get(self.current_theme_key, "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER")
            self.subtitle_lbl.configure(text=sub_text, fg=t.get("accent2", t["subtext"]), bg=self.subtitle_lbl.master["bg"])

        # 4. Dividers
        for div in self.themed_widgets["dividers"]:
            try: div.configure(bg=t["border"])
            except Exception: pass

        # 5. Standard Text Labels
        for lbl in self.themed_widgets["text_labels"]:
            try: lbl.configure(fg=t["text"], bg=lbl.master["bg"])
            except Exception: pass

        # 6. Subtext Labels
        for lbl in self.themed_widgets["subtext_labels"]:
            try: lbl.configure(fg=t["subtext"], bg=lbl.master["bg"])
            except Exception: pass

        # 7. Text Inputs, Entries, and Listboxes
        for inp in self.themed_widgets["text_inputs"]:
            try:
                sel_fg = t.get("select_fg", "white")
                if isinstance(inp, tk.Listbox):
                    inp.configure(
                        bg=t["entry_bg"],
                        fg=t["text"],
                        selectbackground=t["accent"],
                        selectforeground=sel_fg
                    )
                elif isinstance(inp, tk.Text):
                    bg_col = t["panel"] if inp == self.log_text else t["entry_bg"]
                    inp.configure(
                        bg=bg_col,
                        fg=t["text"],
                        insertbackground=t["text"],
                        selectbackground=t["accent"],
                        selectforeground=sel_fg
                    )
                elif isinstance(inp, tk.Entry):
                    inp.configure(
                        bg=t["entry_bg"],
                        fg=t["text"],
                        insertbackground=t["text"],
                        selectbackground=t["accent"],
                        selectforeground=sel_fg
                    )
            except Exception:
                pass

        # Update placeholder colors if present
        if self.store_text.get("1.0", "end").strip() == self.store_placeholder.strip():
            self.store_text.config(fg=t["subtext"])
        if self.new_excl_entry.get() == "New generic exclusion":
            self.new_excl_entry.config(fg=t["subtext"])

        # 8. Accent Buttons
        for btn in self.themed_widgets["accent_btns"]:
            try: btn.configure(bg=t["accent"], fg=t.get("btn_accent_fg", "black" if t.get("name", "").startswith("⚡") else "white"), activebackground=t["accent2"])
            except Exception: pass

        # 9. Danger Buttons
        for btn in self.themed_widgets["danger_btns"]:
            try: btn.configure(bg=t["danger"], fg="white", activebackground=t["danger"])
            except Exception: pass

        # 10. Normal Buttons
        for btn in self.themed_widgets["normal_btns"]:
            try:
                fg_col = t["btn_normal_fg"]
                btn.configure(bg=t["btn_normal_bg"], fg=fg_col, activebackground=t["border"])
            except Exception: pass

        # 11. Checkboxes
        for cb in self.themed_widgets["checks"]:
            try:
                fg_col = t["danger"] if cb == getattr(self, "hr_cb", None) else t["text"]
                cb.configure(bg=cb.master["bg"], fg=fg_col, selectcolor=t["entry_bg"], activebackground=cb.master["bg"])
            except Exception: pass

        # 12. Exclusion canvas & inner
        try:
            self.excl_canvas.configure(bg=t["entry_bg"], highlightbackground=t["border"])
            self.excl_inner.configure(bg=t["entry_bg"])
        except Exception: pass

        # 13. Treeview & Progressbar Styles
        self._style_tree(self.brand_tree)
        self._style_tree(self.result_tree)
        self.brand_tree.tag_configure("target", foreground=t["success"])
        self.brand_tree.tag_configure("exclude", foreground=t["danger"])
        self.brand_tree.tag_configure("neutral", foreground=t["text"])

        # 14. Activity Log tags
        self.log_text.tag_config("err",  foreground=t["danger"])
        self.log_text.tag_config("info", foreground=t["text"])

        # Dynamic theme-specific button flairs & store placeholder
        if self.current_theme_key == "continental":
            if hasattr(self, "sweep_btn"):
                self.sweep_btn.config(text="⚔️ Issue Excommunicado Order: Queue All Targets")
            if hasattr(self, "run_btn"):
                self.run_btn.config(text="▶ Execute Contracts")
            if hasattr(self, "add_q_btn"):
                self.add_q_btn.config(text="➕ Issue Bounty Contract")
            if hasattr(self, "clean_sweep_btn"):
                self.clean_sweep_btn.config(text="🎯 Excommunicado Sweep")
            if "eBay" in getattr(self, "marketplace_var", tk.StringVar()).get():
                old_ph = getattr(self, "store_placeholder", "")
                self.store_placeholder = "Enter target storefronts (One per line) — High Table contracts..."
                if hasattr(self, "store_text"):
                    curr_txt = self.store_text.get("1.0", "end").strip()
                    if not curr_txt or curr_txt == old_ph.strip() or "store1" in curr_txt:
                        self.store_text.delete("1.0", "end")
                        self.store_text.insert("1.0", self.store_placeholder)
                        self.store_text.config(fg=t["subtext"])
        else:
            if hasattr(self, "sweep_btn"):
                self.sweep_btn.config(text="⚡ 1-Click Sweep: Queue Portfolio for All Stores")
            if hasattr(self, "run_btn"):
                self.run_btn.config(text="▶  Run")
            if hasattr(self, "add_q_btn"):
                self.add_q_btn.config(text="➕ Add to Queue")
            if hasattr(self, "clean_sweep_btn"):
                self.clean_sweep_btn.config(text="🎯 Clean Brand Sweep")
            if "eBay" in getattr(self, "marketplace_var", tk.StringVar()).get():
                old_ph = getattr(self, "store_placeholder", "")
                self.store_placeholder = "https://www.ebay.com/str/store1\nstore2\nseller3"
                if hasattr(self, "store_text"):
                    curr_txt = self.store_text.get("1.0", "end").strip()
                    if not curr_txt or curr_txt == old_ph.strip() or "High Table contracts" in curr_txt:
                        self.store_text.delete("1.0", "end")
                        self.store_text.insert("1.0", self.store_placeholder)
                        self.store_text.config(fg=t["subtext"])

        # Refresh Trees & Exclusions list with new colors
        self._refresh_brand_tree()
        self._refresh_exclusion_list()
        self._repopulate_results_table()
        self._hide_preview_popup()
        self._apply_dark_titlebar()
        self._log(f"Theme switched to: {t['name']}")

    def _apply_dark_titlebar(self, win=None):
        """Enable immersive dark mode title bar and custom caption colors via Windows DWM API."""
        target = win if win is not None else self
        try:
            target.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(target.winfo_id())
            if not hwnd:
                hwnd = target.winfo_id()

            # 1. Immersive dark mode (Windows 10 1809+ / Windows 11)
            for attr in (19, 20):
                v = ctypes.c_int(2)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))

            # 2. Windows 11 custom title bar caption & text colors (Build 22000+)
            t = self.theme
            bg_hex = t.get("panel", t.get("bg", "#0A0B0E"))
            fg_hex = t.get("text", "#FFFFFF")

            if bg_hex and len(bg_hex) == 7:
                r = int(bg_hex[1:3], 16)
                g = int(bg_hex[3:5], 16)
                b = int(bg_hex[5:7], 16)
                color_ref = (b << 16) | (g << 8) | r
                c_color = ctypes.c_int(color_ref)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(c_color), ctypes.sizeof(c_color))

            if fg_hex and len(fg_hex) == 7:
                r = int(fg_hex[1:3], 16)
                g = int(fg_hex[3:5], 16)
                b = int(fg_hex[5:7], 16)
                t_color = (b << 16) | (g << 8) | r
                c_text = ctypes.c_int(t_color)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(c_text), ctypes.sizeof(c_text))
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════════════
    #  WIDGET HELPERS
    # ══════════════════════════════════════════════════════════════════════════
    def _section(self, parent, text, toggle_cmd=None):
        t = self.theme
        f = tk.Frame(parent, bg=t["bg"])
        f.pack(fill="x", padx=8, pady=(6, 2))
        self.themed_widgets["bg_frames"].append(f)

        lbl = tk.Label(f, text=text, font=FONT_HEAD, bg=t["bg"], fg=t["accent"],
                       cursor="hand2" if toggle_cmd else "")
        lbl.pack(side="left")
        self.themed_widgets["section_labels"].append(lbl)

        div = tk.Frame(f, bg=t["border"], height=1)
        div.pack(side="left", fill="x", expand=True, padx=6)
        self.themed_widgets["dividers"].append(div)

        if toggle_cmd:
            btn = tk.Button(f, text="⤢", command=toggle_cmd, bg=t["bg"], fg=t["subtext"],
                            relief="flat", bd=0, font=("Segoe UI", 8, "bold"), cursor="hand2",
                            padx=4, pady=0, activebackground=t["bg"], activeforeground=t["accent"])
            btn.pack(side="right")
            self.themed_widgets["text_labels"].append(btn)
            lbl.bind("<Double-Button-1>", lambda e: toggle_cmd())

    def _create_resize_grip(self, parent, target_widget, widget_type="lines", min_val=2, max_val=40, default_val=4, max_toggle=20, name="widget"):
        t = self.theme
        grip_frame = tk.Frame(parent, bg=t["bg"], height=8, cursor="size_ns")
        grip_frame.pack(fill="x", padx=8, pady=(1, 4))
        self.themed_widgets["bg_frames"].append(grip_frame)

        grip_line = tk.Frame(grip_frame, bg=t["border"], height=2, cursor="size_ns")
        grip_line.pack(fill="x", pady=(3, 3))
        self.themed_widgets["dividers"].append(grip_line)

        dot = tk.Label(grip_line, text="···", font=("Segoe UI", 6, "bold"), bg=t["border"], fg=t["subtext"], cursor="size_ns")
        dot.place(relx=0.5, rely=0.5, anchor="center")

        drag_state = {
            "start_y": 0,
            "start_val": default_val,
            "current_val": default_val,
            "is_max": False
        }

        def on_enter(e):
            try:
                grip_line.configure(bg=self.theme["accent"])
                dot.configure(bg=self.theme["accent"], fg="#000000" if self.theme.get("btn_accent_fg") else "#ffffff")
            except Exception:
                pass

        def on_leave(e):
            try:
                grip_line.configure(bg=self.theme["border"])
                dot.configure(bg=self.theme["border"], fg=self.theme["subtext"])
            except Exception:
                pass

        def on_press(e):
            drag_state["start_y"] = e.y_root
            if widget_type in ("lines", "treeview"):
                try:
                    drag_state["start_val"] = int(target_widget.cget("height"))
                except Exception:
                    drag_state["start_val"] = default_val
            elif widget_type == "canvas_px":
                try:
                    drag_state["start_val"] = int(target_widget.cget("height"))
                except Exception:
                    drag_state["start_val"] = default_val

        def on_motion(e):
            delta = e.y_root - drag_state["start_y"]
            if widget_type in ("lines", "treeview"):
                step = 18 if widget_type == "lines" else 24
                new_v = max(min_val, min(max_val, drag_state["start_val"] + int(delta / step)))
                if new_v != drag_state["current_val"]:
                    drag_state["current_val"] = new_v
                    target_widget.configure(height=new_v)
                    if hasattr(self, "_update_left_scrollregion"):
                        self._update_left_scrollregion()
            elif widget_type == "canvas_px":
                new_v = max(min_val, min(max_val, drag_state["start_val"] + delta))
                if new_v != drag_state["current_val"]:
                    drag_state["current_val"] = new_v
                    target_widget.configure(height=new_v)
                    if hasattr(self, "_update_left_scrollregion"):
                        self._update_left_scrollregion()

        def toggle_maximize():
            if drag_state["is_max"]:
                target_widget.configure(height=default_val)
                drag_state["current_val"] = default_val
                drag_state["is_max"] = False
            else:
                target_widget.configure(height=max_toggle)
                drag_state["current_val"] = max_toggle
                drag_state["is_max"] = True
            if hasattr(self, "_update_left_scrollregion"):
                self._update_left_scrollregion()

        for w in (grip_frame, grip_line, dot):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<ButtonPress-1>", on_press)
            w.bind("<B1-Motion>", on_motion)
            w.bind("<Double-Button-1>", lambda e: toggle_maximize())

        return toggle_maximize

    def _entry(self, parent, placeholder=""):
        t = self.theme
        e = tk.Entry(parent, bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                     relief="flat", font=FONT)
        if placeholder:
            e.insert(0, placeholder)
            e.config(fg=t["subtext"])
            e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder: self._clear_ph(ev, en, ph))
            e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder: self._restore_ph(ev, en, ph))
        self.themed_widgets["text_inputs"].append(e)
        return e

    def _clear_ph(self, ev, entry, ph):
        if entry.get() == ph:
            entry.delete(0, "end")
            entry.config(fg=self.theme["text"])

    def _restore_ph(self, ev, entry, ph):
        if not entry.get():
            entry.insert(0, ph)
            entry.config(fg=self.theme["subtext"])

    def _clear_store_ph(self, ev):
        txt = self.store_text.get("1.0", "end").strip()
        if (txt == self.store_placeholder.strip() or 
            "store1" in txt or 
            "High Table" in txt or
            "Global Wholesale Search" in txt or 
            "aliexpress.com/store/110123456" in txt):
            self.store_text.delete("1.0", "end")
            self.store_text.config(fg=self.theme["text"])

    def _restore_store_ph(self, ev):
        if not self.store_text.get("1.0", "end").strip():
            self.store_text.insert("1.0", self.store_placeholder)
            self.store_text.config(fg=self.theme["subtext"])

    def _on_market_changed(self, event=None):
        market = self.marketplace_var.get()
        t = self.theme
        current_text = self.store_text.get("1.0", "end").strip()

        if hasattr(self, "meli_login_btn"):
            if "Mercado Libre" in market:
                self.meli_login_btn.pack(side="left", padx=(0, 4), after=self.market_combo)
            else:
                self.meli_login_btn.pack_forget()

        if "AliExpress" in market:
            self.store_placeholder = "🌐 Global Wholesale Search: https://www.aliexpress.com/w/wholesale-\n(Leave blank to sweep entire AliExpress marketplace, or enter specific store URLs)"
            if not current_text or "ebay.com" in current_text or "wish.com" in current_text or "temu.com" in current_text or "mercadolibre" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🌐 Switched platform to: AliExpress.com (Global Wholesale & Store Search active)")
        elif "Wish" in market:
            self.store_placeholder = "🌐 Global Wish Search: https://www.wish.com/search/\n(Leave blank to sweep entire Wish marketplace, or enter specific merchant URLs)"
            if not current_text or "ebay.com" in current_text or "aliexpress.com" in current_text or "temu.com" in current_text or "mercadolibre" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🌠 Switched platform to: Wish.com (Global Catalog & Merchant Sweeps active)")
        elif "Temu" in market:
            self.store_placeholder = "🌐 Global Temu Search: https://www.temu.com/search_result.html\n(Leave blank to sweep entire Temu marketplace, or enter specific mall URLs)"
            if not current_text or "ebay.com" in current_text or "aliexpress.com" in current_text or "wish.com" in current_text or "mercadolibre" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🟠 Switched platform to: Temu.com (Global Catalog & Mall Sweeps active)")
        elif "Mercado Libre" in market:
            self.store_placeholder = "🌐 Global Mercado Libre Search: https://listado.mercadolibre.com.mx/\n(Leave blank to sweep entire Mercado Libre marketplace, or enter specific seller/store URLs)"
            if not current_text or "ebay.com" in current_text or "aliexpress.com" in current_text or "wish.com" in current_text or "temu.com" in current_text or "redbubble.com" in current_text or "printerval.com" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🇲🇽 Switched platform to: Mercado Libre (Latin America Search active). Tip: Click '🔑 MeLi Login' to log in once.")
        elif "Redbubble" in market:
            self.store_placeholder = "🌐 Global Redbubble Search: https://www.redbubble.com/shop/\n(Leave blank to sweep entire Redbubble catalog, or enter specific artist shop URLs: https://www.redbubble.com/people/artist/shop)"
            if not current_text or "ebay.com" in current_text or "aliexpress.com" in current_text or "wish.com" in current_text or "temu.com" in current_text or "mercadolibre" in current_text or "printerval.com" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🎨 Switched platform to: Redbubble.com (Global Catalog & Artist Sweeps active)")
        elif "Printerval" in market:
            self.store_placeholder = "🌐 Global Printerval Search: https://printerval.com/search\n(Leave blank to sweep entire Printerval catalog, or enter specific shop URLs: https://printerval.com/shop/creator)"
            if not current_text or "ebay.com" in current_text or "aliexpress.com" in current_text or "wish.com" in current_text or "temu.com" in current_text or "mercadolibre" in current_text or "redbubble.com" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("👕 Switched platform to: Printerval.com (Global Catalog & Creator Sweeps active)")
        else:
            self.store_placeholder = "https://www.ebay.com/str/store1\nstore2\nseller3"
            if not current_text or "aliexpress.com" in current_text or "wish.com" in current_text or "temu.com" in current_text or "mercadolibre" in current_text or "redbubble.com" in current_text or "printerval.com" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🛒 Switched platform to: eBay.com (Store & Seller Search active)")

    def _get_stores_from_input(self):
        """Parse stores from input text box, safely ignoring placeholders and handling Global platform modes."""
        raw_text = self.store_text.get("1.0", "end").strip()
        market = self.marketplace_var.get()
        is_ali = "AliExpress" in market
        is_wish = "Wish" in market
        is_temu = "Temu" in market
        is_meli = "Mercado Libre" in market
        is_redbubble = "Redbubble" in market
        is_printerval = "Printerval" in market

        if (not raw_text or 
            raw_text == self.store_placeholder.strip() or 
            "Global" in raw_text or 
            "store1" in raw_text or 
            "leave blank to sweep" in raw_text.lower()):
            if is_ali:
                return ["🌐 Global AliExpress Search"]
            if is_wish:
                return ["🌐 Global Wish Search"]
            if is_temu:
                return ["🌐 Global Temu Search"]
            if is_meli:
                return ["🌐 Global Mercado Libre Search"]
            if is_redbubble:
                return ["🌐 Global Redbubble Search"]
            if is_printerval:
                return ["🌐 Global Printerval Search"]
            return []

        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        valid_stores = []
        ignored_exact = {
            "https://www.ebay.com/str/store1",
            "store2",
            "seller3",
            "https://www.aliexpress.com/store/110123456",
            "https://www.aliexpress.com/w/wholesale-",
            "https://www.wish.com/search/",
            "https://www.temu.com/search_result.html",
            "https://listado.mercadolibre.com.mx/",
            "https://www.redbubble.com/shop/",
            "https://printerval.com/search"
        }
        for l in lines:
            low = l.lower()
            if low in ignored_exact or "leave blank to sweep" in low or "global" in low:
                continue
            valid_stores.append(l)

        if not valid_stores:
            if is_ali:
                return ["🌐 Global AliExpress Search"]
            if is_wish:
                return ["🌐 Global Wish Search"]
            if is_temu:
                return ["🌐 Global Temu Search"]
            if is_meli:
                return ["🌐 Global Mercado Libre Search"]
            if is_redbubble:
                return ["🌐 Global Redbubble Search"]
            if is_printerval:
                return ["🌐 Global Printerval Search"]

        return valid_stores

    def _btn(self, parent, text, cmd, accent=False, danger=False):
        t = self.theme
        if accent:
            bg = t["accent"]
            fg = t.get("btn_accent_fg", "black" if t.get("name", "").startswith("⚡") else "white")
            active_bg = t["accent2"]
        elif danger:
            bg = t["danger"]
            fg = "white"
            active_bg = t["danger"]
        else:
            bg = t["btn_normal_bg"]
            fg = t["btn_normal_fg"]
            active_bg = t["border"]

        btn = tk.Button(parent, text=text, command=cmd,
                        bg=bg, fg=fg, relief="flat",
                        font=FONT_SM, padx=8, pady=3,
                        activebackground=active_bg, cursor="hand2")

        if accent:
            self.themed_widgets["accent_btns"].append(btn)
        elif danger:
            self.themed_widgets["danger_btns"].append(btn)
        else:
            self.themed_widgets["normal_btns"].append(btn)

        return btn

    def _style_tree(self, tree):
        t = self.theme
        style = ttk.Style()
        style.theme_use("clam")
        
        # Base treeview styling (Brand list, 24px)
        style.configure("Treeview",
                        background=t["entry_bg"], foreground=t["text"],
                        fieldbackground=t["entry_bg"],
                        bordercolor=t["border"],
                        darkcolor=t["border"],
                        lightcolor=t["border"],
                        rowheight=24,
                        font=FONT_SM)
        style.configure("Treeview.Heading",
                        background=t["panel"], foreground=t["text"],
                        font=FONT_SM, relief="flat")
        style.map("Treeview", background=[("selected", t["select_bg"])],
                              foreground=[("selected", t["select_fg"])])

        # Results treeview with configurable rowheight for inline thumbnails
        size_key = self.thumb_size_var.get() if hasattr(self, "thumb_size_var") else "Medium (100px)"
        cfg = THUMB_CONFIG.get(size_key, THUMB_CONFIG["Medium (100px)"])
        style.configure("Results.Treeview",
                        background=t["entry_bg"], foreground=t["text"],
                        fieldbackground=t["entry_bg"],
                        bordercolor=t["border"],
                        darkcolor=t["border"],
                        lightcolor=t["border"],
                        rowheight=cfg["rowheight"],
                        font=FONT_SM)
        style.configure("Results.Treeview.Heading",
                        background=t["panel"], foreground=t["text"],
                        font=FONT_SM, relief="flat")
        style.map("Results.Treeview", background=[("selected", t["select_bg"])],
                                     foreground=[("selected", t["select_fg"])])

        # Radiobutton style
        style.configure("TRadiobutton",
                        background=t["bg"], foreground=t["text"])
        style.map("TRadiobutton",
                  background=[("active", t["bg"])],
                  foreground=[("active", t["text"])])

        # Progressbar style
        style.configure("TProgressbar",
                        background=t["accent"],
                        troughcolor=t["entry_bg"])

        # Scrollbar styles (Flat, unified, zero white highlights or blurred grip bars)
        style.configure("TScrollbar",
                        background=t["panel"],
                        troughcolor=t["entry_bg"],
                        bordercolor=t["border"],
                        darkcolor=t["panel"],
                        lightcolor=t["panel"],
                        arrowcolor=t["accent"],
                        gripcount=0,
                        relief="flat")
        style.map("TScrollbar",
                  background=[("active", t["accent"]), ("pressed", t.get("accent2", t["accent"]))],
                  darkcolor=[("active", t["panel"]), ("pressed", t["panel"])],
                  lightcolor=[("active", t["panel"]), ("pressed", t["panel"])],
                  bordercolor=[("active", t["border"]), ("pressed", t["border"])])

        style.configure("Vertical.TScrollbar",
                        background=t["panel"],
                        troughcolor=t["entry_bg"],
                        bordercolor=t["border"],
                        darkcolor=t["panel"],
                        lightcolor=t["panel"],
                        arrowcolor=t["accent"],
                        gripcount=0,
                        relief="flat")
        style.map("Vertical.TScrollbar",
                  background=[("active", t["accent"]), ("pressed", t.get("accent2", t["accent"]))],
                  darkcolor=[("active", t["panel"]), ("pressed", t["panel"])],
                  lightcolor=[("active", t["panel"]), ("pressed", t["panel"])],
                  bordercolor=[("active", t["border"]), ("pressed", t["border"])])

        style.configure("Horizontal.TScrollbar",
                        background=t["panel"],
                        troughcolor=t["entry_bg"],
                        bordercolor=t["border"],
                        darkcolor=t["panel"],
                        lightcolor=t["panel"],
                        arrowcolor=t["accent"],
                        gripcount=0,
                        relief="flat")
        style.map("Horizontal.TScrollbar",
                  background=[("active", t["accent"]), ("pressed", t.get("accent2", t["accent"]))],
                  darkcolor=[("active", t["panel"]), ("pressed", t["panel"])],
                  lightcolor=[("active", t["panel"]), ("pressed", t["panel"])],
                  bordercolor=[("active", t["border"]), ("pressed", t["border"])])

        # Combobox style
        is_bright = t.get("name", "").startswith("⚡") or t.get("name", "").startswith("🪙")
        style.configure("TCombobox",
                        fieldbackground=t["entry_bg"],
                        background=t["panel"],
                        foreground=t["text"],
                        selectbackground=t["accent"],
                        selectforeground="black" if is_bright else "white",
                        bordercolor=t["border"],
                        darkcolor=t["border"],
                        lightcolor=t["border"],
                        arrowcolor=t["accent"])
        style.map("TCombobox",
                  fieldbackground=[("readonly", t["entry_bg"])],
                  selectbackground=[("readonly", t["accent"])],
                  selectforeground=[("readonly", "black" if is_bright else "white")],
                  background=[("readonly", t["panel"])],
                  foreground=[("readonly", t["text"])])

        # Notebook & Tab styling (Eliminates white lines, bevels & borders across all tabbed views)
        style.configure("TNotebook",
                        background=t["bg"],
                        bordercolor=t["border"],
                        darkcolor=t["bg"],
                        lightcolor=t["bg"],
                        tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab",
                        background=t["panel"],
                        foreground=t["text"],
                        bordercolor=t["border"],
                        darkcolor=t["panel"],
                        lightcolor=t["panel"],
                        padding=[14, 6],
                        font=FONT_SM)
        style.map("TNotebook.Tab",
                  background=[("selected", t["accent"]), ("active", t["border"])],
                  foreground=[("selected", t.get("btn_accent_fg", "black" if t.get("name", "").startswith("⚡") else "white")),
                              ("active", t["text"])],
                  darkcolor=[("selected", t["accent"]), ("active", t["border"])],
                  lightcolor=[("selected", t["accent"]), ("active", t["border"])],
                  bordercolor=[("selected", t["accent"]), ("active", t["border"])])

        # Style About dialog specific notebook tabs identically
        style.configure("About.TNotebook",
                        background=t["bg"],
                        bordercolor=t["border"],
                        darkcolor=t["bg"],
                        lightcolor=t["bg"],
                        tabmargins=[2, 5, 2, 0])
        style.configure("About.TNotebook.Tab",
                        background=t["panel"],
                        foreground=t["text"],
                        bordercolor=t["border"],
                        darkcolor=t["panel"],
                        lightcolor=t["panel"],
                        padding=[16, 8],
                        font=("Segoe UI", 9, "bold"))
        style.map("About.TNotebook.Tab",
                  background=[("selected", t["accent"]), ("active", t["border"])],
                  foreground=[("selected", t.get("btn_accent_fg", "black" if t.get("name", "").startswith("⚡") else "white")),
                              ("active", t["text"])],
                  darkcolor=[("selected", t["accent"]), ("active", t["border"])],
                  lightcolor=[("selected", t["accent"]), ("active", t["border"])],
                  bordercolor=[("selected", t["accent"]), ("active", t["border"])])

        # Global Tk option database for dropdown popup listboxes (Tkinter TCombobox popdown)
        try:
            self.option_add("*TCombobox*Listbox.background", t["entry_bg"])
            self.option_add("*TCombobox*Listbox.foreground", t["text"])
            self.option_add("*TCombobox*Listbox.selectBackground", t["accent"])
            self.option_add("*TCombobox*Listbox.selectForeground", "black" if is_bright else "white")
            self.option_add("*TCombobox*Listbox.font", FONT_SM)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════════════
    #  BRAND MANAGEMENT & TARGETING
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh_brand_tree(self):
        self.brand_tree.delete(*self.brand_tree.get_children())
        brands = self.data_store.get_brands()
        for parent_name, data in brands.items():
            mode = self.brand_states.get(parent_name, "neutral")
            pid = self.brand_tree.insert("", "end", iid=parent_name, text=parent_name,
                                         values=("Parent", self._format_mode_label(mode)),
                                         tags=(mode,), open=False)

            # 1. Direct Parent Models (e.g. Camry, Corolla under Toyota; Outback under Subaru)
            for model in data.get("models", []):
                mod_key = f"{parent_name}/{model}"
                mod_mode = self.brand_states.get(mod_key, "neutral")
                self.brand_tree.insert(pid, "end", iid=mod_key, text=model,
                                       values=("Model", self._format_mode_label(mod_mode)),
                                       tags=(mod_mode,))

            # 2. Sub-brands (e.g. Lexus under Toyota; Chevrolet under GM)
            for sub_name, models in data.get("subs", {}).items():
                sub_key = f"{parent_name}/{sub_name}"
                sub_mode = self.brand_states.get(sub_key, "neutral")
                sid = self.brand_tree.insert(pid, "end", iid=sub_key, text=sub_name,
                                              values=("Sub", self._format_mode_label(sub_mode)),
                                              tags=(sub_mode,), open=False)
                for model in models:
                    mod_key = f"{sub_key}/{model}"
                    mod_mode = self.brand_states.get(mod_key, "neutral")
                    self.brand_tree.insert(sid, "end", iid=mod_key, text=model,
                                           values=("Model", self._format_mode_label(mod_mode)),
                                           tags=(mod_mode,))

        self._refresh_bulk_brand_list()
        self._refresh_preset_list()

    def _format_mode_label(self, mode):
        if mode == "target":
            return "🎯 Target"
        elif mode == "exclude":
            return "🚫 Exclude"
        return "⚪ Neutral"

    def _on_tree_double_click(self, event=None):
        """Cycle selected item(s) through: Neutral -> Target -> Exclude -> Neutral."""
        selected = self.brand_tree.selection()
        if not selected:
            return
        for item_id in selected:
            current = self.brand_states.get(item_id, "neutral")
            if current == "neutral":
                new_mode = "target"
            elif current == "target":
                new_mode = "exclude"
            else:
                new_mode = "neutral"
            self._apply_mode(item_id, new_mode)
        self._update_include_preview()

    def _set_selected_mode(self, mode):
        selected = self.brand_tree.selection()
        if not selected:
            messagebox.showinfo("Select", "Select one or more brands/models in the tree first.")
            return
        for item_id in selected:
            self._apply_mode(item_id, mode)
        self._update_include_preview()

    def _apply_mode(self, item_id, mode):
        self.brand_states[item_id] = mode
        item_type = self.brand_tree.item(item_id, "values")[0]
        self.brand_tree.item(item_id, values=(item_type, self._format_mode_label(mode)), tags=(mode,))
        # NOTE: Do NOT cascade to children automatically so parent can be targeted independently

    def _auto_exclude_other_brands(self):
        """Auto-exclude competitor parent brands only."""
        targeted_keys = {k for k, v in self.brand_states.items() if v == "target"}
        if not targeted_keys:
            sel = self.brand_tree.selection()
            if sel:
                for s in sel:
                    self._apply_mode(s, "target")
                targeted_keys = {k for k, v in self.brand_states.items() if v == "target"}

        if not targeted_keys:
            messagebox.showinfo("Target", "Mark or select at least one brand as 🎯 Target first.")
            return

        target_parents = {k.split("/")[0] for k in targeted_keys}
        brands = self.data_store.get_brands()
        excluded_count = 0
        for parent_name in brands.keys():
            if parent_name not in target_parents:
                self._apply_mode(parent_name, "exclude")
                excluded_count += 1

        self._update_include_preview()
        self._log(f"Auto-excluded {excluded_count} competitor brand(s) ({', '.join(target_parents)} targeted).")

    def _auto_exclude_other_models(self):
        """Auto-exclude sibling models/subs under the targeted brand that are not targeted."""
        targeted_keys = {k for k, v in self.brand_states.items() if v == "target"}
        if not targeted_keys:
            sel = self.brand_tree.selection()
            if sel:
                for s in sel:
                    self._apply_mode(s, "target")
                targeted_keys = {k for k, v in self.brand_states.items() if v == "target"}

        if not targeted_keys:
            messagebox.showinfo("Target", "Mark or select at least one model/brand as 🎯 Target first.")
            return

        target_parents = {k.split("/")[0] for k in targeted_keys}
        excluded_count = 0

        for parent_name in target_parents:
            for child_id in self.brand_tree.get_children(parent_name):
                sub_children = self.brand_tree.get_children(child_id)
                if sub_children:
                    # Sub-brand
                    if child_id not in targeted_keys:
                        has_target_sub = any(sc in targeted_keys for sc in sub_children)
                        if not has_target_sub:
                            self._apply_mode(child_id, "exclude")
                            excluded_count += 1
                        else:
                            for sc in sub_children:
                                if sc not in targeted_keys:
                                    self._apply_mode(sc, "exclude")
                                    excluded_count += 1
                else:
                    # Direct model
                    if child_id not in targeted_keys:
                        self._apply_mode(child_id, "exclude")
                        excluded_count += 1

        self._update_include_preview()
        self._log(f"Auto-excluded {excluded_count} sibling model(s) under target brand(s).")

    def _auto_exclude_all_others(self):
        """Auto-exclude BOTH competitor parent brands AND sibling non-target models."""
        self._auto_exclude_other_brands()
        self._auto_exclude_other_models()
        self._log("Auto-excluded all other competitor brands and sibling models.")

    def _reset_brand_modes(self):
        """Reset all brand targeting states to neutral."""
        self.brand_states.clear()
        self._refresh_brand_tree()
        self.include_text.delete("1.0", "end")
        self._log("Brand target states reset to Neutral.")

    def _on_tree_select(self, event=None):
        self._update_include_preview()

    def _update_include_preview(self):
        """Update the include terms text box strictly based on targeted items."""
        target_keys = [k for k, v in self.brand_states.items() if v == "target"]
        exclude_names = {k.split("/")[-1] for k, v in self.brand_states.items() if v == "exclude"}

        if not target_keys:
            sel = self.brand_tree.selection()
            if sel:
                item_name = self.brand_tree.item(sel[0], "text")
                self.include_text.delete("1.0", "end")
                self.include_text.insert("1.0", item_name)
            else:
                self.include_text.delete("1.0", "end")
            return

        all_terms = []
        for key in target_keys:
            parts = key.split("/")
            name = parts[-1]
            if name not in all_terms and name not in exclude_names:
                all_terms.append(name)

        self.include_text.delete("1.0", "end")
        self.include_text.insert("1.0", "\n".join(all_terms))

    def _add_parent_brand(self):
        self._brand_dialog("Add Parent Brand", lambda name: (
            self.data_store.add_parent_brand(name),
            self._refresh_brand_tree()
        ))

    def _add_sub_brand(self):
        sel = self.brand_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Select a parent brand first.")
            return
        parent = sel.split("/")[0]
        self._brand_dialog("Add Sub-brand", lambda name: (
            self.data_store.add_sub_brand(parent, name),
            self._refresh_brand_tree()
        ))

    def _add_model(self):
        sel = self.brand_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Select a parent brand or sub-brand first.")
            return
        parts = sel.split("/")
        if len(parts) == 1:
            parent_name = parts[0]
            self._brand_dialog(f"Add Model to {parent_name}", lambda name: (
                self.data_store.add_model(parent_name, "", name),
                self._refresh_brand_tree()
            ))
        elif len(parts) >= 2:
            parent_name, sub_name = parts[0], parts[1]
            self._brand_dialog(f"Add Model to {sub_name}", lambda name: (
                self.data_store.add_model(parent_name, sub_name, name),
                self._refresh_brand_tree()
            ))

    def _remove_brand(self):
        sel = self.brand_tree.focus()
        if not sel:
            return
        name = self.brand_tree.item(sel)["text"]
        if messagebox.askyesno("Confirm", f"Remove '{name}' and all children?"):
            self.data_store.remove_brand_item(name)
            self._refresh_brand_tree()

    def _brand_dialog(self, title, callback):
        t = self.theme
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg=t["bg"])
        win.geometry("320x120")
        win.grab_set()
        self._apply_dark_titlebar(win)
        tk.Label(win, text="Name:", bg=t["bg"], fg=t["text"], font=FONT).pack(pady=(16, 4))
        entry = tk.Entry(win, bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                         relief="flat", font=FONT, width=28)
        entry.pack()
        entry.focus()
        def submit(ev=None):
            name = entry.get().strip()
            if name:
                callback(name)
                win.destroy()
        entry.bind("<Return>", submit)
        tk.Button(win, text="Add", command=submit,
                  bg=t["accent"], fg="black" if t.get("name", "").startswith("⚡") else "white", relief="flat", font=FONT).pack(pady=8)

    def _on_brand_drag_start(self, event):
        item = self.brand_tree.identify_row(event.y)
        if item:
            self._drag_data = {
                "item": item,
                "y": event.y,
                "dragging": False
            }
        else:
            self._drag_data = None

    def _on_brand_drag_motion(self, event):
        if not self._drag_data:
            return
        if abs(event.y - self._drag_data["y"]) > 4:
            self._drag_data["dragging"] = True
            hover_item = self.brand_tree.identify_row(event.y)
            if hover_item and hover_item != self._drag_data["item"]:
                parent_drag = self.brand_tree.parent(self._drag_data["item"])
                parent_hover = self.brand_tree.parent(hover_item)
                if parent_drag == parent_hover:
                    self.brand_tree.config(cursor="fleur")
                    return
            self.brand_tree.config(cursor="arrow")

    def _on_brand_drag_release(self, event):
        self.brand_tree.config(cursor="arrow")
        if not self._drag_data or not self._drag_data.get("dragging"):
            self._drag_data = None
            return

        drag_item = self._drag_data["item"]
        target_item = self.brand_tree.identify_row(event.y)
        self._drag_data = None

        if not target_item or target_item == drag_item:
            return

        parent_drag = self.brand_tree.parent(drag_item)
        parent_target = self.brand_tree.parent(target_item)

        # Only allow reordering among siblings under the same parent
        if parent_drag == parent_target:
            target_idx = self.brand_tree.index(target_item)
            self.brand_tree.move(drag_item, parent_drag, target_idx)
            self._save_tree_order(parent_drag)
            item_name = self.brand_tree.item(drag_item, "text")
            self._log(f"↕ Reordered brand item: '{item_name}'")

    def _move_selected_brand(self, direction: int):
        """Move selected brand item up (-1) or down (+1) within its siblings."""
        sel = self.brand_tree.focus()
        if not sel:
            return "break"
        parent = self.brand_tree.parent(sel)
        children = list(self.brand_tree.get_children(parent))
        if sel not in children:
            return "break"
        idx = children.index(sel)
        new_idx = idx + direction
        if 0 <= new_idx < len(children):
            self.brand_tree.move(sel, parent, new_idx)
            self._save_tree_order(parent)
            self.brand_tree.see(sel)
            self.brand_tree.focus(sel)
            self.brand_tree.selection_set(sel)
            item_name = self.brand_tree.item(sel, "text")
            self._log(f"↕ Moved '{item_name}' {'up' if direction < 0 else 'down'}.")
        return "break"

    def _save_tree_order(self, parent_id: str):
        """Persist current Treeview order to DataStore."""
        if not parent_id:
            parents = [self.brand_tree.item(c, "text") for c in self.brand_tree.get_children("")]
            self.data_store.reorder_parent_brands(parents)
        else:
            parts = parent_id.split("/")
            if len(parts) == 1:
                parent_name = parts[0]
                models = []
                subs = []
                for c in self.brand_tree.get_children(parent_id):
                    item_type = self.brand_tree.item(c, "values")[0]
                    item_text = self.brand_tree.item(c, "text")
                    if item_type == "Sub":
                        subs.append(item_text)
                    else:
                        models.append(item_text)
                if models:
                    self.data_store.reorder_models(parent_name, "", models)
                if subs:
                    self.data_store.reorder_subs(parent_name, subs)
            elif len(parts) == 2:
                parent_name, sub_name = parts[0], parts[1]
                models = [self.brand_tree.item(c, "text") for c in self.brand_tree.get_children(parent_id)]
                self.data_store.reorder_models(parent_name, sub_name, models)

    # ══════════════════════════════════════════════════════════════════════════
    #  EXCLUSION MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════════
    def _on_excl_mousewheel(self, e):
        """Scroll exclusions list on mousewheel from any inner widget."""
        self.excl_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _select_all_exclusions(self):
        for var in self.excl_vars.values():
            var.set(True)

    def _unselect_all_exclusions(self):
        for var in self.excl_vars.values():
            var.set(False)

    def _refresh_exclusion_list(self):
        t = self.theme
        for w in self.excl_inner.winfo_children():
            w.destroy()
        self.excl_vars = {}
        for term in self.data_store.get_exclusions():
            # Exclusions unselected by default as requested
            var = tk.BooleanVar(value=False)
            self.excl_vars[term] = var
            cb = tk.Checkbutton(self.excl_inner, text=term, variable=var,
                                bg=t["entry_bg"], fg=t["text"], selectcolor=t["panel"],
                                activebackground=t["entry_bg"], font=FONT_SM,
                                anchor="w")
            cb.bind("<MouseWheel>", self._on_excl_mousewheel)
            cb.pack(fill="x", anchor="w")

    def _add_exclusion(self):
        term = self.new_excl_entry.get().strip()
        placeholder = "New generic exclusion"
        if term and term != placeholder:
            if term.lower() in ("rick", "astley", "rickroll", "never gonna give you up", "never"):
                self._trigger_rickroll_easter_egg()
            self.data_store.add_exclusion(term)
            self.new_excl_entry.delete(0, "end")
            self._refresh_exclusion_list()

    def _remove_exclusion(self):
        checked = [t for t, v in self.excl_vars.items() if v.get()]
        if not checked:
            messagebox.showinfo("Remove", "Check terms to remove first.")
            return
        for t in checked:
            self.data_store.remove_exclusion(t)
        self._refresh_exclusion_list()

    def _get_active_exclusions(self):
        return [t for t, v in self.excl_vars.items() if v.get()]

    # ══════════════════════════════════════════════════════════════════════════
    #  PORTFOLIO PRESETS & 1-CLICK SWEEPER
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh_preset_list(self):
        """Populate the portfolio preset combobox."""
        if not hasattr(self, "preset_combo"):
            return
        presets = self.data_store.get_presets()
        keys = list(presets.keys())
        self.preset_combo["values"] = keys
        if keys and (not self.preset_var.get() or self.preset_var.get() not in keys):
            self.preset_var.set(keys[0])

    def _on_preset_selected(self, event=None):
        """When user selects a preset, auto-target its brands in the brand library."""
        preset_name = self.preset_var.get().strip()
        presets = self.data_store.get_presets()
        if preset_name not in presets:
            return

        target_brands = presets[preset_name]
        self.brand_states.clear()

        # Find and target matching parent brands, sub-brands, and models
        all_brands = self.data_store.get_brands()
        for parent_name, pdata in all_brands.items():
            if parent_name in target_brands:
                self._apply_mode(parent_name, "target")
            else:
                self._apply_mode(parent_name, "exclude")

            for sub_name in pdata.get("subs", {}).keys():
                sub_key = f"{parent_name}/{sub_name}"
                if sub_name in target_brands or sub_key in target_brands:
                    self._apply_mode(sub_key, "target")

            for model_name in pdata.get("models", []):
                mod_key = f"{parent_name}/{model_name}"
                if model_name in target_brands or mod_key in target_brands:
                    self._apply_mode(mod_key, "target")

        self._update_include_preview()
        self._log(f"📦 Loaded Preset '{preset_name}': Targeted {len(target_brands)} item(s) ({', '.join(target_brands)}).")
        self._status(f"Loaded Preset: {preset_name}")

    def _save_custom_preset(self):
        """Save currently targeted brands as a new custom portfolio preset with overwrite support."""
        target_keys = [k for k, v in self.brand_states.items() if v == "target"]
        if not target_keys:
            sel = self.brand_tree.selection()
            if sel:
                target_keys = list(sel)

        target_brands = []
        for k in target_keys:
            name = k.split("/")[-1]
            if name not in target_brands:
                target_brands.append(name)

        if not target_brands:
            messagebox.showinfo("No Brands Selected", "Mark one or more brands as 🎯 Target in the library first before saving a preset.")
            return

        t = self.theme
        win = tk.Toplevel(self)
        win.title("Save / Update Portfolio Preset")
        win.configure(bg=t["bg"])
        win.geometry("440x210")
        win.resizable(False, False)
        self._center_window(win, 440, 210)
        self._apply_dark_titlebar(win)

        tk.Label(win, text="💾 Save or Update Portfolio Preset", bg=t["bg"], fg=t["accent"],
                 font=("Segoe UI", 11, "bold")).pack(pady=(14, 4))

        tk.Label(win, text=f"Targeting {len(target_brands)} brand(s): {', '.join(target_brands[:4])}{'...' if len(target_brands) > 4 else ''}",
                 bg=t["bg"], fg=t["subtext"], font=FONT_SM).pack(pady=(0, 10))

        lbl_frame = tk.Frame(win, bg=t["bg"])
        lbl_frame.pack(fill="x", padx=24)
        tk.Label(lbl_frame, text="Preset Name (Select existing to Overwrite, or type new):",
                 bg=t["bg"], fg=t["text"], font=FONT_SM).pack(anchor="w")

        presets = self.data_store.get_presets()
        existing_names = list(presets.keys())
        name_var = tk.StringVar(value=self.preset_var.get() if self.preset_var.get() in existing_names else "")
        combo = ttk.Combobox(lbl_frame, textvariable=name_var, values=existing_names, font=FONT_SM)
        combo.pack(fill="x", pady=(4, 14))
        combo.focus()

        btn_row = tk.Frame(win, bg=t["bg"])
        btn_row.pack(fill="x", padx=24)

        def _do_save():
            chosen_name = name_var.get().strip()
            if not chosen_name:
                messagebox.showwarning("Name Required", "Please enter or select a preset name.", parent=win)
                return
            if chosen_name in presets:
                if not messagebox.askyesno("Overwrite Preset", f"Portfolio Preset '{chosen_name}' already exists.\n\nOverwrite and update with current {len(target_brands)} targeted brand(s)?", parent=win):
                    return

            self.data_store.save_preset(chosen_name, target_brands)
            self._refresh_preset_list()
            self.preset_var.set(chosen_name)
            self._log(f"💾 Saved Portfolio Preset '{chosen_name}' with {len(target_brands)} brand(s): {', '.join(target_brands)}")
            win.destroy()
            messagebox.showinfo("Preset Saved", f"Successfully saved Portfolio Preset '{chosen_name}' with {len(target_brands)} brand(s)!", parent=self)

        self._btn(btn_row, "💾 Save / Update Preset", _do_save, accent=True).pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._btn(btn_row, "Cancel", win.destroy).pack(side="right")
        win.bind("<Return>", lambda e: _do_save())

    def _delete_custom_preset(self):
        """Delete currently selected custom preset."""
        name = self.preset_var.get().strip()
        if not name:
            return
        if messagebox.askyesno("Delete Preset", f"Delete Portfolio Preset '{name}'?"):
            self.data_store.delete_preset(name)
            self._refresh_preset_list()

    def _queue_clean_targeted_brands(self):
        """Queue only the explicitly targeted brand/sub-brand names as clean, individual 1-term searches."""
        # 1. Parse stores (safely handling Global AliExpress mode and placeholders)
        stores = self._get_stores_from_input()
        if not stores:
            messagebox.showwarning("Missing Stores", "Enter one or more store URLs or seller names in the Stores box.")
            return

        # 2. Get explicitly targeted terms or custom ad-hoc terms
        target_keys = [k for k, v in self.brand_states.items() if v == "target"]
        if not target_keys:
            sel = self.brand_tree.selection()
            if sel:
                target_keys = list(sel)

        custom_includes = [l.strip() for l in self.include_text.get("1.0", "end").splitlines() if l.strip()]

        if not target_keys and not custom_includes:
            messagebox.showwarning("No Target Terms", "Mark at least one brand as 🎯 Target or type custom keywords in the Target box.")
            return

        target_terms = []
        for k in target_keys:
            name = k.split("/")[-1]
            if name not in target_terms:
                target_terms.append(name)

        if not target_terms and custom_includes:
            target_terms = list(custom_includes)

        generic_excludes = self._get_active_exclusions()
        condition = self.condition_var.get()
        all_library_brands = self.data_store.get_brands() if hasattr(self, "data_store") else {}
        market = self.marketplace_var.get()
        if "Wish" in market:
            platform_name = "Wish"
        elif "Temu" in market:
            platform_name = "Temu"
        elif "AliExpress" in market:
            platform_name = "AliExpress"
        elif "Printerval" in market:
            platform_name = "Printerval"
        elif "Redbubble" in market:
            platform_name = "Redbubble"
        elif "Mercado" in market:
            platform_name = "Mercado Libre"
        else:
            platform_name = "eBay"

        queued_count = 0
        skipped_executed = 0
        for store in stores:
            for term in target_terms:
                if any(q.get("store", "").strip().lower() == store.strip().lower() and 
                       q.get("brand", "").strip().lower() == term.strip().lower() and 
                       q.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for q in self.queue):
                    continue
                if any(ex.get("store", "").strip().lower() == store.strip().lower() and 
                       ex.get("brand", "").strip().lower() == term.strip().lower() and 
                       ex.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for ex in self.executed_jobs):
                    skipped_executed += 1
                    continue

                # Exclude competitor library brands outside this targeted term/parent
                job_excludes = list(generic_excludes)
                parent_of_term = ""
                for p_b, p_d in all_library_brands.items():
                    if term.lower() == p_b.lower() or term.lower() in [m.lower() for m in p_d.get("models", [])] or term.lower() in [s.lower() for s in p_d.get("subs", {}).keys()]:
                        parent_of_term = p_b
                        break
                for other_b in all_library_brands.keys():
                    if parent_of_term:
                        if other_b.lower() != parent_of_term.lower() and other_b not in job_excludes:
                            job_excludes.append(other_b)
                    else:
                        if other_b.lower() != term.lower() and other_b not in job_excludes:
                            job_excludes.append(other_b)

                entry = {
                    "store": store,
                    "brand": term,
                    "marketplace": platform_name,
                    "includes": [term],  # Clean, standalone single keyword!
                    "excludes": job_excludes,
                    "condition": condition
                }
                self.queue.append(entry)
                label = f"{self._store_label(store, platform=platform_name)} ▸ {term} [Clean 1-Term Sweep]"
                self.queue_list.insert("end", label)
                queued_count += 1

        if skipped_executed > 0:
            self._log(f"ℹ️ Skipped {skipped_executed} already-completed search(es) on {platform_name} in this session.")
        store_names = [self._store_label(s, platform=platform_name) for s in stores]
        self._log(f"🎯 Queued {queued_count} Clean Individual Search(es) for [{', '.join(target_terms)}] across {len(stores)} target(s): {', '.join(store_names)} [{platform_name}]")
        self._status(f"🎯 Queued {queued_count} Clean Term Search(es) [{platform_name}]!")

    def _queue_portfolio_preset(self):
        """1-Click Portfolio Sweep: Automatically queue all preset brands across all entered stores."""
        preset_name = self.preset_var.get().strip()
        presets = self.data_store.get_presets()
        if preset_name not in presets:
            messagebox.showinfo("Select Preset", "Select a valid Portfolio Preset first.")
            return

        stores = self._get_stores_from_input()
        if not stores:
            messagebox.showwarning("Missing Stores", "Enter one or more store URLs or seller names in the Stores box.")
            return

        preset_brands = presets[preset_name]
        if not preset_brands:
            messagebox.showinfo("Empty Preset", f"Preset '{preset_name}' has no brands configured.")
            return

        generic_excludes = self._get_active_exclusions()
        condition = self.condition_var.get()
        all_library_brands = self.data_store.get_brands()

        market = self.marketplace_var.get() if hasattr(self, "marketplace_var") else "eBay"
        if "Wish" in market:
            platform_name = "Wish"
        elif "Temu" in market:
            platform_name = "Temu"
        elif "AliExpress" in market:
            platform_name = "AliExpress"
        elif "Printerval" in market:
            platform_name = "Printerval"
        elif "Redbubble" in market:
            platform_name = "Redbubble"
        elif "Mercado" in market:
            platform_name = "Mercado Libre"
        else:
            platform_name = "eBay"

        queued_count = 0
        skipped_executed = 0
        for store in stores:
            for parent_brand in preset_brands:
                if parent_brand not in all_library_brands:
                    continue
                if any(q.get("store", "").strip().lower() == store.strip().lower() and 
                       q.get("brand", "").strip().lower() == parent_brand.strip().lower() and 
                       q.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for q in self.queue):
                    continue
                if any(ex.get("store", "").strip().lower() == store.strip().lower() and 
                       ex.get("brand", "").strip().lower() == parent_brand.strip().lower() and 
                       ex.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for ex in self.executed_jobs):
                    skipped_executed += 1
                    continue
                pdata = all_library_brands[parent_brand]

                # Gather all include terms for this parent
                includes = [parent_brand]
                includes.extend(pdata.get("models", []))
                for sub, sub_models in pdata.get("subs", {}).items():
                    if sub not in includes:
                        includes.append(sub)
                    for sm in sub_models:
                        if sm not in includes:
                            includes.append(sm)

                # Exclude competitor brands outside this parent
                job_excludes = list(generic_excludes)
                for other_b in all_library_brands.keys():
                    if other_b != parent_brand and other_b not in job_excludes:
                        job_excludes.append(other_b)

                entry = {
                    "store": store,
                    "brand": parent_brand,
                    "marketplace": platform_name,
                    "includes": includes,
                    "excludes": job_excludes,
                    "condition": condition
                }
                self.queue.append(entry)
                label = f"{self._store_label(store, platform=platform_name)} ▸ {parent_brand} ({len(includes)} terms | {len(job_excludes)} excl)"
                self.queue_list.insert("end", label)
                queued_count += 1

        if skipped_executed > 0:
            self._log(f"ℹ️ Skipped {skipped_executed} already-completed search(es) on {platform_name} in this session.")
        store_names = [self._store_label(s, platform=platform_name) for s in stores]
        self._log(f"📦 [PORTFOLIO SWEEP] Queued {queued_count} batch job(s) for Preset '{preset_name}' across {len(stores)} target(s): {', '.join(store_names)} [{platform_name}]")
        self._status(f"📦 1-Click Sweep: Queued {queued_count} job(s) for {len(stores)} target(s) [{platform_name}]!")
        messagebox.showinfo("Portfolio Sweep Queued", f"Successfully queued {queued_count} search job(s) for '{preset_name}' across {len(stores)} target(s) on {platform_name}!\n\nClick '▶ Run' to start harvesting!")

    # ══════════════════════════════════════════════════════════════════════════
    #  QUEUE & BATCH EXECUTION (MULTI-STORE + MULTI-BRAND)
    # ══════════════════════════════════════════════════════════════════════════
    def _add_to_queue(self):
        # 1. Parse all stores/sellers entered
        stores = self._get_stores_from_input()
        if not stores:
            messagebox.showwarning("Missing Stores", "Enter one or more store URLs or seller names in the Stores box.")
            return

        for s in stores:
            if any(r in s.lower() for r in ("rick", "astley", "rickroll", "never gonna give you up")):
                self._trigger_rickroll_easter_egg()
                break

        # 2. Identify Target Brands & Custom Include Terms
        target_items = [k for k, v in self.brand_states.items() if v == "target"]
        custom_includes = [l.strip() for l in self.include_text.get("1.0", "end").splitlines() if l.strip()]

        if not target_items and not custom_includes:
            sel = self.brand_tree.selection()
            if sel:
                target_items = [sel[0]]
            else:
                messagebox.showwarning("Missing Targets", "Mark at least one brand as 🎯 Target or type custom keywords in the Target box.")
                return

        # 3. Identify Excluded Brands from Brand Library
        brand_excludes = []
        for k, v in self.brand_states.items():
            if v == "exclude":
                name = k.split("/")[-1]
                if name not in brand_excludes:
                    brand_excludes.append(name)

        # 4. Collect generic exclusions
        generic_excludes = self._get_active_exclusions()
        condition = self.condition_var.get()

        # Deduplicate top target parents
        top_targets = []
        for k in target_items:
            parts = k.split("/")
            top_parent = parts[0]
            if top_parent not in top_targets:
                top_targets.append(top_parent)

        if not top_targets and custom_includes:
            top_targets = [custom_includes[0].title() if len(custom_includes) == 1 else "Custom Search"]

        market = self.marketplace_var.get() if hasattr(self, "marketplace_var") else "eBay"
        if "Wish" in market:
            platform_name = "Wish"
        elif "Temu" in market:
            platform_name = "Temu"
        elif "AliExpress" in market:
            platform_name = "AliExpress"
        elif "Printerval" in market:
            platform_name = "Printerval"
        elif "Redbubble" in market:
            platform_name = "Redbubble"
        elif "Mercado" in market:
            platform_name = "Mercado Libre"
        else:
            platform_name = "eBay"

        queued_count = 0
        skipped_executed = 0
        for store in stores:
            for parent_brand in top_targets:
                if any(q.get("store", "").strip().lower() == store.strip().lower() and 
                       q.get("brand", "").strip().lower() == parent_brand.strip().lower() and 
                       q.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for q in self.queue):
                    continue
                if any(ex.get("store", "").strip().lower() == store.strip().lower() and 
                       ex.get("brand", "").strip().lower() == parent_brand.strip().lower() and 
                       ex.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for ex in self.executed_jobs):
                    skipped_executed += 1
                    continue

                # Gather explicit target terms for this parent
                brand_target_terms = []
                for k in target_items:
                    if k.split("/")[0] == parent_brand:
                        term_name = k.split("/")[-1]
                        if term_name not in brand_target_terms and term_name not in brand_excludes:
                            brand_target_terms.append(term_name)

                includes = brand_target_terms if brand_target_terms else custom_includes
                if not includes:
                    includes = [parent_brand]

                # Build exclusion list: other targeted brands in batch + library excludes + generic excludes
                job_excludes = list(generic_excludes) + list(brand_excludes)
                for other_b in top_targets:
                    if other_b != parent_brand and other_b not in job_excludes:
                        job_excludes.append(other_b)

                entry = {
                    "store": store,
                    "brand": parent_brand,
                    "marketplace": platform_name,
                    "includes": includes,
                    "excludes": job_excludes,
                    "condition": condition
                }
                self.queue.append(entry)
                label = f"{self._store_label(store, platform=platform_name)} ▸ {parent_brand} ({len(includes)} terms | {len(job_excludes)} excl)"
                self.queue_list.insert("end", label)
                queued_count += 1

        if skipped_executed > 0:
            self._log(f"ℹ️ Skipped {skipped_executed} already-completed search(es) on {platform_name} in this session.")
        store_names = [self._store_label(s, platform=platform_name) for s in stores]
        self._log(f"🎯 Queued {queued_count} job(s) for [{', '.join(top_targets)}] across {len(stores)} target(s): {', '.join(store_names)} [{platform_name}]")

    def _store_label(self, url, platform=None):
        if not platform:
            mkt = self.marketplace_var.get() if hasattr(self, "marketplace_var") else "eBay"
            if "Wish" in mkt:
                plat = "Wish"
            elif "Temu" in mkt:
                plat = "Temu"
            elif "AliExpress" in mkt:
                plat = "AliExpress"
            elif "Printerval" in mkt:
                plat = "Printerval"
            elif "Redbubble" in mkt:
                plat = "Redbubble"
            elif "Mercado" in mkt:
                plat = "Mercado Libre"
            else:
                plat = "eBay"
        else:
            plat = platform

        if not url:
            return f"[{plat}] Full Search"
        low = url.lower().strip()
        if any(g == low or g in low for g in ("global", "global search", "marketplace", "all", "catalog", "wholesale", "search", "all products")):
            return f"[{plat}] Full Search"
        parts = url.rstrip("/").split("/")
        s_name = parts[-1] if parts else url
        return f"[{plat}] {s_name}"

    def _check_strict_exclusions(self, title: str, excludes: list) -> tuple:
        """Verify listing title does not contain any excluded keyword with word-boundary accuracy."""
        if not title or not excludes:
            return True, ""
        t_lower = title.lower()
        for ex in excludes:
            ex_clean = str(ex).strip().strip('"').lower()
            if not ex_clean or len(ex_clean) < 2:
                continue
            pattern = r'(?:\b|_)' + re.escape(ex_clean) + r'(?:\b|_)'
            if re.search(pattern, t_lower):
                return False, ex_clean
        return True, ""

    def _deduplicate_queue(self):
        """Remove duplicate or already-executed jobs from the pending queue with marketplace isolation."""
        if not self.queue:
            messagebox.showinfo("Queue Empty", "Search queue is currently empty.")
            return

        initial_len = len(self.queue)
        seen_keys = set()
        clean_queue = []

        # Collect executed keys from this session with marketplace isolation
        executed_keys = {
            (
                ex.get("marketplace", "eBay").strip().lower(),
                ex.get("store", "").strip().lower(),
                ex.get("brand", "").strip().lower()
            ) for ex in self.executed_jobs
        }

        purged_already_run = 0
        purged_duplicates = 0

        for job in self.queue:
            plat = job.get("marketplace", "eBay")
            k = (
                plat.strip().lower(),
                job.get("store", "").strip().lower(),
                job.get("brand", "").strip().lower()
            )
            if k in executed_keys:
                purged_already_run += 1
                continue
            if k in seen_keys:
                purged_duplicates += 1
                continue
            seen_keys.add(k)
            clean_queue.append(job)

        self.queue = clean_queue
        self.queue_list.delete(0, "end")
        for job in self.queue:
            plat = job.get("marketplace", "eBay")
            s_lbl = self._store_label(job.get("store", ""), platform=plat)
            b_name = job.get("brand", "")
            inc_len = len(job.get("includes", []))
            exc_len = len(job.get("excludes", []))
            lbl = f"{s_lbl} ▸ {b_name} ({inc_len} terms | {exc_len} excl)"
            self.queue_list.insert("end", lbl)

        total_purged = initial_len - len(self.queue)
        self._log(f"🧹 Queue Deduplicated: Purged {total_purged} job(s) ({purged_already_run} already executed on same platform, {purged_duplicates} duplicate). {len(self.queue)} job(s) remain.")
        messagebox.showinfo("Queue Cleaned", f"Queue Deduplication Complete!\n\n• Already Executed Jobs Purged: {purged_already_run}\n• Duplicate Jobs Purged: {purged_duplicates}\n• Remaining Active Jobs: {len(self.queue)}")

    def _pop_queue_ui_item(self):
        """Remove the top completed job from the UI queue listbox."""
        if hasattr(self, "queue_list") and self.queue_list.size() > 0:
            self.queue_list.delete(0)

    def _remove_selected_from_queue(self):
        """Remove currently selected items from queue list."""
        if self.running:
            messagebox.showwarning("Busy", "Cannot modify queue while a scan is running.")
            return
        selected = list(self.queue_list.curselection())
        if not selected:
            messagebox.showinfo("Select", "Select a queued job to remove.")
            return
        for idx in reversed(selected):
            if idx < len(self.queue):
                del self.queue[idx]
            self.queue_list.delete(idx)
        self._log("Removed selected job(s) from queue.")

    def _clear_queue(self):
        if self.running:
            messagebox.showwarning("Busy", "Stop the current scan before clearing the queue.")
            return
        self.queue.clear()
        self.queue_list.delete(0, "end")
        self._log("Queue cleared.")

    def _run_queue(self):
        if not self.queue:
            messagebox.showinfo("Queue", "Queue is empty. Add stores & brands to Queue first.")
            return
        if self.running:
            if self.paused:
                self._toggle_pause()
            return

        self.running = True
        self.paused = False
        self.stop_event.clear()
        self.pause_event.set()

        t = self.theme
        self.run_btn.config(state="disabled")
        self.pause_btn.config(state="normal", text="⏸  Pause", bg=t["btn_normal_bg"])
        self.stop_btn.config(state="normal")
        if hasattr(self, "dedup_q_btn"):
            self.dedup_q_btn.config(state="disabled")
        self.del_q_btn.config(state="disabled")
        self.clear_q_btn.config(state="disabled")

        self.progress.start()
        thread = threading.Thread(target=self._process_queue, daemon=True)
        thread.start()

    def _toggle_pause(self):
        t = self.theme
        if not self.running:
            return
        if self.paused:
            self.paused = False
            self.pause_event.set()
            self.pause_btn.config(text="⏸  Pause", bg=t["btn_normal_bg"])
            self._status("Resumed search...")
            self._log("▶ Search resumed.")
            self.progress.start()
        else:
            self.paused = True
            self.pause_event.clear()
            self.pause_btn.config(text="▶  Resume", bg=t["accent"])
            self._status("Paused. Click 'Resume' to continue.")
            self._log("⏸ Search paused by user.")
            self.progress.stop()

    def _stop_scan(self):
        if not self.running:
            return
        self._log("⏹ Stopping scan (finishing current item)...")
        self._status("Stopping scan...")
        self.stop_event.set()
        self.pause_event.set()
        self.stop_btn.config(state="disabled")

    def _process_queue(self):
        use_api = self.use_api.get()
        app_id  = self.api_app_id_var.get().strip()
        cert_id = self.api_cert_id_var.get().strip()

        # Ensure scrapers honor current headless background mode
        is_headless = self.headless_var.get()
        self.scraper.headless = is_headless
        self.aliexpress_scraper.headless = is_headless
        self.wish_scraper.headless = is_headless
        self.temu_scraper.headless = is_headless
        self.mercadolibre_scraper.headless = is_headless
        self.redbubble_scraper.headless = is_headless
        self.printerval_scraper.headless = is_headless

        if use_api and app_id:
            client = EbayAPIClient(app_id=app_id, cert_id=cert_id)
        else:
            client = None

        total_new_items = 0
        total_initial_jobs = len(self.queue)
        job_idx = 0
        while self.queue and not self.stop_event.is_set():
            job = self.queue[0]
            job_idx += 1

            store_raw = job["store"]
            job_mkt = job.get("marketplace")
            if job_mkt:
                platform_name = job_mkt
                is_wish = platform_name == "Wish"
                is_temu = platform_name == "Temu"
                is_aliexpress = platform_name == "AliExpress"
                is_meli = platform_name == "Mercado Libre"
                is_redbubble = platform_name == "Redbubble"
                is_printerval = platform_name == "Printerval"
                mkt_map = {
                    "Wish": "wish.com", "Temu": "temu.com", "AliExpress": "aliexpress.com",
                    "Mercado Libre": "mercadolibre.com", "Redbubble": "redbubble.com",
                    "Printerval": "printerval.com", "eBay": "ebay.com"
                }
                mkt_tag = mkt_map.get(platform_name, "ebay.com")
            else:
                is_wish = "wish.com" in store_raw.lower() or "Wish" in self.marketplace_var.get()
                is_temu = "temu.com" in store_raw.lower() or "Temu" in self.marketplace_var.get()
                is_aliexpress = "aliexpress.com" in store_raw.lower() or "AliExpress" in self.marketplace_var.get()
                is_meli = "mercadolibre" in store_raw.lower() or "mercadolivre" in store_raw.lower() or "Mercado Libre" in self.marketplace_var.get()
                is_redbubble = "redbubble.com" in store_raw.lower() or "Redbubble" in self.marketplace_var.get()
                is_printerval = "printerval.com" in store_raw.lower() or "Printerval" in self.marketplace_var.get()

                if is_wish:
                    platform_name = "Wish"
                    mkt_tag = "wish.com"
                elif is_temu:
                    platform_name = "Temu"
                    mkt_tag = "temu.com"
                elif is_aliexpress:
                    platform_name = "AliExpress"
                    mkt_tag = "aliexpress.com"
                elif is_meli:
                    platform_name = "Mercado Libre"
                    mkt_tag = "mercadolibre.com"
                elif is_redbubble:
                    platform_name = "Redbubble"
                    mkt_tag = "redbubble.com"
                elif is_printerval:
                    platform_name = "Printerval"
                    mkt_tag = "printerval.com"
                else:
                    platform_name = "eBay"
                    mkt_tag = "ebay.com"

            seller_label = self._store_label(store_raw, platform=platform_name)
            total_active_jobs = (job_idx - 1) + len(self.queue)
            remaining_in_queue = len(self.queue) - 1
            self._status(f"Processing Job {job_idx}/{total_active_jobs} ({remaining_in_queue} queued) [{platform_name}]: {job['brand']} in {seller_label}")
            self._log(f"[Job {job_idx}/{total_active_jobs}] 🛒 [{platform_name}] Target: '{job['brand']}' in {seller_label} (Condition: {job.get('condition', 'all')})")
            job_record = {
                "brand": job["brand"],
                "store": store_raw,
                "marketplace": platform_name,
                "condition": job.get("condition", "all"),
                "includes": list(job["includes"]),
                "excludes": list(job["excludes"]),
                "term_counts": {},
                "total_harvested": 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            try:
                if is_wish:
                    resolved = self.wish_scraper.resolve_store_info(store_raw).get("store_name", seller_label)
                    job_record["resolved_seller"] = resolved
                    self._log(f"🌠 [Wish] Target store resolved: '{resolved}'")
                elif is_temu:
                    resolved = self.temu_scraper.resolve_store_info(store_raw).get("store_name", seller_label)
                    job_record["resolved_seller"] = resolved
                    self._log(f"🟠 [Temu] Target store resolved: '{resolved}'")
                elif is_aliexpress:
                    resolved = self.aliexpress_scraper.resolve_store_info(store_raw).get("store_name", seller_label)
                    job_record["resolved_seller"] = resolved
                    self._log(f"🌐 [AliExpress] Target store resolved: '{resolved}'")
                elif is_meli:
                    resolved = "Mercado Libre (Latin America)"
                    job_record["resolved_seller"] = resolved
                    self._log(f"🇲🇽 [Mercado Libre] Target store resolved: '{resolved}'")
                elif is_redbubble:
                    resolved = self.redbubble_scraper.resolve_store_info(store_raw).get("store_name", seller_label)
                    job_record["resolved_seller"] = resolved
                    self._log(f"🎨 [Redbubble] Target store resolved: '{resolved}'")
                elif is_printerval:
                    resolved = self.printerval_scraper.resolve_store_info(store_raw).get("store_name", seller_label)
                    job_record["resolved_seller"] = resolved
                    self._log(f"👕 [Printerval] Target store resolved: '{resolved}'")
                else:
                    resolved = self.scraper.resolve_seller(store_raw)
                    job_record["resolved_seller"] = resolved
                    self._log(f"🛒 [eBay] Target store resolved: '{resolved}'")
                
                for include_term in job["includes"]:
                    if self.stop_event.is_set():
                        break
                    self.pause_event.wait()

                    self._status(f"Harvesting [{platform_name}]: {job['brand']} → '{include_term}' in {seller_label}...")
                    self._log(f"Searching [{platform_name}]: '{include_term}' in {seller_label} (Condition: {job.get('condition','all')})")
                    
                    if is_wish:
                        target_url = self.wish_scraper._build_search_url(
                            self.wish_scraper.resolve_store_info(store_raw),
                            include_term
                        )
                        self._log(f"  🔗 URL: {target_url}")
                        job_record["url"] = target_url
                        items = self.wish_scraper.search(
                            store_raw,
                            include_term,
                            job["excludes"],
                            condition=job.get("condition", "all"),
                            stop_event=self.stop_event,
                            pause_event=self.pause_event
                        )
                    elif is_temu:
                        target_url = self.temu_scraper._build_search_url(
                            self.temu_scraper.resolve_store_info(store_raw),
                            include_term
                        )
                        self._log(f"  🔗 URL: {target_url}")
                        job_record["url"] = target_url
                        items = self.temu_scraper.search(
                            store_raw,
                            include_term,
                            job["excludes"],
                            condition=job.get("condition", "all"),
                            stop_event=self.stop_event,
                            pause_event=self.pause_event
                        )
                    elif is_aliexpress:
                        target_url = self.aliexpress_scraper._build_search_url(
                            self.aliexpress_scraper.resolve_store_info(store_raw),
                            include_term
                        )
                        self._log(f"  🔗 URL: {target_url}")
                        job_record["url"] = target_url
                        items = self.aliexpress_scraper.search(
                            store_raw,
                            include_term,
                            job["excludes"],
                            condition=job.get("condition", "all"),
                            stop_event=self.stop_event,
                            pause_event=self.pause_event
                        )
                    elif is_meli:
                        self.mercadolibre_scraper.headless = is_headless
                        items = self.mercadolibre_scraper.search(
                            include_term,
                            max_items=50,
                            condition=job.get("condition", "all"),
                            log_callback=self._log
                        )
                        job_record["url"] = f"https://listado.mercadolibre.com.mx/{include_term.replace(' ', '-')}"
                    elif is_redbubble:
                        self.redbubble_scraper.headless = is_headless
                        items = self.redbubble_scraper.search(
                            include_term,
                            max_items=50,
                            condition=job.get("condition", "all"),
                            log_callback=self._log
                        )
                        job_record["url"] = f"https://www.redbubble.com/shop/?query={include_term.replace(' ', '+')}"
                    elif is_printerval:
                        self.printerval_scraper.headless = is_headless
                        items = self.printerval_scraper.search(
                            include_term,
                            max_items=50,
                            condition=job.get("condition", "all"),
                            log_callback=self._log
                        )
                        job_record["url"] = f"https://printerval.com/search?q={include_term.replace(' ', '+')}"
                    elif client:
                        items = client.search(
                            store_raw,
                            include_term,
                            job["excludes"],
                            condition=job.get("condition", "all")
                        )
                    else:
                        target_url = self.scraper._build_url(
                            self.scraper.resolve_store_info(store_raw),
                            include_term,
                            job["excludes"],
                            1,
                            job.get("condition", "all")
                        )
                        self._log(f"  🔗 URL: {target_url}")
                        job_record["url"] = target_url
                        items = self.scraper.search(
                            store_raw,
                            include_term,
                            job["excludes"],
                            condition=job.get("condition", "all"),
                            stop_event=self.stop_event,
                            pause_event=self.pause_event
                        )

                    new_items = []
                    filtered_out_count = 0
                    for item in items:
                        title = item.get("title", "")
                        # 1. Strict Exclusion Filter
                        passed_excl, matched_ex = self._check_strict_exclusions(title, job.get("excludes", []))
                        if not passed_excl:
                            filtered_out_count += 1
                            continue

                        item["brand"] = job["brand"]
                        item["keyword"] = include_term
                        if "marketplace" not in item or not item["marketplace"]:
                            item["marketplace"] = mkt_tag

                        item_id = item.get("item_id")
                        dedup_key = item_id if item_id else item.get("url")
                        if dedup_key and dedup_key not in self.seen_item_ids:
                            self.seen_item_ids.add(dedup_key)
                            self.results.append(item)
                            new_items.append(item)
                            total_new_items += 1
                        elif not dedup_key:
                            self.results.append(item)
                            new_items.append(item)
                            total_new_items += 1

                    job_record["term_counts"][include_term] = len(items)
                    job_record["total_harvested"] += len(new_items)

                    if filtered_out_count > 0:
                        self._log(f"  🛡️ Shielded: Dropped {filtered_out_count} listing(s) containing excluded competitor keywords.")

                    if new_items:
                        self._update_results_table(new_items)
                    self._log(f"  → Found {len(items)} listings ({len(new_items)} new) for '{include_term}' in {seller_label} [{platform_name}]")

            except Exception as e:
                self._log(f"ERROR on {job['brand']} in {seller_label} [{platform_name}]: {e}", error=True)
                job_record["error"] = str(e)

            self.executed_jobs.append(job_record)
            if self.queue:
                self.queue.pop(0)
            self.after(0, self._pop_queue_ui_item)

        stopped_early = self.stop_event.is_set()
        self.after(0, self._run_complete, total_new_items, stopped_early)

    def _run_complete(self, total, stopped_early=False):
        t = self.theme
        self.running = False
        self.paused = False
        self.progress.stop()

        self.run_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="⏸  Pause", bg=t["btn_normal_bg"])
        self.stop_btn.config(state="disabled")
        if hasattr(self, "dedup_q_btn"):
            self.dedup_q_btn.config(state="normal")
        self.del_q_btn.config(state="normal")
        self.clear_q_btn.config(state="normal")

        # Play sound effect if enabled
        if self.sound_enabled_var.get():
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

        if stopped_early:
            msg = f"Scan stopped by user. {total} new listings harvested ({len(self.results)} total in session)."
            self._status(msg)
            self._log(f"⏹ {msg}")
            messagebox.showinfo("Stopped", f"Scan stopped.\nHarvested {total} new listings ({len(self.results)} total).")
        else:
            msg = f"Done. {total} new listings harvested ({len(self.results)} total in session)."
            self._status(msg)
            self._log(f"✓ Run complete — {total} listings harvested.")
            messagebox.showinfo("Complete", f"Harvested {total} listings.\nClick 'Export to Excel' or 'Export Job Log' to save.")

        self.result_count.set(f"{len(self.results)} listings")
        self._check_enforcement_milestones()

    # ══════════════════════════════════════════════════════════════════════════
    #  RESULTS TABLE, LIVE FILTERING, BULK TAGGING & HOVER PREVIEWS
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh_bulk_brand_list(self):
        """Populate the bulk brand reassignment combobox from data_store."""
        if not hasattr(self, "bulk_brand_combo"):
            return
        brands = ["(No change)"]
        raw = self.data_store.get_brands()
        for parent, pdata in raw.items():
            if parent not in brands:
                brands.append(parent)
            for sub in pdata.get("subs", {}):
                if sub not in brands:
                    brands.append(sub)
        self.bulk_brand_combo["values"] = brands
        self.bulk_brand_combo.set("(No change)")

    def _clear_filter(self):
        """Clear live search filter and show all results."""
        self.filter_var.set("")

    def _select_all_visible(self):
        """Select all currently visible (and filtered) rows in results table."""
        children = self.result_tree.get_children()
        if children:
            self.result_tree.selection_set(children)

    def _deduplicate_results(self):
        """Deduplicate harvested listings by item ID and URL across active session."""
        if not self.results:
            messagebox.showinfo("Deduplicate", "No harvested listings in results table to deduplicate.")
            return

        initial_len = len(self.results)
        seen_ids = set()
        seen_urls = set()
        unique_items = []

        for it in self.results:
            iid = str(it.get("item_id", "")).strip()
            url = str(it.get("url", "")).strip().lower()
            norm_url = url.split("?")[0] if url else ""

            if (iid and iid in seen_ids) or (norm_url and norm_url in seen_urls):
                continue

            if iid: seen_ids.add(iid)
            if norm_url: seen_urls.add(norm_url)
            unique_items.append(it)

        purged = initial_len - len(unique_items)
        if purged > 0:
            self.results = unique_items
            self.seen_item_ids = {str(it.get("item_id", "")).strip() for it in self.results if it.get("item_id")}
            self._repopulate_results_table()
            self._log(f"🧹 Deduplication complete: Removed {purged} duplicate listing(s). {len(self.results)} pristine unique listings remain.")
            self._status(f"Deduplicated: Purged {purged} duplicate(s) ({len(self.results)} unique remain)")
            messagebox.showinfo("Deduplication Complete", f"Successfully purged {purged} duplicate listing(s)!\n\n{len(self.results)} unique listings remain in session.")
        else:
            messagebox.showinfo("Deduplication", "All listings in results table are already 100% unique (0 duplicates found).")

    def _on_filter_changed(self, *args):
        """Triggered on keystroke in live search filter entry."""
        self._repopulate_results_table()

    def _apply_bulk_tag(self):
        """Apply selected Brand and/or Product Type to all highlighted rows."""
        selected_iids = self.result_tree.selection()
        if not selected_iids:
            messagebox.showinfo("Select Rows", "Select one or more rows in the results table first.\n(Tip: You can use 'Select All Visible' or Ctrl+Click).")
            return

        new_brand = self.bulk_brand_var.get().strip()
        new_pt = self.bulk_product_var.get().strip()
        if new_pt == "(Select or type...)":
            new_pt = ""

        if (not new_brand or new_brand == "(No change)") and not new_pt:
            messagebox.showinfo("Nothing to Apply", "Choose a Brand to reassign or enter/select a Product Type.")
            return

        updated_count = 0
        for iid in selected_iids:
            vals = list(self.result_tree.item(iid, "values"))
            # values mapping: (brand[0], product_type[1], title[2], item_id[3], price[4], seller[5], location[6], image_url[7], url[8])
            row_item_id = str(vals[3]).strip() if len(vals) > 3 else ""
            row_url = str(vals[8]).strip() if len(vals) > 8 else ""

            # Update master record in self.results
            for item in self.results:
                if (row_item_id and str(item.get("item_id", "")).strip() == row_item_id) or \
                   (row_url and str(item.get("url", "")).strip() == row_url):
                    if new_brand and new_brand != "(No change)":
                        item["brand"] = new_brand
                    if new_pt:
                        item["product_type"] = new_pt
                    updated_count += 1
                    break

        self._repopulate_results_table()
        tag_desc = []
        if new_brand and new_brand != "(No change)":
            tag_desc.append(f"Brand: '{new_brand}'")
        if new_pt:
            tag_desc.append(f"Product Type: '{new_pt}'")
        summary_str = " | ".join(tag_desc)
        self._log(f"🏷️ Bulk Tag Applied to {updated_count} listing(s) → {summary_str}")
        self._status(f"Tagged {updated_count} listing(s) ({summary_str})")

    def _item_matches_filter(self, item: dict, query_str: str, target_col: str = None) -> bool:
        """
        Intelligent multi-column search evaluator supporting:
        1. Column-specific target routing (Title, Seller, Item ID, Brand, Product Type, Price, Location, All Columns)
        2. Positive token matching (e.g. 'emblem', 'trd')
        3. Negative exclusion modifiers (e.g. '-toyota', '-keychain', '-audi')
        4. Quoted exact phrase matching (e.g. '"valve stem" -plastic')
        """
        if not query_str or not query_str.strip():
            return True

        if not target_col:
            target_col = self.filter_col_var.get() if hasattr(self, "filter_col_var") else "Title"

        col_key = target_col.lower().strip()
        if "title" in col_key:
            target_text = str(item.get("title", ""))
        elif "seller" in col_key:
            target_text = str(item.get("seller", ""))
        elif "origin" in col_key:
            target_text = str(item.get("seller_origin", item.get("country", "")))
        elif "threat" in col_key:
            target_text = str(item.get("threat_badge", item.get("threat_intel", "")))
        elif "item" in col_key or "id" in col_key:
            target_text = str(item.get("item_id", ""))
        elif "brand" in col_key:
            target_text = str(item.get("brand", ""))
        elif "product" in col_key:
            target_text = str(item.get("product_type", ""))
        elif "price" in col_key:
            target_text = str(item.get("price", ""))
        elif "location" in col_key:
            target_text = str(item.get("location", ""))
        else:
            # All Columns concatenated
            target_text = " ".join([
                str(item.get("brand", "")),
                str(item.get("product_type", "")),
                str(item.get("title", "")),
                str(item.get("item_id", "")),
                str(item.get("seller", "")),
                str(item.get("seller_origin", "")),
                str(item.get("threat_badge", "")),
                str(item.get("location", "")),
                str(item.get("price", "")),
                str(item.get("keyword", "")),
            ])

        target_lower = target_text.lower()

        import shlex
        try:
            raw_tokens = shlex.split(query_str)
        except Exception:
            raw_tokens = query_str.split()

        positive_tokens = []
        negative_tokens = []

        for tok in raw_tokens:
            tok = tok.strip()
            if not tok:
                continue
            if tok.startswith("-") and len(tok) > 1:
                negative_tokens.append(tok[1:].lower())
            elif tok.startswith("+") and len(tok) > 1:
                positive_tokens.append(tok[1:].lower())
            else:
                positive_tokens.append(tok.lower())

        # Check negative exclusions (item is rejected if ANY negative token is found)
        for neg in negative_tokens:
            if neg in target_lower:
                return False

        # Check positive inclusions (item must contain ALL positive tokens)
        for pos in positive_tokens:
            if pos not in target_lower:
                return False

        return True

    def _update_results_table(self, items):
        """Append newly scraped items honoring the active live search filter."""
        def _add():
            query = self.filter_var.get().strip() if hasattr(self, "filter_var") else ""
            target_col = self.filter_col_var.get() if hasattr(self, "filter_col_var") else "Title"
            size_key = self.thumb_size_var.get() if hasattr(self, "thumb_size_var") else "Medium (100px)"
            cfg = THUMB_CONFIG.get(size_key, THUMB_CONFIG["Medium (100px)"])
            is_thumbs = (cfg["img_size"] > 0)
            ph = self._get_placeholder_thumb(cfg["img_size"]) if is_thumbs else ""

            for item in items:
                if "product_type" not in item:
                    item["product_type"] = ""

                # Evaluate Threat Intel from DataStore cache
                seller_clean = str(item.get("seller", "")).replace("🛡️", "").replace("(Authorized)", "").strip()
                cached_intel = self.data_store.get_seller_intel(seller_clean)
                seller_country = item.get("seller_origin") or (cached_intel.get("country") if cached_intel else "")
                loc = item.get("location", "")

                assessment = self.data_store.compute_threat_assessment(seller_country, loc)
                orig_display = f"{assessment['flag']} {assessment['country']}" if assessment['country'] != "Unknown" else "❓ Unresolved"
                threat_display = assessment['badge']
                item["seller_origin"] = assessment.get("country", "Unknown")
                item["threat_badge"] = threat_display

                # Check High-Risk filter checkbox
                if hasattr(self, "filter_high_risk_var") and self.filter_high_risk_var.get():
                    if not (assessment.get("is_high_risk") or assessment.get("is_3pl_hub")):
                        continue

                if query and not self._item_matches_filter(item, query, target_col):
                    continue

                img_url = item.get("image_url", "")
                iid = self.result_tree.insert("", "end", text="", image=ph, values=(
                    item.get("brand", ""),
                    item.get("product_type", ""),
                    item.get("title", ""),
                    item.get("item_id", ""),
                    item.get("price", ""),
                    item.get("seller", ""),
                    item.get("location", ""),
                    img_url,
                    item.get("url", ""),
                ))

                if is_thumbs and img_url:
                    self._fetch_inline_thumbnail(iid, img_url)

            if query:
                vis = len(self.result_tree.get_children())
                self.result_count.set(f"{vis} / {len(self.results)} listings (filtered)")
            else:
                self.result_count.set(f"{len(self.results)} listings")
        self.after(0, _add)

    def _repopulate_results_table(self):
        """Clear and refill result_tree from self.results honoring current filter."""
        self.result_tree.delete(*self.result_tree.get_children())
        query = self.filter_var.get().strip() if hasattr(self, "filter_var") else ""
        target_col = self.filter_col_var.get() if hasattr(self, "filter_col_var") else "Title"
        size_key = self.thumb_size_var.get() if hasattr(self, "thumb_size_var") else "Medium (100px)"
        cfg = THUMB_CONFIG.get(size_key, THUMB_CONFIG["Medium (100px)"])
        is_thumbs = (cfg["img_size"] > 0)
        ph = self._get_placeholder_thumb(cfg["img_size"]) if is_thumbs else ""

        count = 0
        for item in self.results:
            if "product_type" not in item:
                item["product_type"] = ""

            # Evaluate Threat Intel from DataStore cache
            seller_clean = str(item.get("seller", "")).replace("🛡️", "").replace("(Authorized)", "").strip()
            cached_intel = self.data_store.get_seller_intel(seller_clean)
            seller_country = item.get("seller_origin") or (cached_intel.get("country") if cached_intel else "")
            loc = item.get("location", "")

            assessment = self.data_store.compute_threat_assessment(seller_country, loc)
            orig_display = f"{assessment['flag']} {assessment['country']}" if assessment['country'] != "Unknown" else "❓ Unresolved"
            threat_display = assessment['badge']
            item["seller_origin"] = assessment.get("country", "Unknown")
            item["threat_badge"] = threat_display

            # Check High-Risk filter checkbox
            if hasattr(self, "filter_high_risk_var") and self.filter_high_risk_var.get():
                if not (assessment.get("is_high_risk") or assessment.get("is_3pl_hub")):
                    continue

            if query and not self._item_matches_filter(item, query, target_col):
                continue

            img_url = item.get("image_url", "")
            iid = self.result_tree.insert("", "end", text="", image=ph, values=(
                item.get("brand", ""),
                item.get("product_type", ""),
                item.get("title", ""),
                item.get("item_id", ""),
                item.get("price", ""),
                item.get("seller", ""),
                orig_display,
                threat_display,
                item.get("location", ""),
                img_url,
                item.get("url", ""),
            ))

            if is_thumbs and img_url:
                self._fetch_inline_thumbnail(iid, img_url)

            count += 1

        if query or (hasattr(self, "filter_high_risk_var") and self.filter_high_risk_var.get()):
            self.result_count.set(f"{count} / {len(self.results)} listings (filtered)")
        else:
            self.result_count.set(f"{len(self.results)} listings")

    def _sort_by_column(self, col):
        """Sort self.results by column with numeric/price intelligence and update headers."""
        if not self.results:
            return
        descending = self.sort_directions.get(col, False)
        self.sort_directions[col] = not descending
        field = self.field_map.get(col, col)

        def get_sort_key(item):
            val = item.get(field, "")
            if col == "price":
                m = re.search(r"[\d,]+(?:\.\d+)?", str(val))
                if m:
                    try:
                        return float(m.group(0).replace(",", ""))
                    except ValueError:
                        return 0.0
                return 0.0
            elif col == "item_id":
                try:
                    return int(val) if val else 0
                except ValueError:
                    return 0
            return str(val).lower()

        self.results.sort(key=get_sort_key, reverse=descending)
        self._repopulate_results_table()

        # Update table column headers with sort arrow
        for c in self.result_tree["columns"]:
            label = self.col_labels[c]
            if c == col:
                arrow = " ▼" if descending else " ▲"
                self.result_tree.heading(c, text=f"{label}{arrow}",
                                         command=lambda _c=c: self._sort_by_column(_c))
            else:
                self.result_tree.heading(c, text=label,
                                         command=lambda _c=c: self._sort_by_column(_c))

    def _remove_duplicates(self):
        """Deduplicate harvested listings based on Item ID (or URL)."""
        if not self.results:
            messagebox.showinfo("Deduplicate", "No results to deduplicate.")
            return

        initial_count = len(self.results)
        unique_results = []
        seen = set()

        for item in self.results:
            item_id = item.get("item_id")
            dedup_key = item_id if item_id else item.get("url")
            if dedup_key and dedup_key not in seen:
                seen.add(dedup_key)
                unique_results.append(item)
            elif not dedup_key:
                unique_results.append(item)

        removed = initial_count - len(unique_results)
        self.results = unique_results
        self.seen_item_ids = seen
        self._repopulate_results_table()

        msg = f"Deduplication complete: Removed {removed} duplicate(s). {len(self.results)} unique listings remain."
        self._log(f"✂ {msg}")
        messagebox.showinfo("Deduplication", f"Removed {removed} duplicate listings.\n{len(self.results)} unique listings remain.")

    def _remove_selected_results(self):
        """Remove selected listings in the results table from session."""
        selected = self.result_tree.selection()
        if not selected:
            messagebox.showinfo("Select", "Select one or more rows in the results table to remove.")
            return

        removed_keys = set()
        for item_iid in selected:
            vals = self.result_tree.item(item_iid)["values"]
            if len(vals) > 3:
                item_id = str(vals[3]).strip()
                url = str(vals[8]).strip() if len(vals) > 8 else ""
                if item_id:
                    removed_keys.add(item_id)
                elif url:
                    removed_keys.add(url)
            self.result_tree.delete(item_iid)

        self.results = [
            item for item in self.results
            if str(item.get("item_id", "")).strip() not in removed_keys and
               str(item.get("url", "")).strip() not in removed_keys
        ]
        self.seen_item_ids = {
            item.get("item_id") or item.get("url") for item in self.results
            if item.get("item_id") or item.get("url")
        }
        self.result_count.set(f"{len(self.results)} listings")
        self._log(f"✕ Removed {len(selected)} selected listing(s). {len(self.results)} total remaining.")

    def _clear_results(self):
        if messagebox.askyesno("Clear", "Clear all harvested results?"):
            self.results.clear()
            self.seen_item_ids.clear()
            self.executed_jobs.clear()
            self.result_tree.delete(*self.result_tree.get_children())
            self.result_count.set("0 listings")
            self._hide_preview_popup()
            self._log("Results cleared.")

    def _open_url(self, ev):
        sel = self.result_tree.focus()
        if sel:
            values = self.result_tree.item(sel)["values"]
            listing_url = values[10] if len(values) > 10 else (values[8] if len(values) > 8 else "")
            if listing_url:
                webbrowser.open(listing_url)

    def _show_result_context_menu(self, event):
        """Right-click context menu on results table rows."""
        row_id = self.result_tree.identify_row(event.y)
        if row_id:
            # If right clicked item not in selection, select it
            if row_id not in self.result_tree.selection():
                self.result_tree.selection_set(row_id)

        selected = self.result_tree.selection()
        if not selected:
            return

        t = self.theme
        menu = tk.Menu(self, tearoff=0, bg=t["panel"], fg=t["text"],
                       activebackground=t["accent"], activeforeground="black" if t.get("name","").startswith("⚡") else "white")

        menu.add_command(label="💾 📊 Export All Results to Excel (Ctrl+E)", command=self._export)
        menu.add_command(label="🌐 🗺️ Multi-Locale Global Expander", command=self._open_multi_locale_expander)
        menu.add_separator()
        menu.add_command(label="🔗 🕵️ Find Connected Sellers by Photo / Carousel", command=self._open_connected_network_scanner)
        menu.add_command(label="🏪 ➕ Add Selected Seller to Stores Input", command=self._add_selected_result_seller_to_stores)
        menu.add_command(label="🌍 🚨 Resolve Seller Origin & Threat Intel", command=self._enrich_seller_threat_intel)
        menu.add_command(label="🛡️ Whitelist This Seller (Authorized Dealer)", command=self._whitelist_selected_result_seller)
        menu.add_separator()
        menu.add_command(label="☑️ Select All Rows (Ctrl+A)", command=self._select_all_results)
        menu.add_command(label="🌐 Open in Browser", command=lambda: self._open_url(None))
        menu.add_command(label="📋 Copy Selected Listing URLs", command=self._copy_selected_urls)
        menu.add_command(label="📋 Copy All Listing URLs", command=self._copy_all_listing_urls)
        menu.add_command(label="🏪 Enrich Selected Seller Names", command=self._enrich_sellers)
        menu.add_separator()
        menu.add_command(label="✕ Remove Selected", command=self._remove_selected_results)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _add_selected_result_seller_to_stores(self):
        """Append highlighted results table seller username directly into Stores / Sellers box."""
        selected = self.result_tree.selection()
        if not selected:
            return
        added = []
        for iid in selected:
            for itm in self.results:
                if str(itm.get("item_id", "")) == str(self.result_tree.set(iid, "item_id")):
                    s = str(itm.get("seller", "")).replace("🛡️", "").replace("(Authorized)", "").strip()
                    if s and s not in ("Unknown", "Resolving..."):
                        added.append(s)
                    break
        unique = list(dict.fromkeys(added))
        if not unique:
            return
        curr = self.store_text.get("1.0", "end").strip()
        ph = self.store_placeholder.strip()
        if not curr or curr == ph:
            self.store_text.delete("1.0", "end")
            self.store_text.insert("1.0", "\n".join(unique) + "\n")
            self.store_text.config(fg=self.theme["text"])
        else:
            lines = [l.strip() for l in curr.splitlines() if l.strip()]
            existing_lowers = [l.lower() for l in lines]
            for u in unique:
                if u.lower() not in existing_lowers:
                    lines.append(u)
            self.store_text.delete("1.0", "end")
            self.store_text.insert("1.0", "\n".join(lines) + "\n")
            self.store_text.config(fg=self.theme["text"])
        self._log(f"🏪 Added {len(unique)} seller(s) from Results to Stores box: {', '.join(unique)}")
        self._status(f"Added {len(unique)} seller(s) to Stores box.")

    def _select_all_results(self, event=None):
        """Select all rows in the results table."""
        children = self.result_tree.get_children()
        if children:
            self.result_tree.selection_set(children)
            self._on_result_tree_select()
        return "break"

    def _on_result_tree_select(self, event=None):
        """Update live selected row counter in Results toolbar."""
        selected_count = len(self.result_tree.selection())
        total_count = len(self.results)
        vis_count = len(self.result_tree.get_children())
        if selected_count > 0:
            if vis_count < total_count:
                self.result_count.set(f"{vis_count} / {total_count} listings ({selected_count} selected)")
            else:
                self.result_count.set(f"{total_count} listings ({selected_count} selected)")
        else:
            if vis_count < total_count:
                self.result_count.set(f"{vis_count} / {total_count} listings (filtered)")
            else:
                self.result_count.set(f"{total_count} listings")

    def _copy_all_listing_urls(self):
        """Copy all harvested listing URLs in the results table to clipboard."""
        if not self.results:
            messagebox.showinfo("Copy URLs", "No listings in the results table to copy.")
            return
        urls = [it.get("url") for it in self.results if it.get("url")]
        if not urls:
            messagebox.showinfo("Copy URLs", "No valid URLs found.")
            return
        self.clipboard_clear()
        self.clipboard_append("\n".join(urls))
        self._status(f"📋 Copied {len(urls)} listing URLs to clipboard.")
        self._log(f"📋 Copied all {len(urls)} listing URLs to clipboard.")
        messagebox.showinfo("Copied", f"Copied {len(urls)} listing URLs to clipboard!")

    def _copy_selected_urls(self):
        """Copy selected listing URLs to clipboard."""
        selected = self.result_tree.selection()
        if not selected:
            messagebox.showinfo("Copy URLs", "Select one or more rows to copy URLs.")
            return
        urls = []
        for iid in selected:
            vals = self.result_tree.item(iid)["values"]
            url = vals[10] if len(vals) > 10 else (vals[8] if len(vals) > 8 else "")
            if url:
                urls.append(url)
        if not urls:
            messagebox.showinfo("Copy URLs", "No valid URLs on selected rows.")
            return
        self.clipboard_clear()
        self.clipboard_append("\n".join(urls))
        self._status(f"📋 Copied {len(urls)} selected listing URLs to clipboard.")
        self._log(f"📋 Copied {len(urls)} selected listing URLs to clipboard.")

    def _open_multi_locale_expander(self):
        """Open the Global Multi-Locale Expander & Compliance Exporter modal."""
        if not self.results:
            messagebox.showinfo("Multi-Locale Expander", "No harvested listings in the results table to expand.")
            return
        selected_iids = self.result_tree.selection()
        target_items = []
        if selected_iids:
            for iid in selected_iids:
                vals = self.result_tree.item(iid)["values"]
                if len(vals) > 3:
                    item_id = str(vals[3]).strip()
                    for it in self.results:
                        if str(it.get("item_id", "")).strip() == item_id:
                            target_items.append(it)
                            break
        else:
            target_items = list(self.results)
        
        if hasattr(self, "_win_multilocale") and self._win_multilocale and self._win_multilocale.winfo_exists():
            self._win_multilocale.lift()
            self._win_multilocale.focus_force()
            return
        self._win_multilocale = MultiLocaleModal(self, target_items)

    def _open_whitelist_manager_window(self):
        """Open the Authorized Dealership & Whitelist Management Window."""
        if hasattr(self, "_win_whitelist") and self._win_whitelist and self._win_whitelist.winfo_exists():
            self._win_whitelist.lift()
            self._win_whitelist.focus_force()
            return
        self._win_whitelist = WhitelistManagerModal(self)

    def _whitelist_selected_result_seller(self):
        """Whitelist the seller from the selected row in results table."""
        sel = self.result_tree.focus()
        if not sel:
            selected = self.result_tree.selection()
            if selected:
                sel = selected[0]
        if not sel:
            return
        vals = self.result_tree.item(sel)["values"]
        seller_handle = str(vals[5]).replace("🛡️", "").replace("(Authorized)", "").strip() if len(vals) > 5 else ""
        brand_val = vals[0] if len(vals) > 0 else "General / All Brands"
        if not seller_handle or seller_handle in ("Resolving...", "Unknown"):
            messagebox.showwarning("No Seller", "No valid seller handle found on this row.")
            return
        if self.data_store.is_seller_whitelisted(seller_handle):
            messagebox.showinfo("Already Whitelisted", f"Seller '{seller_handle}' is already on your Authorized Whitelist.")
            return
        
        d_name = simpledialog.askstring("Authorized Dealership", f"Enter Dealership / Entity Name for '{seller_handle}' (optional):", initialvalue="Authorized Dealer", parent=self)
        if d_name is None:
            return
        notes = simpledialog.askstring("Analyst Notes", f"Notes for '{seller_handle}' (optional):", initialvalue="Client Approved Whitelist", parent=self) or ""
        self.data_store.add_to_whitelist(seller_handle, brand=brand_val, dealer_name=d_name, notes=notes)
        self._log(f"🛡️ Added '{seller_handle}' to Authorized Whitelist ({brand_val}).")
        messagebox.showinfo("Seller Whitelisted", f"Successfully added '{seller_handle}' to your Authorized Dealer Whitelist!\n\nThis seller will be automatically shielded and highlighted across scans.")
        if hasattr(self, "_repopulate_results_table"):
            self._repopulate_results_table()

    def _copy_selected_url(self):
        """Copy selected listing URL to clipboard."""
        sel = self.result_tree.focus()
        if not sel:
            selected = self.result_tree.selection()
            if selected:
                sel = selected[0]
        if sel:
            values = self.result_tree.item(sel)["values"]
            listing_url = values[10] if len(values) > 10 else (values[8] if len(values) > 8 else "")
            if listing_url:
                self.clipboard_clear()
                self.clipboard_append(listing_url)
                self._status("📋 Listing URL copied to clipboard.")

    def _open_connected_network_scanner(self):
        """Open the Connected Seller & Visual Syndicate Discovery Modal for the selected listing."""
        sel = self.result_tree.focus()
        if not sel:
            selected = self.result_tree.selection()
            if selected:
                sel = selected[0]
        if not sel:
            messagebox.showinfo("Network Scanner", "Please select a listing from the results table first.")
            return

        values = self.result_tree.item(sel)["values"]
        target_item = {
            "brand": values[0] if len(values) > 0 else "",
            "product_type": values[1] if len(values) > 1 else "",
            "title": values[2] if len(values) > 2 else "",
            "item_id": str(values[3]) if len(values) > 3 else "",
            "price": str(values[4]) if len(values) > 4 else "",
            "seller": str(values[5]) if len(values) > 5 else "",
            "seller_origin": str(values[6]) if len(values) > 6 else "",
            "threat_badge": str(values[7]) if len(values) > 7 else "",
            "location": str(values[8]) if len(values) > 8 else "",
            "image_url": str(values[9]) if len(values) > 9 else "",
            "url": str(values[10]) if len(values) > 10 else (str(values[8]) if len(values) > 8 else ""),
        }
        ConnectedNetworkModal(self, target_item)

    def _enrich_seller_threat_intel(self):
        """
        Parallel resolve true registered seller origin (country) and 3PL drop-shipping
        smokescreen threat flags across all session listings.
        """
        if not self.results:
            messagebox.showinfo("Threat Intel", "No harvested listings to analyze.")
            return

        selected_iids = self.result_tree.selection()
        target_items = []
        if selected_iids:
            for item_iid in selected_iids:
                vals = self.result_tree.item(item_iid)["values"]
                if len(vals) > 3:
                    item_id = str(vals[3]).strip()
                    for it in self.results:
                        if str(it.get("item_id", "")).strip() == item_id:
                            target_items.append(it)
                            break
        else:
            target_items = list(self.results)

        # Collect unique sellers
        sellers_to_query = []
        for it in target_items:
            s = it.get("seller", "")
            if s and s not in ("Unknown", "Resolving..."):
                clean = str(s).replace("🛡️", "").replace("(Authorized)", "").strip()
                if clean:
                    sellers_to_query.append(clean)

        unique_sellers = list(dict.fromkeys(sellers_to_query))
        if not unique_sellers:
            messagebox.showinfo("Threat Intel", "No valid seller handles found to analyze.")
            return

        self._status(f"Resolving Threat Intel for {len(unique_sellers)} sellers in parallel...")
        self._log(f"🌍 Starting Threat Intel & 3PL Smokescreen scan for {len(unique_sellers)} sellers...")

        def _worker():
            # Check data_store cache first
            uncached = []
            cached_intel = {}
            for s in unique_sellers:
                cached = self.data_store.get_seller_intel(s)
                if cached and cached.get("country") and cached.get("country") != "Unknown":
                    cached_intel[s] = cached
                else:
                    uncached.append(s)

            # Resolve uncached in parallel via high-speed batch resolver
            if uncached:
                resolved_map = self.scraper.batch_resolve_seller_countries(uncached)
                for s, data in resolved_map.items():
                    country_val = data.get("country", "Unknown")
                    m_since = data.get("member_since", "")
                    if country_val and country_val != "Unknown":
                        self.data_store.set_seller_intel(s, country_val, member_since=m_since)
                        cached_intel[s] = {"country": country_val, "member_since": m_since}

            # Update results with enriched intel
            updated_count = 0
            critical_threats = 0
            for it in target_items:
                s = str(it.get("seller", "")).replace("🛡️", "").replace("(Authorized)", "").strip()
                intel = cached_intel.get(s) or self.data_store.get_seller_intel(s)
                seller_country = intel.get("country", "") if intel else ""
                loc = it.get("location", "")
                assessment = self.data_store.compute_threat_assessment(seller_country, loc)

                it["seller_origin"] = assessment.get("country", "Unknown")
                it["seller_flag"] = assessment.get("flag", "❓")
                it["threat_score"] = assessment.get("score", "UNKNOWN")
                it["threat_badge"] = assessment.get("badge", "Unresolved")

                if assessment.get("score") == "CRITICAL":
                    critical_threats += 1
                updated_count += 1

            def _apply():
                self._repopulate_results_table()
                msg = f"Enriched Threat Intel for {updated_count} listings across {len(unique_sellers)} unique sellers!"
                if critical_threats > 0:
                    msg += f"\n\n🚨 IDENTIFIED {critical_threats} CRITICAL 3PL SMOKESCREEN / GHOST ORIGIN TARGETS!"
                self._status(f"Threat Intel scan complete: {updated_count} enriched.")
                self._log(f"✅ Threat Intel scan complete: {updated_count} listings enriched ({critical_threats} critical threats).")
                messagebox.showinfo("Threat Intel Complete", msg, parent=self)

            self.after(0, _apply)

        threading.Thread(target=_worker, daemon=True).start()

    def _enrich_sellers(self):
        """Enrich real seller/merchant/store names across AliExpress, Wish, Temu, and Printerval listings."""
        if not self.results:
            messagebox.showinfo("Enrich Sellers", "No harvested listings to enrich.")
            return

        selected_iids = self.result_tree.selection()
        target_items = []

        if selected_iids:
            for item_iid in selected_iids:
                vals = self.result_tree.item(item_iid)["values"]
                if len(vals) > 3:
                    item_id = str(vals[3]).strip()
                    url = str(vals[8]).strip() if len(vals) > 8 else (str(vals[7]).strip() if len(vals) > 7 else "")
                    for it in self.results:
                        if (item_id and str(it.get("item_id", "")).strip() == item_id) or (url and str(it.get("url", "")).strip() == url):
                            if it not in target_items:
                                target_items.append(it)
                            break
        else:
            # Check all items in session needing seller enrichment
            for it in self.results:
                mkt = it.get("marketplace", "").lower()
                url = it.get("url", "").lower()
                seller = str(it.get("seller", "")).strip()
                if not seller or any(g in seller.lower() for g in ("ebay seller", "global search", "aliexpress global", "creator", "unknown", "printerval creator")):
                    target_items.append(it)

        if not target_items:
            messagebox.showinfo("Enrich Sellers", "No listings requiring seller enrichment found (all items already have specific store/merchant names).")
            return

        if not messagebox.askyesno("Enrich Sellers", f"Enrich real merchant/store names for {len(target_items)} listing(s)?\n\nThis will look up the specific seller/store ID for each listing."):
            return

        is_headless = self.headless_var.get()
        self.scraper.headless = is_headless
        self.aliexpress_scraper.headless = is_headless
        self.wish_scraper.headless = is_headless
        self.temu_scraper.headless = is_headless
        self.printerval_scraper.headless = is_headless

        self._log(f"🏪 Starting Seller Name Enrichment for {len(target_items)} item(s)...")
        self._status(f"🏪 Enriching {len(target_items)} sellers...")
        self.stop_event.clear()
        self.stop_btn.config(state="normal")

        def _worker():
            enriched_count = 0
            
            def _on_prog(current, total, item):
                nonlocal enriched_count
                s_name = str(item.get("seller", "")).strip()
                if s_name and not any(g in s_name.lower() for g in ("ebay seller", "global search", "aliexpress global", "unknown")):
                    enriched_count += 1
                self.after(0, lambda: self._status(f"🏪 Enriching Sellers: {current}/{total} -> '{s_name}'"))
                self.after(0, lambda: self._log(f"  ✓ [{item.get('marketplace', 'Platform')}] Enriched: '{item.get('title', '')[:40]}...' → Seller: '{s_name}', Price: {item.get('price', '')}"))
                self.after(0, lambda: self._repopulate_results_table())

            try:
                # Group items by platform
                ebay_items = [it for it in target_items if "ebay" in it.get("marketplace", "").lower() or "ebay.com" in it.get("url", "").lower()]
                ali_items = [it for it in target_items if "ali" in it.get("marketplace", "").lower() or "aliexpress" in it.get("url", "").lower()]
                wish_items = [it for it in target_items if "wish" in it.get("marketplace", "").lower() or "wish" in it.get("url", "").lower()]
                temu_items = [it for it in target_items if "temu" in it.get("marketplace", "").lower() or "temu" in it.get("url", "").lower()]
                printerval_items = [it for it in target_items if "printerval" in it.get("marketplace", "").lower() or "printerval" in it.get("url", "").lower()]

                if ebay_items and not self.stop_event.is_set():
                    self.scraper.enrich_ebay_seller_info(
                        ebay_items,
                        progress_callback=_on_prog,
                        stop_event=self.stop_event
                    )

                if ali_items and not self.stop_event.is_set():
                    self.aliexpress_scraper.enrich_seller_info(
                        ali_items,
                        progress_callback=_on_prog,
                        stop_event=self.stop_event
                    )

                if wish_items and not self.stop_event.is_set():
                    self.wish_scraper.enrich_seller_info(
                        wish_items,
                        progress_callback=_on_prog,
                        stop_event=self.stop_event
                    )

                if temu_items and not self.stop_event.is_set():
                    self.temu_scraper.enrich_seller_info(
                        temu_items,
                        progress_callback=_on_prog,
                        stop_event=self.stop_event
                    )

                if printerval_items and not self.stop_event.is_set():
                    self.printerval_scraper.enrich_seller_info(
                        printerval_items,
                        progress_callback=_on_prog,
                        stop_event=self.stop_event
                    )

            finally:
                self.after(0, lambda: self.stop_btn.config(state="disabled"))
                self.after(0, lambda: self._status(f"🏪 Seller enrichment complete! ({enriched_count} updated)"))
                self.after(0, lambda: self._log(f"🏪 Seller enrichment finished: Updated store names for {enriched_count} item(s)."))
                self.after(0, lambda: self._repopulate_results_table())

        threading.Thread(target=_worker, daemon=True).start()

    # ── Inline & Hover Thumbnail Preview Engine ──────────────────────────────
    def _get_placeholder_thumb(self, size_px=60):
        if not hasattr(self, "_placeholders"):
            self._placeholders = {}
        if size_px not in self._placeholders:
            ph = Image.new("RGBA", (size_px, size_px), (35, 40, 52, 255))
            self._placeholders[size_px] = ImageTk.PhotoImage(ph)
        return self._placeholders[size_px]

    def _get_scaled_photo(self, pil_img, size_px):
        """Scale and center a PIL Image into a square PhotoImage."""
        img_copy = pil_img.copy()
        img_copy.thumbnail((size_px, size_px), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (size_px, size_px), (0, 0, 0, 0))
        offset = ((size_px - img_copy.width) // 2, (size_px - img_copy.height) // 2)
        canvas.paste(img_copy, offset)
        return ImageTk.PhotoImage(canvas)

    def _fetch_inline_thumbnail(self, iid, image_url):
        """Asynchronously download and display square inline thumbnail in result_tree with retry resiliency."""
        if not image_url or not str(image_url).startswith("http"):
            return

        size_key = self.thumb_size_var.get() if hasattr(self, "thumb_size_var") else "Medium (100px)"
        cfg = THUMB_CONFIG.get(size_key, THUMB_CONFIG["Medium (100px)"])
        if cfg["img_size"] <= 0:
            return

        cache_key = (size_key, image_url)
        if cache_key in self.inline_img_cache:
            photo = self.inline_img_cache[cache_key]
            if self.result_tree.exists(iid):
                self.result_tree.item(iid, image=photo)
            return

        if image_url in self.raw_img_cache:
            photo = self._get_scaled_photo(self.raw_img_cache[image_url], cfg["img_size"])
            self.inline_img_cache[cache_key] = photo
            if self.result_tree.exists(iid):
                self.result_tree.item(iid, image=photo)
            return

        cur_size_key = self.thumb_size_var.get()
        cur_cfg = THUMB_CONFIG.get(cur_size_key, THUMB_CONFIG["Medium (100px)"])
        cur_img_size = cur_cfg.get("img_size", 100)

        def _worker(sz_key=cur_size_key, sz_px=cur_img_size):
            for attempt in range(2):
                try:
                    req = urllib.request.Request(str(image_url), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    with urllib.request.urlopen(req, timeout=7) as resp:
                        data = resp.read()
                    pil_img = Image.open(io.BytesIO(data)).convert("RGBA")
                    self.raw_img_cache[image_url] = pil_img
                    
                    if sz_px > 0:
                        photo = self._get_scaled_photo(pil_img, sz_px)
                        self.inline_img_cache[(sz_key, image_url)] = photo
                        
                        def _apply():
                            if self.result_tree.exists(iid) and self.thumb_size_var.get() != "Off (Text Only)":
                                self.result_tree.item(iid, image=photo)
                        self.after(0, _apply)
                    break
                except Exception:
                    if attempt == 0:
                        time.sleep(0.4)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_thumb_size_changed(self, event=None):
        """Handle user changing thumbnail size (Off, Small, Medium, Large, Extra Large)."""
        size_key = self.thumb_size_var.get()
        self.data_store.set_setting("thumb_size", size_key)
        self.show_preview_var.set(size_key != "Off (Text Only)")
        cfg = THUMB_CONFIG.get(size_key, THUMB_CONFIG["Medium (100px)"])

        style = ttk.Style()
        style.configure("Results.Treeview", rowheight=cfg["rowheight"])
        self.result_tree.configure(show=cfg["show"], style="Results.Treeview")
        self.result_tree.column("#0", width=cfg["col_width"], minwidth=cfg["col_width"], anchor="center")
        self.result_tree.heading("#0", text="Preview" if cfg["img_size"] > 0 else "", anchor="center")

        if cfg["img_size"] <= 0:
            self._hide_preview_popup()

        if self.results:
            self._repopulate_results_table()

    def _on_tree_mouse_motion(self, event):
        """Handle cursor motion over results table to trigger thumbnail preview."""
        row_id = self.result_tree.identify_row(event.y)
        if not row_id:
            self._hide_preview_popup()
            return

        if row_id == self.last_hovered_iid and self.preview_win:
            return

        self.last_hovered_iid = row_id
        if self.preview_cancel_id:
            self.after_cancel(self.preview_cancel_id)
        
        # Debounce preview slightly to keep UI fluid
        self.preview_cancel_id = self.after(120, self._show_preview_for_row, row_id, event.x_root, event.y_root)

    def _hide_preview_popup(self, event=None):
        if self.preview_cancel_id:
            self.after_cancel(self.preview_cancel_id)
            self.preview_cancel_id = None
        if self.preview_win:
            try:
                self.preview_win.destroy()
            except Exception:
                pass
            self.preview_win = None
        self.last_hovered_iid = None

    def _show_preview_for_row(self, row_id, x_root, y_root):
        if not self.result_tree.exists(row_id):
            return
        vals = self.result_tree.item(row_id)["values"]
        if len(vals) < 8:
            return

        title     = str(vals[2])
        price     = str(vals[4])
        location  = str(vals[6])
        image_url = str(vals[7]).strip()

        if not image_url or not image_url.startswith("http"):
            self._hide_preview_popup()
            return

        t = self.theme
        if self.preview_win:
            try: self.preview_win.destroy()
            except Exception: pass

        self.preview_win = tk.Toplevel(self)
        self.preview_win.wm_overrideredirect(True)
        self.preview_win.configure(bg=t["border"], padx=1, pady=1)

        pop_frame = tk.Frame(self.preview_win, bg=t["panel"], padx=6, pady=6)
        pop_frame.pack(fill="both", expand=True)

        # Image placeholder
        img_lbl = tk.Label(pop_frame, text="Loading image...", bg=t["entry_bg"], fg=t["subtext"],
                           font=FONT_SM, width=22, height=8)
        img_lbl.pack(pady=(0, 4))

        # Truncated title & price
        short_title = (title[:48] + "...") if len(title) > 50 else title
        title_lbl = tk.Label(pop_frame, text=short_title, bg=t["panel"], fg=t["text"],
                             font=FONT_SM, wraplength=180, justify="left")
        title_lbl.pack(anchor="w")

        info_text = f"{price}" + (f" • {location}" if location else "")
        info_lbl = tk.Label(pop_frame, text=info_text, bg=t["panel"], fg=t["accent"],
                            font=("Segoe UI", 9, "bold"))
        info_lbl.pack(anchor="w", pady=(2, 0))

        # Position window near cursor, keeping strictly inside the application display bounds
        app_x = self.winfo_rootx()
        app_y = self.winfo_rooty()
        app_w = self.winfo_width()
        app_h = self.winfo_height()

        pop_w = 210
        pop_h = 240

        # If placing to the right overflows the window bounds, place to the left
        if x_root + 18 + pop_w > app_x + app_w:
            win_x = max(app_x + 10, x_root - pop_w - 18)
        else:
            win_x = x_root + 18

        if y_root + pop_h > app_y + app_h:
            win_y = max(app_y + 10, app_y + app_h - pop_h - 10)
        else:
            win_y = max(app_y + 10, y_root - 70)

        self.preview_win.geometry(f"+{win_x}+{win_y}")

        # Check in-memory cache
        if image_url in self.img_cache:
            img_lbl.configure(image=self.img_cache[image_url], text="", width=0, height=0)
        elif image_url in self.raw_img_cache:
            photo = self._get_scaled_photo(self.raw_img_cache[image_url], 180)
            self.img_cache[image_url] = photo
            img_lbl.configure(image=photo, text="", width=0, height=0)
        else:
            threading.Thread(target=self._fetch_and_render_img,
                             args=(image_url, img_lbl, self.preview_win), daemon=True).start()

    def _fetch_and_render_img(self, url, img_lbl, target_win):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=7) as resp:
                data = resp.read()
            pil_img = Image.open(io.BytesIO(data)).convert("RGBA")
            self.raw_img_cache[url] = pil_img
            photo = self._get_scaled_photo(pil_img, 180)
            self.img_cache[url] = photo

            def _apply():
                if target_win == self.preview_win and img_lbl.winfo_exists():
                    img_lbl.configure(image=photo, text="", width=0, height=0)
            self.after(0, _apply)
        except Exception:
            def _fail():
                if target_win == self.preview_win and img_lbl.winfo_exists():
                    img_lbl.configure(text="(Image preview\nunavailable)", height=5)
            self.after(0, _fail)

    # ══════════════════════════════════════════════════════════════════════════
    #  EASTER EGGS & FUN DETAILS
    # ══════════════════════════════════════════════════════════════════════════
    def _check_konami(self, event):
        """Global Konami code detection (↑ ↑ ↓ ↓ ← → ← → B A)."""
        key = event.keysym
        self.konami_buffer.append(key)
        if len(self.konami_buffer) > len(self.konami_sequence):
            self.konami_buffer.pop(0)

        if self.konami_buffer == self.konami_sequence:
            self._trigger_konami_easter_egg()
            self.konami_buffer.clear()

    def _trigger_wick_easter_egg(self):
        """John Wick / The Continental High Table Excommunicado easter egg."""
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

        self.data_store.unlock_wick()
        secret_name = THEMES["continental"]["name"]
        vals = list(self.theme_combo["values"])
        if secret_name not in vals:
            vals.append(secret_name)
            self.theme_combo["values"] = vals
        self.theme_var.set(secret_name)
        self._on_theme_changed()

        self._log("=" * 75)
        self._log("🪙 ─────────────────────────────────────────────────────────────────────────")
        self._log("🪙 [THE CONTINENTAL HOTEL — NEW YORK]")
        self._log("🪙 'Good evening, Mr. Wick. Membership status: Recognized. Services: Available.'")
        self._log("🪙 'Rules... without them, we live with the animals.'")
        self._log("🪙 [HIGH TABLE EXCOMMUNICADO TARGETING PROTOCOL INITIALIZED]")
        self._log("🪙 ─────────────────────────────────────────────────────────────────────────")
        self._log("=" * 75)
        self._status("🪙 THE CONTINENTAL: High Table Excommunicado Protocol Engaged!")
        # Custom Themed Dark Continental Concierge Modal
        win = tk.Toplevel(self)
        win.title("🪙 The Continental — New York")
        win.configure(bg="#0A0B0E")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        self._apply_dark_titlebar(win)

        # Center modal
        win.update_idletasks()
        p_x = self.winfo_rootx()
        p_y = self.winfo_rooty()
        p_w = self.winfo_width()
        p_h = self.winfo_height()
        w, h = 500, 340
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        card = tk.Frame(win, bg="#12141A", padx=20, pady=18, highlightbackground="#D4AF37", highlightthickness=2)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(card, text="🪙 THE CONTINENTAL", font=("Segoe UI", 15, "bold"), bg="#12141A", fg="#D4AF37").pack(anchor="center")
        tk.Label(card, text="NEW YORK CITY  •  HIGH TABLE SANCTIONED", font=("Segoe UI", 8, "bold"), bg="#12141A", fg="#8C93A3").pack(anchor="center", pady=(2, 10))

        div = tk.Frame(card, bg="#D4AF37", height=1)
        div.pack(fill="x", pady=(0, 12))

        tk.Label(card, text="Good evening, Mr. Wick.", font=("Segoe UI", 12, "bold"), bg="#12141A", fg="#F2F4F8").pack(anchor="center")
        tk.Label(card, text="Membership status: Recognized  •  Concierge Services: Available", font=FONT_SM, bg="#12141A", fg="#4EBA6F").pack(anchor="center", pady=(3, 10))

        quote_box = tk.Frame(card, bg="#060709", padx=12, pady=8, highlightbackground="#2E3342", highlightthickness=1)
        quote_box.pack(fill="x", pady=(0, 14))
        tk.Label(quote_box, text='"Rules... without them, we live with the animals."', font=("Georgia", 10, "italic"), bg="#060709", fg="#D4AF37").pack(anchor="center")
        tk.Label(quote_box, text="— Winston Scott, Manager", font=("Segoe UI", 8), bg="#060709", fg="#8C93A3").pack(anchor="center", pady=(2, 0))

        btn = tk.Button(card, text="🪙 Enter The Continental", command=win.destroy,
                        bg="#D4AF37", fg="#0A0B0E", font=("Segoe UI", 10, "bold"),
                        relief="flat", padx=16, pady=5, activebackground="#E5B842", cursor="hand2")
        btn.pack(anchor="center")

    def _trigger_heimvis_easter_egg(self):
        """All-Seeing Eye & Heimvis / Jarvis AI Co-Pilot Easter Egg."""
        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
        self._log("=" * 75)
        self._log("👁️ ─────────────────────────────────────────────────────────────────────────")
        self._log("👁️⚡ [HEIMVIS / JARVIS ONLINE] ALL-SEEING SURVEILLANCE PROTOCOLS ENGAGED!")
        self._log("🛡️ Cross-marketplace synthetic radar scanning 150+ enterprise brand registries...")
        self._log("⚔️ 'We don't just enforce against infringement. We dismantle the entire machine.'")
        self._log("🏆 CO-CREATOR RECOGNITION: Jerry Seidenstucker & Heimvis AI Architecture!")
        self._log("👁️ ─────────────────────────────────────────────────────────────────────────")
        self._log("=" * 75)
        self._status("👁️⚡ HEIMVIS ONLINE: All-Seeing Brand Protection Protocols Engaged!")

    def _trigger_eleanor_easter_egg(self):
        """Playful 1967 Shelby GT500 Eleanor Go-Baby-Go easter egg."""
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

        # Reveal and switch to Eleanor theme
        if "eleanor" in THEMES:
            secret_name = THEMES["eleanor"]["name"]
            vals = list(self.theme_combo["values"])
            if secret_name not in vals:
                vals.append(secret_name)
                self.theme_combo["values"] = vals
            self.theme_var.set(secret_name)
            self._on_theme_changed()

        self._log("=" * 75)
        self._log("🐎 ─────────────────────────────────────────────────────────────────────────")
        self._log("🐎💨 [GO-BABY-GO!] 1967 SHELBY GT500 'ELEANOR' HAS ROARED TO LIFE!")
        self._log("🔥 427ci Big-Block Ford V8 + Nitrous Oxide System Engaged!")
        self._log("🌉 Flying over the Vincent Thomas Bridge at 160 MPH... Zero Counterfeits Survived!")
        self._log("🏆 ACHIEVEMENT UNLOCKED: Legendary 'Gone in 60 Seconds' Unicorn!")
        self._log("🐎 ─────────────────────────────────────────────────────────────────────────")
        self._log("=" * 75)
        self._status("🐎💨 GO-BABY-GO! 1967 Shelby GT500 Eleanor Nitrous Engaged!")

    def _trigger_konami_easter_egg(self):
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

        # Reveal and switch to secret Synthwave theme
        secret_name = THEMES["synthwave"]["name"]
        vals = list(self.theme_combo["values"])
        if secret_name not in vals:
            vals.append(secret_name)
            self.theme_combo["values"] = vals
        self.theme_var.set(secret_name)
        self._on_theme_changed()

        self._log("=" * 60)
        self._log("🎮 ★ ACHIEVEMENT UNLOCKED: THE KONAMI CODE ★ 🎮")
        self._log("✨ Supercharged Retro Synthwave 80s theme activated!")
        self._log("🚀 You have unlocked hidden developer superpowers!")
        self._log("=" * 60)
        messagebox.showinfo(
            "🎮 Konami Code Activated!",
            "★ ACHIEVEMENT UNLOCKED ★\n\n"
            "↑ ↑ ↓ ↓ ← → ← → B A\n\n"
            "🕹️ Retro Synthwave 80s theme activated!\n"
            "Happy brand hunting!"
        )

    def _trigger_rickroll_easter_egg(self):
        """Playful Rick Astley trademark guardian easter egg."""
        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
        self._log("=" * 70)
        self._log("🕺 ───────────────────────────────────────────────────────────────────")
        self._log("🎤 NEVER GONNA GIVE YOUR BRANDS UP!")
        self._log("🎤 NEVER GONNA LET INFRINGERS DOWN!")
        self._log("🎤 NEVER GONNA RUN AROUND AND DESERT YOUR IP! 🛡️✨")
        self._log("🏆 ACHIEVEMENT UNLOCKED: Legendary Rick Astley Brand Guardian!")
        self._log("🕺 ───────────────────────────────────────────────────────────────────")
        self._log("=" * 70)
        self._status("🕺 🎤 Never gonna give your brands up! (Achievement Unlocked)")

    def _on_run_btn_double_click(self, event=None):
        """Double-clicking Run button engages Nitro Boost flair."""
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass
        self._log("🏎️💨 [NITRO BOOST ENGAGED] Twin-turbochargers spooling to 9,500 RPM... Search velocity +200%!")
        self._status("🏎️💨 NITRO BOOST ENGAGED at 9,500 RPM!")

    def _on_title_click(self, event=None):
        """Clicking title bar triggers fun motivational enforcement badges and theme-specific quotes."""
        t_key = self.current_theme_key
        if t_key == "continental":
            quote = CONTINENTAL_QUOTES[self.quote_idx % len(CONTINENTAL_QUOTES)]
        elif t_key in THEME_QUOTES and (self.quote_idx % 2 == 1):
            quote = THEME_QUOTES[t_key]
        else:
            quote = QUOTES[self.quote_idx % len(QUOTES)]

        self.quote_idx += 1
        self._log(f"★ {quote}")
        self._status(quote)

    def _check_enforcement_milestones(self):
        """Check and log high-volume enterprise enforcement milestones."""
        total_res = len(self.results)
        milestones = [
            (50, "🎯 RECON SCOUT", "50 Suspicious Listings Identified!"),
            (100, "⚡ FIRST STRIKE", "100 Counterfeit Listings Harvested!"),
            (250, "🔍 IP SENTINEL", "250 Infringing Products Logged and Cataloged!"),
            (500, "🛡️ ENFORCEMENT BATTALION", "500 Counterfeits Seized across Store Fronts!"),
            (1000, "⚔️ BRAND DEFENDER", "1,000 Infringements Purged from the Marketplace!"),
            (2000, "🏆 ELITE BRAND ENFORCER", "2,000 Counterfeits Logged! (Monthly Target Reached!)"),
            (5000, "🚀 FLEET COMMANDER", "5,000 Counterfeit Assets Harvested! Master Enforcer!"),
            (10000, "👑 TITAN OF INDUSTRY", "10,000 Infringements Seized! Supreme Anti-Counterfeit Authority!"),
        ]
        if not hasattr(self, "achieved_milestones"):
            self.achieved_milestones = set()

        for threshold, badge, desc in milestones:
            if total_res >= threshold and threshold not in self.achieved_milestones:
                self.achieved_milestones.add(threshold)
                self._log("=" * 75)
                self._log(f"★ ─────────────────────────────────────────────────────────────────────────")
                self._log(f"★ 🏆 MILESTONE ACHIEVED: {badge} ({threshold:,} Listings) ★")
                self._log(f"★ {desc}")
                self._log(f"★ ─────────────────────────────────────────────────────────────────────────")
                self._log("=" * 75)
                self._status(f"🏆 MILESTONE: {badge} ({threshold:,} Listings)")

    # ══════════════════════════════════════════════════════════════════════════
    #  EXPORT
    # ══════════════════════════════════════════════════════════════════════════
    def _export(self):
        if not self.results:
            messagebox.showinfo("Export", "No results to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile=f"enforcement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        if path:
            try:
                self.exporter.export(self.results, path)
                # Ingest verified exported results into Enterprise Brand Enforcement Registry
                seller_items = {}
                for item in self.results:
                    seller = item.get("seller") or "Unknown"
                    seller_items.setdefault(seller, []).append(item)
                for seller, s_items in seller_items.items():
                    self.data_store.record_enforcement_scan(seller, s_items)
                self._log(f"Exported {len(self.results)} rows → {path}")
                self._log(f"🛡️ Logged {len(self.results)} verified listing(s) across {len(seller_items)} seller(s) into Enterprise Brand Enforcement Registry.")
                messagebox.showinfo("Exported", f"Saved {len(self.results)} verified listings to:\n{path}\n\n🛡️ Logged into Enterprise Brand Enforcement Registry.")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def _export_job_log(self):
        """Export comprehensive Job Audit Log & Summary Report."""
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Log / Text file", "*.txt"), ("Log file", "*.log"), ("All files", "*.*")],
            initialfile=f"job_audit_log_{now_str}.txt"
        )
        if not path:
            return

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append(" EBAY ENFORCEMENT HARVESTER - JOB AUDIT REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Export Date/Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Active Theme     : {self.theme['name']}")
        report_lines.append(f"Session Mode     : {'eBay Browse API' if self.use_api.get() else 'Browser Automation (Edge Stealth)'}")
        report_lines.append(f"Total Unique Listings Harvested : {len(self.results)}")
        report_lines.append("")

        report_lines.append("-" * 80)
        report_lines.append(" EXECUTED SEARCH JOBS BREAKDOWN")
        report_lines.append("-" * 80)

        if not self.executed_jobs:
            report_lines.append("  (No queued jobs were executed during this session)")
        else:
            for idx, job in enumerate(self.executed_jobs, 1):
                report_lines.append(f"[Job #{idx}] Target Brand: {job.get('brand', 'Unknown')}")
                report_lines.append(f"  • Execution Time    : {job.get('timestamp', '')}")
                report_lines.append(f"  • Target Store      : {job.get('store', '')}")
                report_lines.append(f"  • Resolved Seller   : {job.get('resolved_seller', job.get('store', ''))}")
                report_lines.append(f"  • Condition Filter  : {job.get('condition', 'all')}")
                report_lines.append(f"  • Listings Harvested: {job.get('total_harvested', 0)}")
                
                report_lines.append("  • Keywords Searched :")
                for term in job.get("includes", []):
                    cnt = job.get("term_counts", {}).get(term, "N/A")
                    report_lines.append(f"      - '{term}': {cnt} listings found")

                excludes = job.get("excludes", [])
                report_lines.append(f"  • Applied Exclusions ({len(excludes)} terms):")
                if excludes:
                    report_lines.append(f"      {', '.join(excludes)}")
                else:
                    report_lines.append("      (None)")
                report_lines.append("")

        report_lines.append("-" * 80)
        report_lines.append(" RAW ACTIVITY & CONSOLE LOG")
        report_lines.append("-" * 80)
        raw_log = self.log_text.get("1.0", "end").strip()
        report_lines.append(raw_log if raw_log else "(No activity log entries recorded)")
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append(" END OF AUDIT REPORT")
        report_lines.append("=" * 80)

        content = "\n".join(report_lines)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._log(f"Job audit log exported → {path}")
            messagebox.showinfo("Log Exported", f"Job Audit Log successfully saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export log: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  BROWSER & API SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    def _toggle_headless(self):
        is_headless = self.headless_var.get()
        self.scraper.headless = is_headless
        self.aliexpress_scraper.headless = is_headless
        self.wish_scraper.headless = is_headless
        self.temu_scraper.headless = is_headless
        self.mercadolibre_scraper.headless = is_headless
        self.redbubble_scraper.headless = is_headless
        self.printerval_scraper.headless = is_headless
        self.data_store.set_setting("headless", is_headless)
        self._log(f"Browser search mode: {'👻 Silent Background' if is_headless else '🖥 Visible Browser Window'}")

    def _toggle_api(self):
        if self.use_api.get():
            self.app_id_lbl.pack(side="left", padx=(3, 1), after=self.api_cb)
            self.app_id_entry.pack(side="left", after=self.app_id_lbl)
            self.cert_id_lbl.pack(side="left", padx=(3, 1), after=self.app_id_entry)
            self.cert_id_entry.pack(side="left", after=self.cert_id_lbl)
            self.save_keys_btn.pack(side="left", padx=2, after=self.cert_id_entry)
            self.app_id_entry.config(state="normal")
            self.cert_id_entry.config(state="normal")
        else:
            self.app_id_lbl.pack_forget()
            self.app_id_entry.pack_forget()
            self.cert_id_lbl.pack_forget()
            self.cert_id_entry.pack_forget()
            self.save_keys_btn.pack_forget()

    def _save_api_keys(self):
        self.data_store.set_setting("use_api", self.use_api.get())
        self.data_store.set_setting("api_app_id", self.api_app_id_var.get().strip())
        self.data_store.set_setting("api_cert_id", self.api_cert_id_var.get().strip())
        self._log("eBay API settings saved.")
        messagebox.showinfo("Saved", "API settings saved.")

    def _launch_meli_login(self):
        """Open a visible browser window to log in to Mercado Libre and permanently preserve session cookies."""
        self._log("🔑 Opening Mercado Libre authentication window in Microsoft Edge. Please log in or create an account—your authenticated session will be saved permanently!")
        self.mercadolibre_scraper.launch_interactive_auth()
        messagebox.showinfo("Mercado Libre Login", "A browser window is opening to Mercado Libre.\n\nPlease log in or create an account (you only need to do this once!).\n\nYour session cookies will be permanently stored for all future automated searches.")

    # ══════════════════════════════════════════════════════════════════════════
    #  ADHOC BATCH URL & EXCEL LISTING IMPORTER
    # ══════════════════════════════════════════════════════════════════════════
    def _open_adhoc_importer_window(self):
        """Open the Adhoc Batch URL & Excel Listing Importer dialog."""
        if self._win_importer and self._win_importer.winfo_exists():
            self._win_importer.lift()
            self._win_importer.focus_force()
            return

        t = self.theme
        win = tk.Toplevel(self)
        self._win_importer = win
        win.title("📥 Adhoc Batch URL & Excel Listing Importer — Multi-Marketplace Harvester")
        win.configure(bg=t["bg"])
        self._apply_dark_titlebar(win)

        # Center relative to main window
        win.update_idletasks()
        p_x = self.winfo_rootx()
        p_y = self.winfo_rooty()
        p_w = self.winfo_width()
        p_h = self.winfo_height()
        w, h = 1040, 720
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        pad_f = tk.Frame(win, bg=t["bg"], padx=14, pady=12)
        pad_f.pack(fill="both", expand=True)

        # ── Header Banner ────────────────────────────────────────────────────
        head_f = tk.Frame(pad_f, bg=t["bg"])
        head_f.pack(fill="x", pady=(0, 8))

        tk.Label(head_f, text="📥 Adhoc Batch URL & Excel Listing Importer",
                 font=("Segoe UI", 13, "bold"), bg=t["bg"], fg=t["accent"]).pack(side="left")

        tk.Label(head_f, text="Instant Deep Metadata Scraping for Client Request Lists (eBay, Ali, Wish, Temu, MeLi)",
                 font=FONT_SM, bg=t["bg"], fg=t["subtext"]).pack(side="left", padx=12, pady=(2, 0))

        # ── Top KPI Stat Badges ──────────────────────────────────────────────
        kpi_f = tk.Frame(pad_f, bg=t["panel"], padx=12, pady=8)
        kpi_f.pack(fill="x", pady=(0, 8))

        kpi_labels = {}
        def _kpi(parent, title, val, key, color=None):
            f = tk.Frame(parent, bg=t["panel"], padx=12)
            f.pack(side="left", fill="y")
            tk.Label(f, text=title, font=("Segoe UI", 8, "bold"), bg=t["panel"], fg=t["subtext"]).pack(anchor="w")
            lbl = tk.Label(f, text=val, font=("Segoe UI", 12, "bold"), bg=t["panel"], fg=color or t["text"])
            lbl.pack(anchor="w")
            kpi_labels[key] = lbl

        _kpi(kpi_f, "📋 URLs in Batch", "0", "total")
        _kpi(kpi_f, "🌐 Marketplaces Detected", "None", "mkts", color=t["accent2"])
        _kpi(kpi_f, "✅ Successfully Scraped", "0", "success", color=t["success"])
        _kpi(kpi_f, "💰 Total Value Captured", "$0.00", "val", color=t["warning"])

        # ── Input Section: Paste Box + File Loader ───────────────────────────
        input_head = tk.Frame(pad_f, bg=t["bg"])
        input_head.pack(fill="x", pady=(4, 2))

        tk.Label(input_head, text="📋 Target Listing URLs (Paste raw URLs or upload spreadsheet):",
                 font=FONT_HEAD, bg=t["bg"], fg=t["accent"]).pack(side="left")

        url_count_lbl = tk.Label(input_head, text="0 URLs detected", font=FONT_SM, bg=t["bg"], fg=t["subtext"])
        url_count_lbl.pack(side="right")

        text_frame = tk.Frame(pad_f, bg=t["entry_bg"], highlightthickness=1, highlightbackground=t["border"])
        text_frame.pack(fill="both", expand=True, pady=(2, 6))

        url_text = tk.Text(text_frame, height=9, bg=t["entry_bg"], fg=t["text"],
                           insertbackground=t["text"], relief="flat", font=("Consolas", 10),
                           wrap="none")
        text_vsb = ttk.Scrollbar(text_frame, orient="vertical", command=url_text.yview)
        text_hsb = ttk.Scrollbar(text_frame, orient="horizontal", command=url_text.xview)
        url_text.configure(yscrollcommand=text_vsb.set, xscrollcommand=text_hsb.set)

        url_text.pack(side="left", fill="both", expand=True)
        text_vsb.pack(side="right", fill="y")
        text_hsb.pack(side="bottom", fill="x")

        placeholder_txt = "# Paste listing URLs below (one per line, comma-separated, or mixed text):\nhttps://www.ebay.com/itm/123456789012\nhttps://www.aliexpress.us/item/3256809669065606.html\nhttps://www.wish.com/product/5e6b7c8d9a0b1c2d3e4f5a6b\nhttps://www.temu.com/goods.html?goods_id=601099512345\nhttps://articulo.mercadolibre.com.mx/MLM-1234567890-example"
        url_text.insert("1.0", placeholder_txt)
        url_text.config(fg=t["subtext"])

        def _clear_ph(e):
            if url_text.get("1.0", "end").strip() == placeholder_txt.strip():
                url_text.delete("1.0", "end")
                url_text.config(fg=t["text"])

        url_text.bind("<FocusIn>", _clear_ph)

        def _update_url_counter(e=None):
            raw = url_text.get("1.0", "end").strip()
            if raw == placeholder_txt.strip():
                url_count_lbl.config(text="0 URLs detected")
                kpi_labels["total"].config(text="0")
                kpi_labels["mkts"].config(text="None")
                return []
            urls = batch_importer.extract_urls_from_text(raw)
            url_count_lbl.config(text=f"{len(urls)} URLs detected")
            kpi_labels["total"].config(text=f"{len(urls):,}")

            mkts = set(batch_importer.detect_platform(u) for u in urls)
            if mkts:
                kpi_labels["mkts"].config(text=", ".join(sorted(mkts)))
            else:
                kpi_labels["mkts"].config(text="None")
            return urls

        url_text.bind("<KeyRelease>", _update_url_counter)

        # ── Toolbar: File Importer & Actions ──────────────────────────────────
        action_bar = tk.Frame(pad_f, bg=t["bg"])
        action_bar.pack(fill="x", pady=(0, 6))

        loaded_structured_items = []

        def _load_file():
            nonlocal loaded_structured_items
            path = filedialog.askopenfilename(
                title="Select Spreadsheet or URL List File",
                filetypes=[
                    ("Spreadsheet / URL List", "*.xlsx;*.xls;*.csv;*.txt"),
                    ("Excel Workbook (*.xlsx)", "*.xlsx"),
                    ("Excel 97-2003 (*.xls)", "*.xls"),
                    ("CSV File (*.csv)", "*.csv"),
                    ("Text File (*.txt)", "*.txt"),
                    ("All Files (*.*)", "*.*")
                ],
                parent=win
            )
            if not path:
                return
            
            override_brand = brand_var.get().strip()
            items, urls = batch_importer.extract_structured_listings_from_file(path, default_brand=override_brand)
            if not urls and not items:
                messagebox.showwarning("No Listings Found", f"No valid listing records or URLs were found in:\n{path}", parent=win)
                return

            loaded_structured_items = items
            url_text.delete("1.0", "end")
            url_text.insert("1.0", "\n".join(urls) + "\n")
            url_text.config(fg=t["text"])
            _update_url_counter()

            if items:
                status_lbl.config(
                    text=f"⚡ {len(items)} structured listings loaded from '{os.path.basename(path)}' (Title, Seller, Price, Photos ready)!",
                    fg=t["success"]
                )
                self._log(f"📥 Loaded {len(items)} structured listings from {os.path.basename(path)}")
                instant_import_btn.config(state="normal")
            else:
                status_lbl.config(text=f"Loaded {len(urls)} plain URL(s) from '{os.path.basename(path)}'. Ready to harvest.", fg=t["text"])
                self._log(f"📥 Loaded {len(urls)} listing URL(s) from {os.path.basename(path)}")

        def _paste_clipboard():
            nonlocal loaded_structured_items
            try:
                clip = win.clipboard_get()
                if clip:
                    curr = url_text.get("1.0", "end").strip()
                    if not curr or curr == placeholder_txt.strip():
                        url_text.delete("1.0", "end")
                        url_text.insert("1.0", clip.strip() + "\n")
                    else:
                        url_text.insert("end", "\n" + clip.strip() + "\n")
                    url_text.config(fg=t["text"])
                    _update_url_counter()
            except Exception:
                pass

        def _clear_urls():
            nonlocal loaded_structured_items
            loaded_structured_items = []
            url_text.delete("1.0", "end")
            url_text.config(fg=t["text"])
            _update_url_counter()
            status_lbl.config(text="Ready to harvest batch URLs.", fg=t["text"])

        self._btn(action_bar, "📂 Load Excel / CSV / TXT", _load_file).pack(side="left", padx=(0, 6))
        self._btn(action_bar, "📋 Paste Clipboard", _paste_clipboard).pack(side="left", padx=(0, 6))
        self._btn(action_bar, "🧹 Clear URLs", _clear_urls).pack(side="left", padx=(0, 6))

        tk.Label(action_bar, text="🏷️ Brand Tag:", font=FONT_SM, bg=t["bg"], fg=t["accent"]).pack(side="left", padx=(14, 4))
        brand_var = tk.StringVar(value="⚡ Auto-Detect from Title")
        all_library_brands = sorted(list(self.data_store.get_brands().keys())) if hasattr(self, "data_store") else []
        brand_choices = ["⚡ Auto-Detect from Title"] + all_library_brands
        brand_combo = ttk.Combobox(action_bar, textvariable=brand_var, values=brand_choices, width=22, state="readonly", font=FONT_SM)
        brand_combo.pack(side="left", padx=(0, 6))

        exec_frame = tk.Frame(pad_f, bg=t["panel"], padx=10, pady=8)
        exec_frame.pack(fill="x", pady=(4, 6))

        batch_running = [False]
        batch_stop = threading.Event()
        batch_pause = threading.Event()
        batch_pause.set()

        progress_var = tk.DoubleVar(value=0.0)
        p_bar = ttk.Progressbar(exec_frame, variable=progress_var, maximum=100)
        p_bar.pack(fill="x", pady=(0, 6))

        status_lbl = tk.Label(exec_frame, text="Ready to harvest batch URLs.", font=FONT_SM, bg=t["panel"], fg=t["text"])
        status_lbl.pack(side="left")

        run_btn = None
        stop_btn = None
        instant_import_btn = None

        def _direct_instant_import():
            nonlocal loaded_structured_items
            override_brand = brand_var.get().strip()
            
            # If structured items are cached from the loaded file, use them directly
            items_to_add = list(loaded_structured_items)
            
            # If user pasted raw URLs or edited the text box without a structured file, build instant baseline records
            if not items_to_add:
                raw_urls = _update_url_counter()
                if not raw_urls:
                    messagebox.showwarning("No Listings", "Please paste listing URLs or load a spreadsheet first.", parent=win)
                    return
                for u in raw_urls:
                    m_id = re.search(r'/itm/(?:[^/]+/)?(\d{10,14})', u) or re.search(r'(\d{10,14})', u)
                    item_id = m_id.group(1) if m_id else ""
                    mkt = batch_importer.detect_platform(u)
                    items_to_add.append({
                        "title": f"Imported Listing #{item_id}" if item_id else "Imported Web Listing",
                        "item_id": item_id,
                        "url": u,
                        "price": "$0.00",
                        "seller": "Unknown",
                        "location": "United States",
                        "image_url": "",
                        "marketplace": mkt,
                        "brand": override_brand if override_brand not in ("⚡ Auto-Detect from Title", "Auto-Detect", "") else "Automotive & Consumer Brands",
                        "product_type": "Accessories"
                    })

            if not items_to_add:
                return

            added_count = 0
            total_val = 0.0
            newly_added = []

            for item in items_to_add:
                # Apply brand override if selected by analyst
                if override_brand and override_brand not in ("⚡ Auto-Detect from Title", "Auto-Detect", ""):
                    item["brand"] = override_brand

                iid = item.get("item_id")
                dedup_key = iid if iid else item.get("url")
                if dedup_key and dedup_key not in self.seen_item_ids:
                    self.seen_item_ids.add(dedup_key)
                    self.results.append(item)
                    newly_added.append(item)
                    added_count += 1

                    # Extract numeric value
                    p_str = item.get("price", "")
                    m_p = re.search(r"[\d,]+(?:\.\d+)?", p_str)
                    if m_p:
                        try: total_val += float(m_p.group(0).replace(",", ""))
                        except ValueError: pass
                elif not dedup_key:
                    self.results.append(item)
                    newly_added.append(item)
                    added_count += 1

            if newly_added:
                self._update_results_table(newly_added)
                self._status(f"⚡ Instantly imported {added_count} listings from spreadsheet to Results table.")
                self._log(f"⚡ Instant Import: Added {added_count} pre-populated listings to Results table (Value: ${total_val:,.2f}).")
                kpi_labels["success"].config(text=f"{added_count:,}")
                kpi_labels["val"].config(text=f"${total_val:,.2f}")
                status_lbl.config(text=f"⚡ Successfully imported {added_count} listings in 0.05s!", fg=t["success"])
                progress_var.set(100)

                # Sound alert if enabled
                if self.sound_enabled_var.get():
                    try: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                    except Exception: pass

                # Prompt user for Multi-Locale Expander
                msg = f"⚡ Successfully loaded {added_count} listings directly into your Results table!\n\nAll photos, sellers, prices, and IDs have been preserved.\n\nWould you like to open the Global Multi-Locale Expander now to project these across international marketplaces?"
                if messagebox.askyesno("Instant Import Complete", msg, parent=win):
                    win.destroy()
                    self._open_multi_locale_expander()
            else:
                messagebox.showinfo("Import Info", f"All {len(items_to_add)} listings are already present in your Results table (duplicates skipped).", parent=win)

        def _start_harvest():
            nonlocal loaded_structured_items
            urls = _update_url_counter()
            if not urls:
                messagebox.showwarning("No URLs", "Please paste one or more listing URLs or load a spreadsheet first.", parent=win)
                return

            if batch_running[0]:
                return

            batch_running[0] = True
            batch_stop.clear()
            batch_pause.set()

            run_btn.config(state="disabled")
            instant_import_btn.config(state="disabled")
            stop_btn.config(state="normal")

            override_brand = brand_var.get().strip()
            is_headless = self.headless_var.get()

            # Build fast lookup map from loaded structured items
            structured_by_url = {it.get("url", ""): it for it in loaded_structured_items if it.get("url")}
            structured_by_id = {str(it.get("item_id", "")): it for it in loaded_structured_items if it.get("item_id")}

            def _worker():
                scraped_count = 0
                total_val = 0.0
                total_urls = len(urls)

                self._log(f"🚀 Starting Adhoc Batch Harvest of {total_urls} URLs...")

                for idx, u in enumerate(urls):
                    if batch_stop.is_set():
                        break

                    batch_pause.wait()

                    pct = int(((idx + 1) / total_urls) * 100)
                    mkt = batch_importer.detect_platform(u)
                    
                    def _ui_prog(_idx=idx, _mkt=mkt, _pct=pct):
                        status_lbl.config(text=f"[{_idx+1}/{total_urls}] Harvesting {_mkt} listing...", fg=t["text"])
                        progress_var.set(_pct)
                    win.after(0, _ui_prog)

                    try:
                        # Check if we already have complete structured data from file
                        cached_item = structured_by_url.get(u)
                        if not cached_item:
                            m_id = re.search(r'/itm/(?:[^/]+/)?(\d{10,14})', u) or re.search(r'(\d{10,14})', u)
                            if m_id:
                                cached_item = structured_by_id.get(m_id.group(1))

                        # If cached item has valid title and seller, use it without re-fetching
                        if cached_item and cached_item.get("title") and cached_item.get("seller") not in ("Unknown", "eBay Seller", ""):
                            item = dict(cached_item)
                        else:
                            item = batch_importer.fetch_single_listing(u, default_brand=override_brand, headless=is_headless)

                        if item:
                            if override_brand and override_brand not in ("⚡ Auto-Detect from Title", "Auto-Detect", ""):
                                item["brand"] = override_brand

                            iid = item.get("item_id")
                            dedup_key = iid if iid else item.get("url")
                            if dedup_key and dedup_key not in self.seen_item_ids:
                                self.seen_item_ids.add(dedup_key)
                                self.results.append(item)
                                scraped_count += 1

                                # Extract numeric value
                                p_str = item.get("price", "")
                                m_p = re.search(r"[\d,]+(?:\.\d+)?", p_str)
                                if m_p:
                                    try: total_val += float(m_p.group(0).replace(",", ""))
                                    except ValueError: pass

                                def _ui_add(_item=item, _cnt=scraped_count, _val=total_val):
                                    self._update_results_table([_item])
                                    kpi_labels["success"].config(text=f"{_cnt:,}")
                                    kpi_labels["val"].config(text=f"${_val:,.2f}")
                                win.after(0, _ui_add)
                                self._log(f"  ✓ [{mkt}] Harvested: '{item.get('title')[:55]}...' ({item.get('price')})")
                            elif not dedup_key:
                                self.results.append(item)
                                scraped_count += 1
                                def _ui_add2(_item=item, _cnt=scraped_count):
                                    self._update_results_table([_item])
                                    kpi_labels["success"].config(text=f"{_cnt:,}")
                                win.after(0, _ui_add2)
                            else:
                                self._log(f"  ℹ [{mkt}] Skipped duplicate Item ID: {iid}")
                    except Exception as e:
                        self._log(f"  ❌ Error on {u}: {e}", error=True)

                    time.sleep(0.1)

                def _ui_done(_scraped=scraped_count, _tot=total_urls):
                    batch_running[0] = False
                    run_btn.config(state="normal")
                    instant_import_btn.config(state="normal")
                    stop_btn.config(state="disabled")
                    status_lbl.config(text=f"Completed! Harvested {_scraped}/{_tot} listings.", fg=t["success"])
                    progress_var.set(100)

                    # Sound alert if enabled
                    if self.sound_enabled_var.get():
                        try: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                        except Exception: pass

                    self._log(f"🏁 Adhoc Batch Import Complete: Added {_scraped} listings to results table.")
                    messagebox.showinfo("Batch Harvest Complete",
                                        f"Harvest Complete!\n\nSuccessfully processed {_scraped} of {_tot} listings.\n\nAll listings have been added to your Main Results Table, Threat Intelligence Hub, and Excel export.",
                                        parent=win)

                win.after(0, _ui_done)

            t_thread = threading.Thread(target=_worker, daemon=True)
            t_thread.start()

        def _stop_harvest():
            if batch_running[0]:
                batch_stop.set()
                status_lbl.config(text="Stopping batch harvest...")
                stop_btn.config(state="disabled")

        stop_btn = self._btn(exec_frame, "⏹ Stop", _stop_harvest, danger=True)
        stop_btn.pack(side="right", padx=(4, 0))
        stop_btn.config(state="disabled")

        run_btn = self._btn(exec_frame, "🌐 Scrape Web", _start_harvest)
        run_btn.pack(side="right", padx=(4, 0))

        instant_import_btn = self._btn(exec_frame, "⚡ Instant Load to Results (0s)", _direct_instant_import, accent=True)
        instant_import_btn.pack(side="right", padx=(4, 0))

    _open_batch_import_dialog = _open_adhoc_importer_window

    # ══════════════════════════════════════════════════════════════════════════
    #  ENTERPRISE BRAND ENFORCEMENT & RECIDIVISM REGISTRY
    # ══════════════════════════════════════════════════════════════════════════
    def _open_enforcement_registry_window(self):
        """Open the executive Enterprise Brand Enforcement & Recidivism Registry dialog."""
        if self._win_registry and self._win_registry.winfo_exists():
            self._win_registry.lift()
            self._win_registry.focus_force()
            return

        t = self.theme
        win = tk.Toplevel(self)
        self._win_registry = win
        win.title("🛡️ Enterprise Brand Enforcement & Recidivism Registry")
        win.configure(bg=t["bg"])
        win.geometry("1180x680")
        win.minsize(980, 580)
        self._apply_dark_titlebar(win)

        # Center relative to main window
        win.update_idletasks()
        p_x = self.winfo_rootx()
        p_y = self.winfo_rooty()
        p_w = self.winfo_width()
        p_h = self.winfo_height()
        w, h = 1180, 680
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        pad_f = tk.Frame(win, bg=t["bg"], padx=14, pady=12)
        pad_f.pack(fill="both", expand=True)

        # ── Header Banner ────────────────────────────────────────────────────
        head_f = tk.Frame(pad_f, bg=t["bg"])
        head_f.pack(fill="x", pady=(0, 8))

        tk.Label(head_f, text="🛡️ Enterprise Brand Enforcement & Recidivism Registry",
                 font=("Segoe UI", 13, "bold"), bg=t["bg"], fg=t["accent"]).pack(side="left")

        tk.Label(head_f, text="Cross-Brand Infringement Tracking & Repeat Offender Intelligence",
                 font=FONT_SM, bg=t["bg"], fg=t["subtext"]).pack(side="left", padx=12, pady=(2, 0))

        # ── Top KPI Stat Badges ──────────────────────────────────────────────
        kpi_f = tk.Frame(pad_f, bg=t["panel"], padx=12, pady=8)
        kpi_f.pack(fill="x", pady=(0, 8))

        kpi_labels = {}
        def _kpi(parent, title, val, key, color=None):
            f = tk.Frame(parent, bg=t["panel"], padx=12)
            f.pack(side="left", fill="y")
            tk.Label(f, text=title, font=("Segoe UI", 8, "bold"), bg=t["panel"], fg=t["subtext"]).pack(anchor="w")
            lbl = tk.Label(f, text=val, font=("Segoe UI", 12, "bold"), bg=t["panel"], fg=color or t["text"])
            lbl.pack(anchor="w")
            kpi_labels[key] = lbl

        _kpi(kpi_f, "🏬 Stores Harvested", "0", "stores")
        _kpi(kpi_f, "🚨 Repeat Offender Stores", "0", "repeat", color=t["danger"])
        _kpi(kpi_f, "📦 Infringing Listings Captured", "0", "items", color=t["accent"])
        _kpi(kpi_f, "💰 Total Counterfeit Market Value", "$0.00", "val", color=t["success"])

        def _refresh_kpis():
            reg_data = self.data_store.get_enforcement_registry()
            total_stores = len(reg_data)
            repeat_offenders = sum(1 for d in reg_data.values() if d.get("scan_count", 1) > 1 or d.get("total_listings", 0) > 10)
            total_infringing_items = sum(d.get("total_listings", len(d.get("items", []))) for d in reg_data.values())
            total_infringing_val = sum(d.get("total_value", 0.0) for d in reg_data.values())

            if "stores" in kpi_labels: kpi_labels["stores"].config(text=f"{total_stores:,}")
            if "repeat" in kpi_labels: kpi_labels["repeat"].config(text=f"{repeat_offenders:,}")
            if "items" in kpi_labels: kpi_labels["items"].config(text=f"{total_infringing_items:,}")
            if "val" in kpi_labels: kpi_labels["val"].config(text=f"${total_infringing_val:,.2f}")

        _refresh_kpis()

        # ── Filter & Search Toolbar ──────────────────────────────────────────
        filter_toolbar = tk.Frame(pad_f, bg=t["bg"])
        filter_toolbar.pack(fill="x", pady=(0, 6))

        tk.Label(filter_toolbar, text="🔍 Filter:", font=FONT_SM, bg=t["bg"], fg=t["accent"]).pack(side="left", padx=(0, 4))
        
        reg_col_var = tk.StringVar(value="All Columns")
        reg_cols = ["All Columns", "Store / Seller", "Status", "Brands", "Product Types", "Locations", "Est. Value"]
        reg_col_combo = ttk.Combobox(filter_toolbar, textvariable=reg_col_var,
                                     values=reg_cols, width=13, state="readonly", font=FONT_SM)
        reg_col_combo.pack(side="left", padx=(0, 6))

        reg_filter_var = tk.StringVar()
        reg_filter_entry = tk.Entry(filter_toolbar, textvariable=reg_filter_var, width=20,
                                    bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                    relief="flat", font=FONT_SM)
        reg_filter_entry.pack(side="left", padx=(0, 6))

        offense_filter_var = tk.StringVar(value="All Stores")
        offense_combo = ttk.Combobox(filter_toolbar, textvariable=offense_filter_var,
                                     values=["All Stores", "🚨 Repeat Offenders Only", "⚠️ First Strike Only"],
                                     state="readonly", width=20, font=FONT_SM)
        offense_combo.pack(side="left", padx=(0, 6))

        def _clear_reg_filter():
            reg_filter_var.set("")
            offense_filter_var.set("All Stores")
            reg_col_var.set("All Columns")

        def _select_all_reg_visible():
            ch = tree.get_children()
            if ch:
                tree.selection_set(ch)

        self._btn(filter_toolbar, "✕ Clear", _clear_reg_filter).pack(side="left", padx=(0, 4))
        self._btn(filter_toolbar, "✓ Select All Visible", _select_all_reg_visible).pack(side="left", padx=(0, 4))

        # ── Treeview Table ───────────────────────────────────────────────────
        tree_frame = tk.Frame(pad_f, bg=t["bg"])
        tree_frame.pack(fill="both", expand=True)

        cols = ("seller", "status", "brands", "product_types", "listings", "total_val", "locations", "first_seen", "last_scanned", "scans")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="extended")
        
        col_headers = {
            "seller": "Store / Seller Name",
            "status": "Offense Status",
            "brands": "Brands Infringed",
            "product_types": "Product Types",
            "listings": "Listings",
            "total_val": "Est. Market Value ($)",
            "locations": "Locations",
            "first_seen": "First Detected",
            "last_scanned": "Last Scanned",
            "scans": "Scans"
        }
        col_w = {
            "seller": 140,
            "status": 120,
            "brands": 150,
            "product_types": 140,
            "listings": 65,
            "total_val": 120,
            "locations": 120,
            "first_seen": 110,
            "last_scanned": 110,
            "scans": 50
        }
        for c in cols:
            tree.heading(c, text=col_headers[c])
            tree.column(c, width=col_w[c], minwidth=40)

        self._style_tree(tree)
        tree.tag_configure("repeat", foreground=t["danger"])
        tree.tag_configure("normal", foreground=t["text"])

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        def _matches_reg_query(seller, status, brands_str, pts_str, locs_str, total_val_str, query_str, col_target):
            if not query_str:
                return True
            
            c_key = col_target.lower().strip()
            if "seller" in c_key or "store" in c_key:
                target_text = seller
            elif "status" in c_key:
                target_text = status
            elif "brand" in c_key:
                target_text = brands_str
            elif "product" in c_key:
                target_text = pts_str
            elif "loc" in c_key:
                target_text = locs_str
            elif "val" in c_key or "price" in c_key:
                target_text = total_val_str
            else:
                target_text = f"{seller} {status} {brands_str} {pts_str} {locs_str} {total_val_str}"

            target_lower = target_text.lower()

            import shlex
            try:
                raw_tokens = shlex.split(query_str)
            except Exception:
                raw_tokens = query_str.split()

            positive_tokens = []
            negative_tokens = []

            for tok in raw_tokens:
                tok = tok.strip()
                if not tok:
                    continue
                if tok.startswith("-") and len(tok) > 1:
                    negative_tokens.append(tok[1:].lower())
                elif tok.startswith("+") and len(tok) > 1:
                    positive_tokens.append(tok[1:].lower())
                else:
                    positive_tokens.append(tok.lower())

            for neg in negative_tokens:
                if neg in target_lower:
                    return False

            for pos in positive_tokens:
                if pos not in target_lower:
                    return False

            return True

        def _populate_tree():
            tree.delete(*tree.get_children())
            q = reg_filter_var.get().strip()
            c_target = reg_col_var.get()
            off_f = offense_filter_var.get()
            cur_reg = self.data_store.get_enforcement_registry()

            for seller, data in sorted(cur_reg.items(), key=lambda x: x[1].get("total_value", 0.0), reverse=True):
                scans = data.get("scan_count", 1)
                is_repeat = scans > 1 or data.get("total_listings", 0) > 10
                status = "🚨 REPEAT OFFENDER" if is_repeat else "⚠️ FIRST STRIKE"

                if off_f == "🚨 Repeat Offenders Only" and not is_repeat:
                    continue
                if off_f == "⚠️ First Strike Only" and is_repeat:
                    continue

                brands_str = ", ".join(data.get("brands", []))
                pts_str = ", ".join(data.get("product_types", []))
                locs_str = ", ".join(data.get("locations", []))
                val_str = f"${data.get('total_value', 0.0):,.2f}"

                if q and not _matches_reg_query(seller, status, brands_str, pts_str, locs_str, val_str, q, c_target):
                    continue

                tree.insert("", "end", iid=seller, values=(
                    seller,
                    status,
                    brands_str,
                    pts_str,
                    data.get("total_listings", len(data.get("items", []))),
                    val_str,
                    locs_str,
                    data.get("first_seen", ""),
                    data.get("last_scanned", ""),
                    scans
                ), tags=("repeat" if is_repeat else "normal",))

        reg_filter_var.trace_add("write", lambda *a: _populate_tree())
        reg_col_combo.bind("<<ComboboxSelected>>", lambda e: _populate_tree())
        offense_combo.bind("<<ComboboxSelected>>", lambda e: _populate_tree())
        _populate_tree()

        # ── Bottom Action Toolbar ────────────────────────────────────────────
        btn_row = tk.Frame(pad_f, bg=t["bg"])
        btn_row.pack(fill="x", pady=(10, 0))

        def _export_dossier():
            cur_reg = self.data_store.get_enforcement_registry()
            if not cur_reg:
                messagebox.showinfo("Empty Registry", "No store enforcement records to export.", parent=win)
                return
            now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                initialfile=f"A2C2_Store_Recidivism_Dossier_{now_str}.xlsx",
                parent=win
            )
            if path:
                try:
                    self.exporter.export_a2c2_dossier(cur_reg, path)
                    self._log(f"📄 A2C2 Master Store Dossier exported → {path}")
                    messagebox.showinfo("Dossier Exported", f"Successfully exported A2C2 Store Recidivism Dossier to:\n{path}", parent=win)
                except Exception as ex:
                    messagebox.showerror("Export Error", str(ex), parent=win)

        def _inspect_selected_seller():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Select Store", "Select a store in the registry table first.", parent=win)
                return
            seller_key = sel[0]
            cur_reg = self.data_store.get_enforcement_registry()
            if seller_key in cur_reg:
                self._open_seller_items_inspector(seller_key, cur_reg[seller_key])

        def _queue_reenforcement_sweep():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Select Store", "Select a store to re-enforce.", parent=win)
                return
            seller_key = sel[0]
            self.store_text.delete("1.0", "end")
            self.store_text.insert("1.0", seller_key)
            self.store_text.config(fg=t["text"])
            self._queue_portfolio_preset()
            win.destroy()

        def _deduplicate_registry():
            """Deduplicate stores and items across the entire A2C2 Registry."""
            cur_reg = self.data_store.get_enforcement_registry()
            if not cur_reg:
                messagebox.showinfo("Deduplicate Registry", "Enforcement registry is empty.", parent=win)
                return

            purged_items = 0
            merged_stores = 0
            cleaned_reg = {}

            for s_name, data in cur_reg.items():
                canon_key = s_name.strip()
                if not canon_key:
                    continue

                if canon_key not in cleaned_reg:
                    cleaned_reg[canon_key] = {
                        "brands": set(data.get("brands", [])),
                        "product_types": set(data.get("product_types", [])),
                        "locations": set(data.get("locations", [])),
                        "items": [],
                        "scan_count": data.get("scan_count", 1),
                        "first_seen": data.get("first_seen", ""),
                        "last_scanned": data.get("last_scanned", "")
                    }
                else:
                    merged_stores += 1
                    cleaned_reg[canon_key]["brands"].update(data.get("brands", []))
                    cleaned_reg[canon_key]["product_types"].update(data.get("product_types", []))
                    cleaned_reg[canon_key]["locations"].update(data.get("locations", []))
                    cleaned_reg[canon_key]["scan_count"] += data.get("scan_count", 1)

                seen_item_ids = {str(it.get("item_id", "")).strip() for it in cleaned_reg[canon_key]["items"] if it.get("item_id")}
                for it in data.get("items", []):
                    iid = str(it.get("item_id", "")).strip()
                    if iid and iid in seen_item_ids:
                        purged_items += 1
                        continue
                    if iid:
                        seen_item_ids.add(iid)
                    cleaned_reg[canon_key]["items"].append(it)

            final_dict = {}
            for k, v in cleaned_reg.items():
                total_val = 0.0
                for it in v["items"]:
                    m_p = re.search(r"[\d,]+(?:\.\d+)?", str(it.get("price", "")))
                    if m_p:
                        try: total_val += float(m_p.group(0).replace(",", ""))
                        except Exception: pass
                final_dict[k] = {
                    "brands": sorted(list(v["brands"])),
                    "product_types": sorted(list(v["product_types"])),
                    "locations": sorted(list(v["locations"])),
                    "items": v["items"],
                    "total_listings": len(v["items"]),
                    "total_value": round(total_val, 2),
                    "scan_count": v["scan_count"],
                    "first_seen": v["first_seen"],
                    "last_scanned": v["last_scanned"]
                }

            self.data_store.save_enforcement_registry(final_dict)
            _populate_tree()
            _refresh_kpis()
            self._log(f"🧹 A2C2 Registry Deduplicated: Merged {merged_stores} duplicate store(s), purged {purged_items} duplicate listing(s).")
            messagebox.showinfo("Registry Deduplicated", f"Registry Cleaned Successfully!\n\n• Merged Duplicate Stores: {merged_stores}\n• Duplicate Listings Purged: {purged_items}\n• Total Clean Stores in Registry: {len(final_dict)}", parent=win)

        def _delete_selected_entry():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Select Store", "Select an entry to remove.", parent=win)
                return
            if messagebox.askyesno("Delete Entry", f"Remove {len(sel)} selected store record(s) from registry?", parent=win):
                for seller_key in sel:
                    self.data_store.delete_registry_entry(seller_key)
                _populate_tree()
                _refresh_kpis()
                self._log(f"🗑 Removed {len(sel)} store record(s) from Enforcement Registry.")

        self._btn(btn_row, "📄 Export Enterprise Dossier (.xlsx)", _export_dossier, accent=True).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "🔍 Inspect Store Listings", _inspect_selected_seller).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "⚡ Queue Re-Enforcement Sweep", _queue_reenforcement_sweep).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "🧹 Deduplicate Registry", _deduplicate_registry).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "🗑 Remove Store Entry", _delete_selected_entry, danger=True).pack(side="left", padx=(0, 6))

        self._btn(btn_row, "✕ Close", win.destroy).pack(side="right")
        tree.bind("<Double-1>", lambda e: _inspect_selected_seller())

    def _open_seller_items_inspector(self, seller_name: str, seller_data: dict):
        """Open detailed inspector for all captured listings under a specific seller."""
        t = self.theme
        win = tk.Toplevel(self)
        win.title(f"🔍 Seller Listings Inspector — {seller_name}")
        win.configure(bg=t["bg"])
        win.geometry("980x540")
        win.minsize(800, 420)
        self._apply_dark_titlebar(win)

        # Center relative to main window
        win.update_idletasks()
        p_x = self.winfo_rootx()
        p_y = self.winfo_rooty()
        p_w = self.winfo_width()
        p_h = self.winfo_height()
        w, h = 980, 540
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        pad_f = tk.Frame(win, bg=t["bg"], padx=12, pady=10)
        pad_f.pack(fill="both", expand=True)

        head_f = tk.Frame(pad_f, bg=t["panel"], padx=10, pady=8)
        head_f.pack(fill="x", pady=(0, 8))

        tk.Label(head_f, text=f"Store / Seller: {seller_name}", font=("Segoe UI", 11, "bold"),
                 bg=t["panel"], fg=t["accent"]).pack(side="left")

        val_str = f"Total Value: ${seller_data.get('total_value', 0.0):,.2f}  •  {seller_data.get('total_listings', len(seller_data.get('items', [])))} Listing(s)"
        tk.Label(head_f, text=val_str, font=FONT_SM, bg=t["panel"], fg=t["text"]).pack(side="right")

        tree_frame = tk.Frame(pad_f, bg=t["bg"])
        tree_frame.pack(fill="both", expand=True)

        cols = ("brand", "product_type", "title", "item_id", "price", "location", "url")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        col_w = {"brand": 80, "product_type": 120, "title": 300, "item_id": 110, "price": 80, "location": 110, "url": 150}
        for c in cols:
            tree.heading(c, text=self.col_labels.get(c, c.title()))
            tree.column(c, width=col_w.get(c, 100))
        self._style_tree(tree)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for it in seller_data.get("items", []):
            tree.insert("", "end", values=(
                it.get("brand", ""),
                it.get("product_type", ""),
                it.get("title", ""),
                it.get("item_id", ""),
                it.get("price", ""),
                it.get("location", ""),
                it.get("url", "")
            ))

        def _open_row_url(e):
            sel = tree.focus()
            if sel:
                vals = tree.item(sel)["values"]
                if len(vals) > 6 and vals[6]:
                    webbrowser.open(vals[6])

        tree.bind("<Double-1>", _open_row_url)

        btn_row = tk.Frame(pad_f, bg=t["bg"])
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Label(btn_row, text="💡 Double-click any listing to open live on eBay",
                 font=FONT_SM, bg=t["bg"], fg=t["subtext"]).pack(side="left")
        self._btn(btn_row, "✕ Close", win.destroy, accent=True).pack(side="right")

    # ══════════════════════════════════════════════════════════════════════════
    #  CROSS-MARKETPLACE THREAT INTELLIGENCE & ENFORCEMENT ROI HUB
    # ══════════════════════════════════════════════════════════════════════════
    def _open_threat_intel_window(self):
        """Open the Executive Cross-Marketplace Threat Intelligence & Enforcement ROI Hub."""
        if self._win_threat_intel and self._win_threat_intel.winfo_exists():
            self._win_threat_intel.lift()
            self._win_threat_intel.focus_force()
            return

        t = self.theme
        win = tk.Toplevel(self)
        self._win_threat_intel = win
        win.title("🕵️ Cross-Marketplace Threat Intelligence & Enforcement ROI Hub")
        win.configure(bg=t["bg"])
        win.geometry("1240x720")
        win.minsize(1020, 600)
        self._apply_dark_titlebar(win)

        # Center relative to main window
        win.update_idletasks()
        p_x = self.winfo_rootx()
        p_y = self.winfo_rooty()
        p_w = self.winfo_width()
        p_h = self.winfo_height()
        w, h = 1240, 720
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        pad_f = tk.Frame(win, bg=t["bg"], padx=14, pady=12)
        pad_f.pack(fill="both", expand=True)

        # ── Data Aggregation & Intelligence Computation ───────────────────────
        all_items = []
        mkt_counts = {"eBay": 0, "AliExpress": 0, "Wish": 0, "Temu": 0, "Other": 0}
        total_cf_value = 0.0
        total_msrp_est = 0.0
        brand_stats = {}
        supply_chain_matches = []
        sorted_brands = []

        # ── KPI Header Banner (4 Metric Cards) ───────────────────────────────
        kpi_frame = tk.Frame(pad_f, bg=t["bg"])
        kpi_frame.pack(fill="x", pady=(0, 10))

        kpi_cards = {}
        def _kpi(parent, icon, title, key, accent_col):
            card = tk.Frame(parent, bg=t["panel"], padx=12, pady=8, highlightbackground=t["border"], highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=4)
            h_row = tk.Frame(card, bg=t["panel"])
            h_row.pack(fill="x")
            tk.Label(h_row, text=f"{icon} {title}", font=FONT_SM, bg=t["panel"], fg=t["subtext"]).pack(side="left")
            val_lbl = tk.Label(card, text="0", font=("Segoe UI", 15, "bold"), bg=t["panel"], fg=accent_col)
            val_lbl.pack(anchor="w", pady=(2, 0))
            sub_lbl = tk.Label(card, text="", font=("Segoe UI", 8), bg=t["panel"], fg=t["subtext"])
            sub_lbl.pack(anchor="w")
            kpi_cards[key] = (val_lbl, sub_lbl)

        _kpi(kpi_frame, "🛡️", "INFRINGEMENTS IDENTIFIED", "items", t["accent"])
        _kpi(kpi_frame, "💰", "ESTIMATED MSRP PROTECTED", "msrp", t["success"])
        _kpi(kpi_frame, "🌐", "MULTI-MARKETPLACE REACH", "mkts", t.get("accent2", t["accent"]))
        _kpi(kpi_frame, "🔗", "SUPPLY CHAINS LINKED", "chains", t["warning"])

        def _recalculate_intel():
            nonlocal all_items, mkt_counts, total_cf_value, total_msrp_est, brand_stats, supply_chain_matches, sorted_brands
            all_items = list(self.results)
            reg = self.data_store.get_enforcement_registry()
            for s_name, s_data in reg.items():
                for it in s_data.get("items", []):
                    if it not in all_items:
                        all_items.append(it)

            mkt_counts = {"eBay": 0, "AliExpress": 0, "Wish": 0, "Temu": 0, "Mercado Libre": 0, "Redbubble": 0, "Printerval": 0, "Other": 0}
            total_cf_value = 0.0
            total_msrp_est = 0.0
            brand_stats = {}

            for it in all_items:
                mkt_raw = it.get("marketplace", "").lower()
                url_raw = it.get("url", "").lower()
                
                if "ebay" in mkt_raw or "ebay.com" in url_raw:
                    mkt_key = "eBay"
                elif "ali" in mkt_raw or "aliexpress.com" in url_raw:
                    mkt_key = "AliExpress"
                elif "wish" in mkt_raw or "wish.com" in url_raw:
                    mkt_key = "Wish"
                elif "temu" in mkt_raw or "temu.com" in url_raw:
                    mkt_key = "Temu"
                elif "meli" in mkt_raw or "mercadolibre" in mkt_raw or "mercadolivre" in mkt_raw or "mercadolibre.com" in url_raw:
                    mkt_key = "Mercado Libre"
                elif "redbubble" in mkt_raw or "redbubble.com" in url_raw:
                    mkt_key = "Redbubble"
                elif "printerval" in mkt_raw or "printerval.com" in url_raw:
                    mkt_key = "Printerval"
                else:
                    mkt_key = "Other"
                mkt_counts[mkt_key] += 1

                p_val = 0.0
                if "price_usd" in it and isinstance(it["price_usd"], (int, float)) and it["price_usd"] > 0:
                    p_val = float(it["price_usd"])
                else:
                    m_p = re.search(r"[\d,]+(?:\.\d+)?", str(it.get("price", "")))
                    if m_p:
                        try: p_val = float(m_p.group(0).replace(",", ""))
                        except ValueError: p_val = 0.0
                if p_val <= 0:
                    p_val = 14.50

                total_cf_value += p_val

                pt = str(it.get("product_type", "")).lower()
                if "headlamp" in pt or "light" in pt:
                    msrp_val = max(p_val * 4.0, 550.0)
                elif "fob" in pt or "key" in pt:
                    msrp_val = max(p_val * 6.0, 225.0)
                elif "badge" in pt or "emblem" in pt:
                    msrp_val = max(p_val * 7.5, 85.0)
                elif "brake" in pt or "caliper" in pt:
                    msrp_val = max(p_val * 5.0, 450.0)
                else:
                    msrp_val = p_val * 5.5

                total_msrp_est += msrp_val

                brand = it.get("brand") or "General Automotive"
                if brand not in brand_stats:
                    brand_stats[brand] = {"count": 0, "cf_val": 0.0, "msrp_val": 0.0, "mkts": set()}
                brand_stats[brand]["count"] += 1
                brand_stats[brand]["cf_val"] += p_val
                brand_stats[brand]["msrp_val"] += msrp_val
                brand_stats[brand]["mkts"].add(mkt_key)

            # Correlations (eBay vs Suppliers)
            ebay_items = [it for it in all_items if "ebay" in it.get("marketplace", "").lower() or "ebay.com" in it.get("url", "").lower()]
            china_items = [it for it in all_items if it not in ebay_items]

            supply_chain_matches = []
            stop_words = {"for", "and", "the", "car", "auto", "with", "set", "pair", "pcs", "piece", "universal", "fit", "new", "replacement", "style", "front", "rear"}

            def get_tokens(title):
                words = re.findall(r"[a-zA-Z0-9]+", title.lower())
                return {w for w in words if len(w) > 2 and w not in stop_words}

            seen_pairs = set()
            for eb in ebay_items[:150]:
                eb_brand = (eb.get("brand") or "").lower()
                eb_toks = get_tokens(eb.get("title", ""))
                if not eb_toks:
                    continue

                eb_p = 0.0
                m1 = re.search(r"[\d,]+(?:\.\d+)?", str(eb.get("price", "")))
                if m1:
                    try: eb_p = float(m1.group(0).replace(",", ""))
                    except ValueError: eb_p = 28.00

                for ch in china_items:
                    ch_brand = (ch.get("brand") or "").lower()
                    if eb_brand and ch_brand and eb_brand != ch_brand:
                        continue

                    ch_toks = get_tokens(ch.get("title", ""))
                    overlap = eb_toks.intersection(ch_toks)

                    if len(overlap) >= 2:
                        pair_key = (eb.get("item_id"), ch.get("item_id"))
                        if pair_key in seen_pairs:
                            continue
                        seen_pairs.add(pair_key)

                        ch_p = 0.0
                        if "price_usd" in ch and isinstance(ch["price_usd"], (int, float)) and ch["price_usd"] > 0:
                            ch_p = float(ch["price_usd"])
                        else:
                            m2 = re.search(r"[\d,]+(?:\.\d+)?", str(ch.get("price", "")))
                            if m2:
                                try: ch_p = float(m2.group(0).replace(",", ""))
                                except ValueError: ch_p = 3.50

                        spread = max(0.0, eb_p - ch_p)
                        margin_pct = int(((eb_p - ch_p) / ch_p * 100)) if ch_p > 0 else 500

                        if margin_pct > 700:
                            threat = "🔴 CRITICAL"
                        elif margin_pct > 300:
                            threat = "🟠 HIGH"
                        else:
                            threat = "🟡 ELEVATED"

                        supply_chain_matches.append({
                            "keyword": " ".join(list(overlap)[:3]).title(),
                            "brand": eb.get("brand") or ch.get("brand") or "Automotive",
                            "dropshipper": eb.get("seller") or "eBay Rogue Seller",
                            "ebay_price": f"${eb_p:.2f}" if eb_p > 0 else "$29.99",
                            "supplier": ch.get("seller") or "Supplier / Merchant",
                            "platform": ch.get("marketplace", "AliExpress"),
                            "china_price": f"${ch_p:.2f}" if ch_p > 0 else "$2.50",
                            "spread": f"+${spread:.2f}",
                            "margin": f"+{margin_pct:,}%",
                            "threat": threat,
                            "ebay_url": eb.get("url", ""),
                            "china_url": ch.get("url", "")
                        })

                        if len(supply_chain_matches) >= 80:
                            break

            sorted_brands = sorted(brand_stats.items(), key=lambda x: x[1]["msrp_val"], reverse=True)

            # Update KPI card texts
            if "items" in kpi_cards:
                kpi_cards["items"][0].config(text=f"{len(all_items):,} Listings")
                kpi_cards["items"][1].config(text=f"{len(self.results):,} in current active session")
            if "msrp" in kpi_cards:
                kpi_cards["msrp"][0].config(text=f"${total_msrp_est:,.2f}")
                kpi_cards["msrp"][1].config(text=f"${total_cf_value:,.2f} illegal GMV captured")
            if "mkts" in kpi_cards:
                kpi_cards["mkts"][0].config(text=f"{len([k for k, v in mkt_counts.items() if v > 0])} Platforms")
                kpi_cards["mkts"][1].config(text=f"eBay: {mkt_counts['eBay']} | Ali: {mkt_counts['AliExpress']} | Wish: {mkt_counts['Wish']} | Temu: {mkt_counts['Temu']} | MeLi: {mkt_counts['Mercado Libre']} | Redbubble: {mkt_counts['Redbubble']} | Printerval: {mkt_counts['Printerval']}")
            if "chains" in kpi_cards:
                kpi_cards["chains"][0].config(text=f"{len(supply_chain_matches)} Rogue Links")
                kpi_cards["chains"][1].config(text="Cross-marketplace dropship matches")

        _recalculate_intel()

        # ── Notebook Navigation Tabs ──────────────────────────────────────────
        nb_frame = tk.Frame(pad_f, bg=t["bg"])
        nb_frame.pack(fill="both", expand=True)

        notebook = ttk.Notebook(nb_frame)
        notebook.pack(fill="both", expand=True)

        def _matches_intel_query(target_text, query_str):
            if not query_str:
                return True
            target_lower = target_text.lower()
            import shlex
            try:
                raw_tokens = shlex.split(query_str)
            except Exception:
                raw_tokens = query_str.split()

            positive_tokens = []
            negative_tokens = []

            for tok in raw_tokens:
                tok = tok.strip()
                if not tok:
                    continue
                if tok.startswith("-") and len(tok) > 1:
                    negative_tokens.append(tok[1:].lower())
                elif tok.startswith("+") and len(tok) > 1:
                    positive_tokens.append(tok[1:].lower())
                else:
                    positive_tokens.append(tok.lower())

            for neg in negative_tokens:
                if neg in target_lower:
                    return False

            for pos in positive_tokens:
                if pos not in target_lower:
                    return False

            return True

        # ── TAB 1: Supply Chain & Arbitrage Matrix ────────────────────────────
        tab1 = tk.Frame(notebook, bg=t["bg"], padx=6, pady=6)
        notebook.add(tab1, text="🔗 Cross-Marketplace Supply Chain & Price Arbitrage Matrix")

        t1_head = tk.Frame(tab1, bg=t["bg"])
        t1_head.pack(fill="x", pady=(0, 6))

        tk.Label(t1_head, text="🔍 Filter:", font=FONT_SM, bg=t["bg"], fg=t["accent"]).pack(side="left", padx=(0, 4))
        t1_col_var = tk.StringVar(value="All Columns")
        t1_cols = ["All Columns", "Product Match", "Brand", "eBay Dropshipper", "Upstream Supplier", "Platform", "Threat Level"]
        t1_col_combo = ttk.Combobox(t1_head, textvariable=t1_col_var, values=t1_cols, width=15, state="readonly", font=FONT_SM)
        t1_col_combo.pack(side="left", padx=(0, 6))

        t1_filter_var = tk.StringVar()
        t1_filter_entry = tk.Entry(t1_head, textvariable=t1_filter_var, width=18,
                                   bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                   relief="flat", font=FONT_SM)
        t1_filter_entry.pack(side="left", padx=(0, 6))

        tree1_frame = tk.Frame(tab1, bg=t["bg"])
        tree1_frame.pack(fill="both", expand=True)

        cols1 = ("keyword", "brand", "dropshipper", "ebay_price", "supplier", "platform", "china_price", "spread", "margin", "threat")
        tree1 = ttk.Treeview(tree1_frame, columns=cols1, show="headings", selectmode="extended")
        w1 = {"keyword": 130, "brand": 90, "dropshipper": 120, "ebay_price": 75, "supplier": 130, "platform": 95, "china_price": 75, "spread": 85, "margin": 80, "threat": 95}
        l1 = {"keyword": "Product Match", "brand": "Brand", "dropshipper": "eBay Dropshipper", "ebay_price": "eBay Price", "supplier": "Upstream Supplier", "platform": "Platform", "china_price": "Source Price", "spread": "Gross Spread", "margin": "Est. Margin", "threat": "Threat Level"}

        t1_sort_dirs = {}
        def _sort_tree1(col):
            descending = t1_sort_dirs.get(col, False)
            t1_sort_dirs[col] = not descending
            def _k(m):
                v = m.get(col, "")
                if col in ("ebay_price", "china_price", "spread"):
                    m_p = re.search(r"[\d,]+(?:\.\d+)?", str(v))
                    return float(m_p.group(0).replace(",", "")) if m_p else 0.0
                elif col == "margin":
                    m_p = re.search(r"[\d,]+", str(v))
                    return int(m_p.group(0).replace(",", "")) if m_p else 0
                return str(v).lower()
            supply_chain_matches.sort(key=_k, reverse=descending)
            _populate_tree1()
            for c in cols1:
                arrow = (" ▼" if descending else " ▲") if c == col else ""
                tree1.heading(c, text=f"{l1[c]}{arrow}", command=lambda _c=c: _sort_tree1(_c))

        for c in cols1:
            tree1.heading(c, text=l1[c], command=lambda _c=c: _sort_tree1(_c))
            tree1.column(c, width=w1.get(c, 90))
        self._style_tree(tree1)

        vsb1 = ttk.Scrollbar(tree1_frame, orient="vertical", command=tree1.yview)
        tree1.configure(yscrollcommand=vsb1.set)
        tree1.pack(side="left", fill="both", expand=True)
        vsb1.pack(side="right", fill="y")

        def _populate_tree1():
            tree1.delete(*tree1.get_children())
            q = t1_filter_var.get().strip()
            c_target = t1_col_var.get().lower()

            for m in supply_chain_matches:
                if "product" in c_target or "match" in c_target:
                    target_txt = m["keyword"]
                elif "brand" in c_target:
                    target_txt = m["brand"]
                elif "dropship" in c_target:
                    target_txt = m["dropshipper"]
                elif "supplier" in c_target:
                    target_txt = m["supplier"]
                elif "platform" in c_target:
                    target_txt = m["platform"]
                elif "threat" in c_target:
                    target_txt = m["threat"]
                else:
                    target_txt = f"{m['keyword']} {m['brand']} {m['dropshipper']} {m['supplier']} {m['platform']} {m['threat']}"

                if q and not _matches_intel_query(target_txt, q):
                    continue

                tree1.insert("", "end", values=(
                    m["keyword"],
                    m["brand"],
                    m["dropshipper"],
                    m["ebay_price"],
                    m["supplier"],
                    m["platform"],
                    m["china_price"],
                    m["spread"],
                    m["margin"],
                    m["threat"]
                ))

        t1_filter_var.trace_add("write", lambda *a: _populate_tree1())
        t1_col_combo.bind("<<ComboboxSelected>>", lambda e: _populate_tree1())

        def _clear_t1_filter():
            t1_filter_var.set("")
            t1_col_var.set("All Columns")

        def _select_all_t1_visible():
            ch = tree1.get_children()
            if ch:
                tree1.selection_set(ch)

        self._btn(t1_head, "✕ Clear", _clear_t1_filter).pack(side="left", padx=(0, 4))
        self._btn(t1_head, "✓ Select All Visible", _select_all_t1_visible).pack(side="left", padx=(0, 4))

        _populate_tree1()

        def _open_chain_urls(e):
            sel = tree1.focus()
            if sel:
                idx = tree1.index(sel)
                if idx < len(supply_chain_matches):
                    match_data = supply_chain_matches[idx]
                    if match_data.get("ebay_url"):
                        webbrowser.open(match_data["ebay_url"])
                    if match_data.get("china_url"):
                        webbrowser.open(match_data["china_url"])

        tree1.bind("<Double-1>", _open_chain_urls)

        # ── TAB 2: Brand & Client ROI Breakdown ───────────────────────────────
        tab2 = tk.Frame(notebook, bg=t["bg"], padx=6, pady=6)
        notebook.add(tab2, text="📊 Client Enforcement ROI & Brand Value Protection")

        t2_head = tk.Frame(tab2, bg=t["bg"])
        t2_head.pack(fill="x", pady=(0, 6))

        tk.Label(t2_head, text="🔍 Filter:", font=FONT_SM, bg=t["bg"], fg=t["accent"]).pack(side="left", padx=(0, 4))
        t2_col_var = tk.StringVar(value="All Columns")
        t2_cols = ["All Columns", "Client / Brand", "Platforms", "Priority Rating"]
        t2_col_combo = ttk.Combobox(t2_head, textvariable=t2_col_var, values=t2_cols, width=15, state="readonly", font=FONT_SM)
        t2_col_combo.pack(side="left", padx=(0, 6))

        t2_filter_var = tk.StringVar()
        t2_filter_entry = tk.Entry(t2_head, textvariable=t2_filter_var, width=18,
                                   bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                   relief="flat", font=FONT_SM)
        t2_filter_entry.pack(side="left", padx=(0, 6))

        tree2_frame = tk.Frame(tab2, bg=t["bg"])
        tree2_frame.pack(fill="both", expand=True)

        cols2 = ("brand", "count", "avg_price", "msrp_protected", "platforms", "threat_rating")
        tree2 = ttk.Treeview(tree2_frame, columns=cols2, show="headings", selectmode="extended")
        w2 = {"brand": 140, "count": 100, "avg_price": 95, "msrp_protected": 150, "platforms": 160, "threat_rating": 110}
        l2 = {"brand": "Client / Brand", "count": "Seized Listings", "avg_price": "Avg Illegal Price", "msrp_protected": "Est. Genuine MSRP Protected", "platforms": "Marketplace Footprint", "threat_rating": "Priority Rating"}

        t2_sort_dirs = {}
        def _sort_tree2(col):
            descending = t2_sort_dirs.get(col, False)
            t2_sort_dirs[col] = not descending
            def _k(pair):
                b_name, b_info = pair
                if col == "brand":
                    return b_name.lower()
                elif col == "count":
                    return b_info.get("count", 0)
                elif col == "avg_price":
                    return (b_info["cf_val"] / b_info["count"]) if b_info["count"] > 0 else 0.0
                elif col == "msrp_protected":
                    return b_info.get("msrp_val", 0.0)
                elif col == "platforms":
                    return len(b_info.get("mkts", []))
                elif col == "threat_rating":
                    return b_info.get("msrp_val", 0.0)
                return str(b_name).lower()
            sorted_brands.sort(key=_k, reverse=descending)
            _populate_tree2()
            for c in cols2:
                arrow = (" ▼" if descending else " ▲") if c == col else ""
                tree2.heading(c, text=f"{l2[c]}{arrow}", command=lambda _c=c: _sort_tree2(_c))

        for c in cols2:
            tree2.heading(c, text=l2[c], command=lambda _c=c: _sort_tree2(_c))
            tree2.column(c, width=w2.get(c, 100))
        self._style_tree(tree2)

        vsb2 = ttk.Scrollbar(tree2_frame, orient="vertical", command=tree2.yview)
        tree2.configure(yscrollcommand=vsb2.set)
        tree2.pack(side="left", fill="both", expand=True)
        vsb2.pack(side="right", fill="y")

        def _populate_tree2():
            tree2.delete(*tree2.get_children())
            q = t2_filter_var.get().strip()
            c_target = t2_col_var.get().lower()

            for b_name, b_info in sorted_brands:
                avg_p = b_info["cf_val"] / b_info["count"] if b_info["count"] > 0 else 0.0
                rating = "🔥 HIGH PRIORITY" if b_info["msrp_val"] > 50000 else "⚡ ACTIVE TARGET"
                mkts_str = ", ".join(b_info["mkts"])

                if "brand" in c_target or "client" in c_target:
                    target_txt = b_name
                elif "platform" in c_target:
                    target_txt = mkts_str
                elif "rating" in c_target or "priority" in c_target:
                    target_txt = rating
                else:
                    target_txt = f"{b_name} {mkts_str} {rating}"

                if q and not _matches_intel_query(target_txt, q):
                    continue

                tree2.insert("", "end", values=(
                    b_name,
                    f"{b_info['count']:,} listings",
                    f"${avg_p:.2f}",
                    f"${b_info['msrp_val']:,.2f}",
                    mkts_str,
                    rating
                ))

        t2_filter_var.trace_add("write", lambda *a: _populate_tree2())
        t2_col_combo.bind("<<ComboboxSelected>>", lambda e: _populate_tree2())

        def _clear_t2_filter():
            t2_filter_var.set("")
            t2_col_var.set("All Columns")

        def _select_all_t2_visible():
            ch = tree2.get_children()
            if ch:
                tree2.selection_set(ch)

        self._btn(t2_head, "✕ Clear", _clear_t2_filter).pack(side="left", padx=(0, 4))
        self._btn(t2_head, "✓ Select All Visible", _select_all_t2_visible).pack(side="left", padx=(0, 4))

        _populate_tree2()

        # ── Action Buttons ───────────────────────────────────────────────────
        btn_row = tk.Frame(pad_f, bg=t["bg"])
        btn_row.pack(fill="x", pady=(10, 0))

        def _export_threat_intel():
            now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Workbook", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"threat_intel_report_{now_str}.xlsx"
            )
            if not path:
                return

            try:
                import openpyxl
                wb = openpyxl.Workbook()
                wb.properties.creator = "Jerry Seidenstucker"
                wb.properties.title = "Threat Intelligence & ROI Report"

                # Sheet 1: ROI Summary
                ws_roi = wb.active
                ws_roi.title = "Brand ROI Protection"
                ws_roi.append(["Client / Brand", "Seized Listings", "Avg Illegal Price", "Est. Genuine MSRP Protected", "Marketplace Footprint", "Priority Rating"])
                for b_name, b_info in sorted_brands:
                    avg_p = b_info["cf_val"] / b_info["count"] if b_info["count"] > 0 else 0.0
                    ws_roi.append([b_name, b_info["count"], f"${avg_p:.2f}", f"${b_info['msrp_val']:,.2f}", ", ".join(b_info["mkts"]), "High Priority"])

                # Sheet 2: Supply Chain Matches
                ws_sc = wb.create_sheet(title="Cross-Marketplace Supply Chains")
                ws_sc.append(["Product Match", "Brand", "eBay Dropshipper", "eBay Price", "Upstream Supplier", "Platform", "Source Price", "Gross Spread", "Est. Margin", "Threat Level", "eBay URL", "Supplier URL"])
                for m in supply_chain_matches:
                    ws_sc.append([m["keyword"], m["brand"], m["dropshipper"], m["ebay_price"], m["supplier"], m["platform"], m["china_price"], m["spread"], m["margin"], m["threat"], m.get("ebay_url",""), m.get("china_url","")])

                wb.save(path)
                self._log(f"🕵️ Threat Intelligence & ROI Dossier exported → {path}")
                messagebox.showinfo("Export Complete", f"Saved Threat Intelligence & ROI Dossier to:\n{path}", parent=win)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}", parent=win)

        def _copy_summary():
            summary_txt = (
                f"═══════════════════════════════════════════════════════════════════\n"
                f"       EXECUTIVE BRAND ENFORCEMENT & THREAT INTEL SUMMARY          \n"
                f"═══════════════════════════════════════════════════════════════════\n"
                f"Report Date           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Total Infringements   : {len(all_items):,} Listings\n"
                f"Estimated MSRP Seized : ${total_msrp_est:,.2f}\n"
                f"Illegal GMV Identified: ${total_cf_value:,.2f}\n"
                f"Marketplace Breakdown : eBay ({mkt_counts['eBay']}) | AliExpress ({mkt_counts['AliExpress']}) | Wish ({mkt_counts['Wish']}) | Temu ({mkt_counts['Temu']}) | MeLi ({mkt_counts['Mercado Libre']}) | Redbubble ({mkt_counts['Redbubble']}) | Printerval ({mkt_counts['Printerval']})\n"
                f"Rogue Supply Chains   : {len(supply_chain_matches)} Connected Dropship Links\n"
                f"═══════════════════════════════════════════════════════════════════\n"
            )
            self.clipboard_clear()
            self.clipboard_append(summary_txt)
            messagebox.showinfo("Copied", "Executive Summary copied to clipboard!", parent=win)

        def _deduplicate_threat_intel():
            """Deduplicate active session items and recalculate threat intelligence metrics."""
            initial_len = len(self.results)
            seen_ids = set()
            seen_urls = set()
            unique_items = []

            for it in self.results:
                iid = str(it.get("item_id", "")).strip()
                url = str(it.get("url", "")).strip().lower()
                norm_url = url.split("?")[0] if url else ""

                if (iid and iid in seen_ids) or (norm_url and norm_url in seen_urls):
                    continue

                if iid: seen_ids.add(iid)
                if norm_url: seen_urls.add(norm_url)
                unique_items.append(it)

            purged = initial_len - len(unique_items)
            self.results = unique_items
            self.seen_item_ids = {str(it.get("item_id", "")).strip() for it in self.results if it.get("item_id")}
            self._repopulate_results_table()

            _recalculate_intel()
            _populate_tree1()
            _populate_tree2()

            self._log(f"🧹 Threat Intel Deduplicated: Purged {purged} duplicate items. Recomputed KPIs and supply chain matrix.")
            messagebox.showinfo("Threat Intel Deduplicated", f"Threat Intel Cleaned Successfully!\n\n• Duplicate Items Purged: {purged}\n• Total Unique Listings: {len(all_items):,}\n• Supply Chain Links: {len(supply_chain_matches)}", parent=win)

        self._btn(btn_row, "📄 Export Threat Intel Dossier (.xlsx)", _export_threat_intel, accent=True).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "📋 Copy Executive Summary", _copy_summary).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "🧹 Deduplicate Threat Intel", _deduplicate_threat_intel).pack(side="left", padx=(0, 6))
        tk.Label(btn_row, text="💡 Double-click any row in Tab 1 to open eBay & Supplier links side-by-side",
                 font=FONT_SM, bg=t["bg"], fg=t["subtext"]).pack(side="left", padx=(10, 0))

        self._btn(btn_row, "✕ Close", win.destroy).pack(side="right")

    def _show_about_dialog(self):
        """Show About, Valknut Ethos & Architecture, and Intellectual Property Disclaimer dialog."""
        t = self.theme
        win = tk.Toplevel(self)
        win.title("About 🔺 Valknut Brand Intelligence")
        win.configure(bg=t["bg"])
        win.geometry("880x700")
        win.minsize(820, 620)
        win.transient(self)
        win.grab_set()
        self._apply_dark_titlebar(win)

        # Center dialog relative to main window
        win.update_idletasks()
        p_x = self.winfo_rootx()
        p_y = self.winfo_rooty()
        p_w = self.winfo_width()
        p_h = self.winfo_height()
        w, h = 880, 700
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        # Secret word easter egg listener scoped strictly inside About dialog
        about_word_buf = [""]
        def _on_about_key(e):
            if hasattr(e, "char") and e.char and e.char.isprintable():
                about_word_buf[0] += e.char.lower()
                if len(about_word_buf[0]) > 25:
                    about_word_buf[0] = about_word_buf[0][-25:]
                if any(w in about_word_buf[0] for w in ("wick", "babayaga", "continental")):
                    self._trigger_wick_easter_egg()
                    about_word_buf[0] = ""
                elif any(w in about_word_buf[0] for w in ("lock", "relock", "hide")):
                    self.data_store.set_setting("unlocked_wick", False)
                    if self.current_theme_key == "continental":
                        self.theme_var.set(THEMES["midnight"]["name"])
                        self._on_theme_changed()
                    vals = [v for v in self.theme_combo["values"] if v != THEMES["continental"]["name"]]
                    self.theme_combo["values"] = vals
                    self._log("🔒 Secret Continental theme relocked and hidden from dropdown.")
                    self._status("🔒 The Continental relocked and secured.")
                    about_word_buf[0] = ""
                elif any(w in about_word_buf[0] for w in ("jarvis", "heimvis")):
                    self._trigger_heimvis_easter_egg()
                    about_word_buf[0] = ""
                elif any(w in about_word_buf[0] for w in ("rick", "astley", "nevergonna", "rickroll")):
                    self._trigger_rickroll_easter_egg()
                    about_word_buf[0] = ""
                elif any(w in about_word_buf[0] for w in ("eleanor", "gobabygo", "shelby")):
                    self._trigger_eleanor_easter_egg()
                    about_word_buf[0] = ""
        win.bind("<Key>", _on_about_key)

        pad_f = tk.Frame(win, bg=t["bg"], padx=20, pady=16)
        pad_f.pack(fill="both", expand=True)

        # ── Header ───────────────────────────────────────────────────────────
        head_f = tk.Frame(pad_f, bg=t["bg"])
        head_f.pack(fill="x", pady=(0, 10))

        tk.Label(head_f, text="🔺 Valknut Brand Intelligence",
                 font=("Segoe UI", 16, "bold"), bg=t["bg"], fg=t["accent"]).pack(anchor="w")

        tk.Label(head_f, text="Targeted Seller Harvester & Cross-Brand Syndicate Defense Suite",
                 font=FONT_SM, bg=t["bg"], fg=t["subtext"]).pack(anchor="w", pady=(2, 0))

        div = tk.Frame(pad_f, bg=t["border"], height=1)
        div.pack(fill="x", pady=(6, 10))

        # ── Notebook / Tabs ──────────────────────────────────────────────────
        style = ttk.Style(win)
        style.theme_use("clam")
        style.configure("About.TNotebook",
                        background=t["bg"],
                        bordercolor=t["border"],
                        darkcolor=t["bg"],
                        lightcolor=t["bg"],
                        tabmargins=[2, 5, 2, 0])
        style.configure("About.TNotebook.Tab",
                        background=t["panel"],
                        foreground=t["text"],
                        bordercolor=t["border"],
                        darkcolor=t["panel"],
                        lightcolor=t["panel"],
                        padding=[16, 8],
                        font=("Segoe UI", 9, "bold"))
        style.map("About.TNotebook.Tab",
                  background=[("selected", t["accent"]), ("active", t["border"])],
                  foreground=[("selected", t.get("btn_accent_fg", "black" if t.get("name", "").startswith("⚡") else "white")),
                              ("active", t["text"])],
                  darkcolor=[("selected", t["accent"]), ("active", t["border"])],
                  lightcolor=[("selected", t["accent"]), ("active", t["border"])],
                  bordercolor=[("selected", t["accent"]), ("active", t["border"])])

        nb = ttk.Notebook(pad_f, style="About.TNotebook")
        nb.pack(fill="both", expand=True)

        # ── TAB 1: Ethos & Architecture ──────────────────────────────────────
        tab_ethos = tk.Frame(nb, bg=t["panel"], padx=16, pady=12)
        nb.add(tab_ethos, text="🔺 Enterprise Architecture & 9 Pillars")

        # Scrollable container for ethos tab
        ethos_canvas = tk.Canvas(tab_ethos, bg=t["panel"], highlightthickness=0)
        ethos_vsb = ttk.Scrollbar(tab_ethos, orient="vertical", command=ethos_canvas.yview)
        ethos_scroll_frame = tk.Frame(ethos_canvas, bg=t["panel"])

        def _on_canvas_configure(event):
            ethos_canvas.configure(scrollregion=ethos_canvas.bbox("all"))
            # Compensate for scrollbar & margins so right edge aligns uniformly
            inner_w = max(680, event.width - 20)
            ethos_canvas.itemconfig(canvas_win_id, width=inner_w)

        canvas_win_id = ethos_canvas.create_window((0, 0), window=ethos_scroll_frame, anchor="nw")
        ethos_canvas.bind("<Configure>", _on_canvas_configure)
        ethos_scroll_frame.bind("<Configure>", lambda e: ethos_canvas.configure(scrollregion=ethos_canvas.bbox("all")))
        ethos_canvas.configure(yscrollcommand=ethos_vsb.set)

        # Enable mousewheel scrolling across canvas
        def _on_mousewheel(event):
            try:
                ethos_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        ethos_canvas.bind("<MouseWheel>", _on_mousewheel)
        ethos_scroll_frame.bind("<MouseWheel>", _on_mousewheel)

        ethos_canvas.pack(side="left", fill="both", expand=True)
        ethos_vsb.pack(side="right", fill="y")

        # Valknut Narrative
        narrative_hdr = tk.Label(ethos_scroll_frame, text="Valknut Brand Intelligence Enterprise Architecture",
                                 font=("Segoe UI", 11, "bold"), bg=t["panel"], fg=t["accent"])
        narrative_hdr.pack(anchor="w", padx=4, pady=(0, 4))
        narrative_hdr.bind("<MouseWheel>", _on_mousewheel)

        narrative_txt = (
            "Valknut Brand Intelligence is an on-demand brand protection platform engineered for "
            "rapid multi-brand seller harvesting, visual syndicate discovery, and multi-jurisdiction compliance dossiers."
        )
        nar_lbl = tk.Label(ethos_scroll_frame, text=narrative_txt, font=FONT_SM, bg=t["panel"],
                           fg=t["text"], wraplength=760, justify="left")
        nar_lbl.pack(anchor="w", padx=4, pady=(0, 10))
        nar_lbl.bind("<MouseWheel>", _on_mousewheel)

        # 3 Triangles Card Frame (Pixel-locked icon boxes & bounded width)
        tri_frame = tk.Frame(ethos_scroll_frame, bg=t["entry_bg"], padx=14, pady=12, relief="flat")
        tri_frame.pack(fill="x", padx=4, pady=(0, 12))
        tri_frame.bind("<MouseWheel>", _on_mousewheel)

        tri_hdr = tk.Label(tri_frame, text="🔺 The Triad of Modern Brand Defense:",
                           font=("Segoe UI", 10, "bold"), bg=t["entry_bg"], fg=t["accent"])
        tri_hdr.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        tri_hdr.bind("<MouseWheel>", _on_mousewheel)

        tri_data = [
            ("🔍", "Pillar 1: Reconnaissance", "Rapid, automated store sweeps across global marketplaces with stealth session handling."),
            ("🛡",  "Pillar 2: Threat Intelligence", "Unmasking 3PL domestic smokescreens, dropship margins, and historical store recidivism."),
            ("⚡", "Pillar 3: Rapid Enforcement", "Standardized, audit-ready Excel compliance packs and multi-locale takedown dossiers."),
        ]

        for r_idx, (icon, title, desc) in enumerate(tri_data, start=1):
            # Fixed 26x22 pixel container to lock horizontal & center alignment for any emoji glyph
            icon_box = tk.Frame(tri_frame, bg=t["entry_bg"], width=26, height=22)
            icon_box.grid(row=r_idx, column=0, sticky="nsew", pady=3, padx=(0, 6))
            icon_box.pack_propagate(False)
            icon_box.bind("<MouseWheel>", _on_mousewheel)

            i_lbl = tk.Label(icon_box, text=icon, font=("Segoe UI", 10),
                             bg=t["entry_bg"], fg=t["accent"])
            i_lbl.pack(expand=True)
            i_lbl.bind("<MouseWheel>", _on_mousewheel)

            t_lbl = tk.Label(tri_frame, text=f"{title}:", font=("Segoe UI", 9, "bold"),
                             bg=t["entry_bg"], fg=t["text"], anchor="w")
            t_lbl.grid(row=r_idx, column=1, sticky="w", pady=3, padx=(0, 10))
            t_lbl.bind("<MouseWheel>", _on_mousewheel)

            d_lbl = tk.Label(tri_frame, text=desc, font=FONT_SM, bg=t["entry_bg"],
                             fg=t["subtext"], wraplength=520, justify="left", anchor="w")
            d_lbl.grid(row=r_idx, column=2, sticky="w", pady=3)
            d_lbl.bind("<MouseWheel>", _on_mousewheel)

        tri_frame.columnconfigure(2, weight=1)

        # 9 Pillars
        p_hdr = tk.Label(ethos_scroll_frame, text="⚔️ The 9 Pillars of Valknut Intelligence:",
                         font=("Segoe UI", 10, "bold"), bg=t["panel"], fg=t["accent"])
        p_hdr.pack(anchor="w", padx=4, pady=(4, 6))
        p_hdr.bind("<MouseWheel>", _on_mousewheel)

        pillars_grid = tk.Frame(ethos_scroll_frame, bg=t["panel"])
        pillars_grid.pack(fill="x", padx=4, pady=(0, 8))
        pillars_grid.bind("<MouseWheel>", _on_mousewheel)

        pillars = [
            ("1. Vigilance", "Comprehensive cross-marketplace seller surveillance (eBay, Ali, Wish, Temu, MeLi)"),
            ("2. Stealth", "Resilient session management and anti-bot mitigation"),
            ("3. Precision", "Multi-layer keyword & brand exclusion shielding to minimize noise"),
            ("4. Traceability", "Unmasking domestic 3PL drop-shippers and cross-border supply chains"),
            ("5. Tenacity", "Tracking repeat offender storefronts across rebrands and re-listings"),
            ("6. Integrity", "Standardized, audit-ready compliance reporting for client review"),
            ("7. Velocity", "Rapid multi-brand batch harvesting across complex seller networks"),
            ("8. Impact", "Quantifiable client revenue protection and enforcement ROI metrics"),
            ("9. Global Scope", "16-country international domain expansion for global takedown parity"),
        ]

        for i, (p_title, p_desc) in enumerate(pillars):
            col = i % 3
            row = i // 3
            cell = tk.Frame(pillars_grid, bg=t["entry_bg"], padx=10, pady=8)
            cell.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            cell.bind("<MouseWheel>", _on_mousewheel)
            pillars_grid.columnconfigure(col, weight=1)

            l1 = tk.Label(cell, text=p_title, font=("Segoe UI", 9, "bold"), bg=t["entry_bg"], fg=t["accent"])
            l1.pack(anchor="w")
            l1.bind("<MouseWheel>", _on_mousewheel)

            l2 = tk.Label(cell, text=p_desc, font=("Segoe UI", 8), bg=t["entry_bg"], fg=t["subtext"], wraplength=220, justify="left")
            l2.pack(anchor="w")
            l2.bind("<MouseWheel>", _on_mousewheel)

        # ── TAB 2: Author, IP & Legal Attribution ────────────────────────────
        tab_legal = tk.Frame(nb, bg=t["panel"], padx=20, pady=18)
        nb.add(tab_legal, text="⚖️ Author & Legal Attribution")

        # Creator / Credits section
        info_frame = tk.Frame(tab_legal, bg=t["entry_bg"], padx=16, pady=14)
        info_frame.pack(fill="x", pady=(0, 14))

        def _row(parent, label, val):
            r = tk.Frame(parent, bg=t["entry_bg"])
            r.pack(fill="x", pady=3)
            tk.Label(r, text=label, font=("Segoe UI", 9, "bold"), bg=t["entry_bg"], fg=t["text"], width=22, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=FONT_SM, bg=t["entry_bg"], fg=t["accent"] if "Jerry Seidenstucker" in val else t["text"], anchor="w").pack(side="left")

        _row(info_frame, "Creator & Lead Architect:", "Jerry Seidenstucker (Personal Project)")
        _row(info_frame, "AI Pair Programmer:", "Antigravity (Google DeepMind)")
        _row(info_frame, "Intellectual Property:", "© 2026 Jerry Seidenstucker. All Rights Reserved.")
        _row(info_frame, "Architecture Version:", "Valknut v3.0 Enterprise Suite")
        _row(info_frame, "License Mode:", "Proprietary / Authorized Internal Evaluation")

        # Legal & Ownership Notice box
        notice_lbl = tk.Label(tab_legal, text="Intellectual Property & Attribution Notice:",
                              font=("Segoe UI", 9, "bold"), bg=t["panel"], fg=t["text"])
        notice_lbl.pack(anchor="w", pady=(4, 4))

        notice_box = tk.Text(tab_legal, height=6, bg=t["entry_bg"], fg=t["subtext"],
                             font=FONT_SM, relief="flat", wrap="word", padx=10, pady=8,
                             bd=0, highlightthickness=0)
        notice_box.pack(fill="x", pady=(0, 6))
        notice_text = (
            "This software and its underlying intelligence architectures were conceived, designed, "
            "and developed independently by Jerry Seidenstucker.\n\n"
            "All rights, title, copyright, and trade secrets in and to this software remain the exclusive "
            "property of the author. Unauthorized corporate appropriation, commercial distribution, or "
            "rebranding without prominent author attribution and express written consent is strictly prohibited."
        )
        notice_box.insert("1.0", notice_text)
        notice_box.config(state="disabled")

        # Close button bar
        btn_row = tk.Frame(pad_f, bg=t["bg"])
        btn_row.pack(fill="x", pady=(12, 0))
        self._btn(btn_row, "Close", win.destroy, accent=True).pack(side="right")

    # ══════════════════════════════════════════════════════════════════════════
    #  LOGGING / STATUS
    # ══════════════════════════════════════════════════════════════════════════
    def _log(self, msg, error=False):
        def _write():
            self.log_text.config(state="normal")
            ts  = datetime.now().strftime("%H:%M:%S")
            tag = "err" if error else "info"
            self.log_text.tag_config("err",  foreground=self.theme["danger"])
            self.log_text.tag_config("info", foreground=self.theme["text"])
            self.log_text.insert("end", f"[{ts}] {msg}\n", tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.after(0, _write)

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _status(self, msg):
        self.after(0, lambda: self.status_var.set(msg))



# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL MULTI-LOCALE EXPANDER & COMPLIANCE EXPORTER
# ══════════════════════════════════════════════════════════════════════════════
class MultiLocaleModal(tk.Toplevel):
    """
    Global Multi-Locale Expander & Compliance Exporter.
    Probes sample item IDs per seller across international eBay domains (.com, .ca, .co.uk, .de, .fr, .it, .es, etc.),
    multiplies verified listings into full international compliance packs, and exports to Excel.
    """
    def __init__(self, parent, target_items: list = None):
        super().__init__(parent)
        self.parent = parent
        self.target_items = target_items if target_items else list(parent.results)
        self.t = parent.theme
        self.locale_vars = {}
        self.locale_status_labels = {}
        self.probe_results = {}
        self.probing = False

        self.title("🌐 Global Multi-Locale Expander & Compliance Exporter")
        self.geometry("980x660")
        self.configure(bg=self.t["bg"])
        self.minsize(840, 520)
        self.parent._apply_dark_titlebar(self)

        # Center modal relative to parent window
        self.update_idletasks()
        p_x = parent.winfo_rootx()
        p_y = parent.winfo_rooty()
        p_w = parent.winfo_width()
        p_h = parent.winfo_height()
        w, h = 980, 660
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.lift()
        self.focus_force()

        self._build_ui()

    def _build_ui(self):
        t = self.t
        pad_f = tk.Frame(self, bg=t["bg"], padx=14, pady=12)
        pad_f.pack(fill="both", expand=True)

        # ── Header Banner ────────────────────────────────────────────────────
        head_f = tk.Frame(pad_f, bg=t["bg"])
        head_f.pack(fill="x", pady=(0, 8))

        tk.Label(head_f, text="🌐 Global Multi-Locale Expander & Compliance Exporter",
                 font=("Segoe UI", 13, "bold"), bg=t["bg"], fg=t["accent"]).pack(side="left")

        tk.Label(head_f, text="Multiply & verify harvested listings across international eBay domains for global sweeps",
                 font=FONT_SM, bg=t["bg"], fg=t["subtext"]).pack(side="left", padx=12, pady=(2, 0))

        # ── Top KPI Stat Badges ──────────────────────────────────────────────
        kpi_f = tk.Frame(pad_f, bg=t["panel"], padx=12, pady=8)
        kpi_f.pack(fill="x", pady=(0, 8))

        unique_sellers = set(it.get("seller", "") for it in self.target_items if it.get("seller"))
        
        self.kpi_labels = {}
        def _kpi(parent, title, val, key, color=None):
            f = tk.Frame(parent, bg=t["panel"], padx=14)
            f.pack(side="left", fill="y")
            tk.Label(f, text=title, font=("Segoe UI", 8, "bold"), bg=t["panel"], fg=t["subtext"]).pack(anchor="w")
            lbl = tk.Label(f, text=val, font=("Segoe UI", 12, "bold"), bg=t["panel"], fg=color or t["text"])
            lbl.pack(anchor="w")
            self.kpi_labels[key] = lbl

        _kpi(kpi_f, "📋 Listings in Batch", f"{len(self.target_items):,}", "items")
        _kpi(kpi_f, "🏬 Unique Sellers", f"{len(unique_sellers):,}", "sellers", color=t["accent"])
        _kpi(kpi_f, "🌐 Selected Locales", "16 of 16", "locales", color=t["accent2"])
        _kpi(kpi_f, "📦 Expanded Output Rows", f"{len(self.target_items) * 16:,}", "output", color=t["success"])

        # ── Preset Toolbar & Probe Action ────────────────────────────────────
        preset_f = tk.Frame(pad_f, bg=t["bg"])
        preset_f.pack(fill="x", pady=(0, 8))

        tk.Label(preset_f, text="⚡ Quick Presets:", font=("Segoe UI", 9, "bold"), bg=t["bg"], fg=t["accent"]).pack(side="left", padx=(0, 6))

        self.parent._btn(preset_f, "🌍 All Verified Global (16)", lambda: self._apply_preset("all")).pack(side="left", padx=2)
        self.parent._btn(preset_f, "🇺🇸 🇨🇦 North America", lambda: self._apply_preset("na")).pack(side="left", padx=2)
        self.parent._btn(preset_f, "🇪🇺 Europe (UK/EU)", lambda: self._apply_preset("eu")).pack(side="left", padx=2)
        self.parent._btn(preset_f, "🇦🇺 APAC (Australia)", lambda: self._apply_preset("apac")).pack(side="left", padx=2)
        self.parent._btn(preset_f, "✕ Clear All", lambda: self._apply_preset("none")).pack(side="left", padx=2)

        self.probe_btn = self.parent._btn(preset_f, "🔬 Probe & Verify Active Domains", self._start_domain_probe, accent=True)
        self.probe_btn.pack(side="right", padx=(4, 0))

        # ── Locale Checkbox Grid ─────────────────────────────────────────────
        grid_frame = tk.Frame(pad_f, bg=t["panel"], padx=10, pady=10, relief="flat", highlightbackground=t["border"], highlightthickness=1)
        grid_frame.pack(fill="both", expand=True, pady=(0, 8))

        for col_idx in range(4):
            grid_frame.columnconfigure(col_idx, weight=1)

        for idx, loc in enumerate(EBAY_LOCALES):
            row = idx // 4
            col = idx % 4

            cell = tk.Frame(grid_frame, bg=t["entry_bg"], padx=8, pady=6, relief="flat", highlightbackground=t["border"], highlightthickness=1)
            cell.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            var = tk.BooleanVar(value=True)
            self.locale_vars[loc["domain"]] = var

            cb = tk.Checkbutton(cell, text=f"{loc['flag']} {loc.get('name', loc.get('country', ''))}", variable=var,
                                command=self._update_kpis, bg=t["entry_bg"], fg=t["text"],
                                selectcolor=t["panel"], activebackground=t["entry_bg"],
                                font=("Segoe UI", 9, "bold"))
            cb.pack(anchor="w")

            sub_f = tk.Frame(cell, bg=t["entry_bg"])
            sub_f.pack(fill="x", pady=(2, 0))

            tk.Label(sub_f, text=f"• {loc['domain']}", font=("Segoe UI", 8), bg=t["entry_bg"], fg=t["subtext"]).pack(side="left")
            
            stat_lbl = tk.Label(sub_f, text=loc.get("region", ""), font=("Segoe UI", 7, "bold"), bg=t["panel"], fg=t["accent"], padx=4, pady=1)
            stat_lbl.pack(side="right")
            self.locale_status_labels[loc["domain"]] = stat_lbl

        # ── Footer Status & Export Action Bar ─────────────────────────────────
        btn_bar = tk.Frame(pad_f, bg=t["panel"], padx=14, pady=10, relief="flat", highlightbackground=t["border"], highlightthickness=1)
        btn_bar.pack(side="bottom", fill="x")

        self.status_var = tk.StringVar(value="Ready to expand listings across selected international eBay domains.")
        self.status_lbl = tk.Label(btn_bar, textvariable=self.status_var, font=FONT_SM, bg=t["panel"], fg=t["text"])
        self.status_lbl.pack(side="left")

        self.parent._btn(btn_bar, "✕ Close", self.destroy).pack(side="right", padx=(4, 0))
        self.export_btn = self.parent._btn(btn_bar, "💾 Export Multi-Locale Enforcement Pack", self._export_multi_locale, accent=True)
        self.export_btn.pack(side="right", padx=(4, 0))

    def _apply_preset(self, preset_name: str):
        for loc in EBAY_LOCALES:
            dom = loc["domain"]
            reg = loc.get("region", "")
            if preset_name == "all":
                self.locale_vars[dom].set(True)
            elif preset_name == "none":
                self.locale_vars[dom].set(False)
            elif preset_name == "na":
                self.locale_vars[dom].set(reg == "North America")
            elif preset_name == "eu":
                self.locale_vars[dom].set(reg == "Europe")
            elif preset_name == "apac":
                self.locale_vars[dom].set(reg == "APAC")
        self._update_kpis()

    def _update_kpis(self):
        selected_count = sum(1 for v in self.locale_vars.values() if v.get())
        total_items = len(self.target_items)
        output_rows = total_items * selected_count
        self.kpi_labels["locales"].config(text=f"{selected_count} of {len(EBAY_LOCALES)}")
        self.kpi_labels["output"].config(text=f"{output_rows:,}")
        self.status_var.set(f"Selected {selected_count} locales → Will generate {output_rows:,} international compliance rows.")

    def _start_domain_probe(self):
        """Probe sample listing per seller in parallel across eBay locales."""
        if self.probing:
            return
        if not self.target_items:
            messagebox.showinfo("Probe", "No items to probe.", parent=self)
            return

        # Pick 1 sample item per unique seller
        sample_items = {}
        for it in self.target_items:
            s = it.get("seller") or "Unknown"
            iid = it.get("item_id")
            if s not in sample_items and iid:
                sample_items[s] = iid

        if not sample_items:
            messagebox.showinfo("Probe", "No valid Item IDs found to probe.", parent=self)
            return

        self.probing = True
        self.probe_btn.config(state="disabled")
        self.status_var.set(f"🔬 Probing {len(sample_items)} sample seller item(s) across 16 global domains...")

        def _worker():
            scraper = getattr(self.parent, "scraper", None)
            if not scraper:
                scraper = EbayScraper(headless=True)

            verified_domains = set()
            for s, iid in sample_items.items():
                active_locales = scraper.probe_item_locales(iid)
                for loc in active_locales:
                    verified_domains.add(loc["domain"])

            def _apply():
                self.probing = False
                self.probe_btn.config(state="normal")
                for loc in EBAY_LOCALES:
                    dom = loc["domain"]
                    lbl = self.locale_status_labels.get(dom)
                    if dom in verified_domains:
                        self.locale_vars[dom].set(True)
                        if lbl: lbl.config(text="🟢 Verified Active", fg=self.t["success"])
                    else:
                        if lbl: lbl.config(text="⚪ Geoblocked / Inactive", fg=self.t["subtext"])
                self._update_kpis()
                self.status_var.set(f"✅ Probe complete: {len(verified_domains)} international domains verified active!")
                messagebox.showinfo("Probe Complete", f"Successfully probed {len(sample_items)} seller(s)!\n\nVerified {len(verified_domains)} active international domains.", parent=self)

            self.after(0, _apply)

        threading.Thread(target=_worker, daemon=True).start()

    def _export_multi_locale(self):
        selected_locales = [loc for loc in EBAY_LOCALES if self.locale_vars.get(loc["domain"], tk.BooleanVar(value=False)).get()]
        if not selected_locales:
            messagebox.showwarning("Select Locales", "Please select at least one international locale to export.", parent=self)
            return

        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"multi_locale_enforcement_{now_str}.xlsx",
            parent=self
        )
        if not path:
            return

        try:
            total_rows = self.parent.exporter.export_multi_locale(self.target_items, selected_locales, path)
            # Ingest verified exported results into Enterprise Brand Enforcement Registry
            seller_items = {}
            for item in self.target_items:
                seller = item.get("seller") or "Unknown"
                seller_items.setdefault(seller, []).append(item)
            for seller, s_items in seller_items.items():
                self.parent.data_store.record_enforcement_scan(seller, s_items)

            self.parent._log(f"🌐 Multi-Locale Enforcement Pack exported: {total_rows} listings across {len(selected_locales)} domains → {path}")
            self.parent._log(f"🛡️ Logged {len(self.target_items)} verified listing(s) across {len(seller_items)} seller(s) into Enterprise Brand Enforcement Registry.")
            self.status_var.set(f"✅ Exported {total_rows:,} rows across {len(selected_locales)} domains to Excel!")
            messagebox.showinfo("Multi-Locale Export Complete",
                                f"Successfully generated Multi-Locale Enforcement Pack!\n\n• Base Harvested Listings: {len(self.target_items):,}\n• Target Locales: {len(selected_locales)}\n• Total Expanded Listings: {total_rows:,}\n\nSaved to:\n{path}\n\n🛡️ Logged into Enterprise Brand Enforcement Registry.",
                                parent=self)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export multi-locale file: {e}", parent=self)


# ══════════════════════════════════════════════════════════════════════════════
#  CONNECTED SELLER NETWORK & PHOTO SYNDICATE HUNTER MODAL
# ══════════════════════════════════════════════════════════════════════════════
class ConnectedNetworkModal(tk.Toplevel):
    """
    On-Demand Visual Syndicate & Connected Seller Hunter.
    Scans merchandising carousels on eBay listing pages and runs perceptual image hashing (dHash)
    to discover burner storefronts, competing listings, and connected counterfeit networks.
    """
    def __init__(self, parent, target_item: dict):
        super().__init__(parent)
        self.parent = parent
        self.target_item = target_item
        self.t = parent.theme
        self.discovered_items = []
        self.thumb_cache = {}
        self._sort_directions = {}
        
        self.title("🔗 Connected Seller Network & Photo Syndicate Hunter")
        self.geometry("1200x780")
        self.configure(bg=self.t["bg"])
        self.minsize(980, 620)
        self.parent._apply_dark_titlebar(self)
        
        # Center modal relative to parent window
        self.update_idletasks()
        p_x = parent.winfo_rootx()
        p_y = parent.winfo_rooty()
        p_w = parent.winfo_width()
        p_h = parent.winfo_height()
        w, h = 1200, 780
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.lift()
        self.focus_force()
        
        self._build_ui()
        self._start_network_scan()

    def _build_ui(self):
        t = self.t

        # ── 1. Top Target Reference Listing Card ──────────────────────────────
        hdr_frame = tk.Frame(self, bg=t["panel"], padx=16, pady=12, relief="flat", highlightbackground=t["border"], highlightthickness=1)
        hdr_frame.pack(side="top", fill="x", padx=12, pady=(12, 6))

        # Big Thumbnail preview container
        img_box = tk.Frame(hdr_frame, bg=t["entry_bg"], width=104, height=104, highlightbackground=t["border"], highlightthickness=1)
        img_box.pack_propagate(False)
        img_box.pack(side="left", padx=(0, 16))

        self.src_img_lbl = tk.Label(img_box, text="Loading\nPhoto...", bg=t["entry_bg"], fg=t["subtext"], font=FONT_SM)
        self.src_img_lbl.pack(fill="both", expand=True)
        self._load_source_image()

        info_box = tk.Frame(hdr_frame, bg=t["panel"])
        info_box.pack(side="left", fill="both", expand=True)

        badge_row = tk.Frame(info_box, bg=t["panel"])
        badge_row.pack(anchor="w", pady=(0, 4))
        
        tag_lbl = tk.Label(badge_row, text="🎯 TARGET REFERENCE LISTING", font=("Segoe UI", 8, "bold"), bg=t["accent"], fg="white", padx=8, pady=2)
        tag_lbl.pack(side="left", padx=(0, 8))

        brand_val = self.target_item.get("brand") or "General Brand"
        tk.Label(badge_row, text=f"Brand: {brand_val}", font=("Segoe UI", 8, "bold"), bg=t["entry_bg"], fg=t["subtext"], padx=8, pady=2).pack(side="left")

        title_lbl = tk.Label(info_box, text=self.target_item.get("title", "Unknown Title"), font=FONT_HEAD, bg=t["panel"], fg=t["text"], wraplength=820, justify="left")
        title_lbl.pack(anchor="w")

        seller_name = self.target_item.get("seller") or "Unknown Seller"
        price_val = self.target_item.get("price") or "N/A"
        item_id_val = self.target_item.get("item_id") or "N/A"
        sub_text = f"👤 Seller: {seller_name}    💰 Price: {price_val}    🆔 Item ID: {item_id_val}"
        sub_lbl = tk.Label(info_box, text=sub_text, font=FONT_SM, bg=t["panel"], fg=t["subtext"])
        sub_lbl.pack(anchor="w", pady=(4, 0))

        # ── 2. Status & Filter Bar ────────────────────────────────────────────
        self.status_frame = tk.Frame(self, bg=t["bg"], padx=14, pady=4)
        self.status_frame.pack(side="top", fill="x", padx=12)

        self.status_lbl = tk.Label(self.status_frame, text="🔍 Scanning eBay merchandising carousels and matching perceptual image hashes...", font=("Segoe UI", 9, "italic"), bg=t["bg"], fg=t["accent"])
        self.status_lbl.pack(side="left")

        self.pbar = ttk.Progressbar(self.status_frame, mode="indeterminate", length=180)
        self.pbar.pack(side="right", padx=(8, 0))
        self.pbar.start(12)

        # Filters toolbar
        f_row = tk.Frame(self, bg=t["panel"], padx=12, pady=5, relief="flat", highlightbackground=t["border"], highlightthickness=1)
        f_row.pack(side="top", fill="x", padx=12, pady=(2, 4))

        tk.Label(f_row, text="Thumbnails:", font=FONT_SM, bg=t["panel"], fg=t["subtext"]).pack(side="left", padx=(0, 4))
        self.thumb_size_var = tk.StringVar(value="Medium (96px)")
        self.thumb_size_combo = ttk.Combobox(f_row, textvariable=self.thumb_size_var, values=list(THUMB_CONFIG.keys()), width=14, state="readonly", font=FONT_SM)
        self.thumb_size_combo.pack(side="left", padx=(0, 10))
        self.thumb_size_combo.bind("<<ComboboxSelected>>", self._on_thumb_size_changed)

        tk.Label(f_row, text="Match Filter:", font=FONT_SM, bg=t["panel"], fg=t["subtext"]).pack(side="left", padx=(0, 4))
        self.match_filter_var = tk.StringVar(value="(All Discovered)")
        match_filters = ["(All Discovered)", "🎯 Exact & Near-Exact Photos Only", "🖼️ Visual Matches Only"]
        self.match_filter_combo = ttk.Combobox(f_row, textvariable=self.match_filter_var, values=match_filters, width=24, state="readonly", font=FONT_SM)
        self.match_filter_combo.pack(side="left", padx=(0, 10))
        self.match_filter_combo.bind("<<ComboboxSelected>>", lambda e: self._populate_tree())

        self.hide_same_seller_var = tk.BooleanVar(value=True)
        same_seller_cb = tk.Checkbutton(f_row, text="☐ Hide Same Seller", variable=self.hide_same_seller_var, command=self._populate_tree, bg=t["panel"], fg=t["text"], selectcolor=t["entry_bg"], activebackground=t["panel"], font=FONT_SM)
        same_seller_cb.pack(side="left", padx=(0, 8))

        self.hide_wl_var = tk.BooleanVar(value=True)
        wl_cb = tk.Checkbutton(f_row, text="🛡️ Hide Whitelisted Dealers", variable=self.hide_wl_var, command=self._populate_tree, bg=t["panel"], fg=t["text"], selectcolor=t["entry_bg"], activebackground=t["panel"], font=FONT_SM)
        wl_cb.pack(side="left", padx=(0, 8))

        self.hide_targeted_var = tk.BooleanVar(value=True)
        targeted_cb = tk.Checkbutton(f_row, text="🎯 Hide Targeted / Harvested", variable=self.hide_targeted_var, command=self._populate_tree, bg=t["panel"], fg=t["text"], selectcolor=t["entry_bg"], activebackground=t["panel"], font=FONT_SM)
        targeted_cb.pack(side="left", padx=(0, 8))

        # ── 3. Discovered Network Table (With Configurable Previews & Zero Overlap) ──
        table_frame = tk.Frame(self, bg=t["bg"])
        table_frame.pack(side="top", fill="both", expand=True, padx=12, pady=4)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        cols = ("similarity", "seller", "origin", "threat", "price", "title", "item_id")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="tree headings", selectmode="extended", style="Network.Treeview")

        style = ttk.Style()
        style.configure("Network.Treeview", background=t["entry_bg"], foreground=t["text"], fieldbackground=t["entry_bg"], rowheight=108, font=FONT_SM)
        style.configure("Network.Treeview.Heading", background=t["panel"], foreground=t["text"], font=("Segoe UI", 9, "bold"))
        style.map("Network.Treeview", background=[("selected", t["select_bg"])], foreground=[("selected", t["select_fg"])])

        self.tree.tag_configure("whitelisted", foreground=t["success"])
        self.tree.tag_configure("same_seller", foreground=t["accent2"])
        self.tree.tag_configure("targeted", foreground=t["subtext"])

        self.tree.heading("#0", text="Photo Preview", anchor="center")
        self.tree.column("#0", width=120, minwidth=100, anchor="center")

        self.col_cfg = {
            "similarity": ("Match Type / Visual Fingerprint", 185),
            "seller": ("Connected Seller", 140),
            "origin": ("Origin", 85),
            "threat": ("Threat Assessment", 175),
            "price": ("Price", 75),
            "title": ("Discovered Listing Title", 360),
            "item_id": ("Item ID", 105)
        }
        for c, (txt, w) in self.col_cfg.items():
            self.tree.heading(c, text=txt, command=lambda _c=c: self._sort_by_column(_c))
            self.tree.column(c, width=w, minwidth=50)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<Double-1>", self._open_selected_url)
        self.tree.bind("<Button-3>", self._show_row_context_menu)
        self.tree.bind("<Control-a>", self._select_all_rows)
        self.tree.bind("<Control-A>", self._select_all_rows)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ── 4. Action Toolbar ─────────────────────────────────────────────────
        btn_bar = tk.Frame(self, bg=t["panel"], padx=16, pady=12, relief="flat", highlightbackground=t["border"], highlightthickness=1)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(6, 12))

        self.count_var = tk.StringVar(value="0 connected listings discovered")
        count_lbl = tk.Label(btn_bar, textvariable=self.count_var, bg=t["panel"], fg=t["text"], font=FONT_HEAD)
        count_lbl.pack(side="left")

        tk.Button(btn_bar, text="✕ Close", command=self.destroy, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=12, pady=6, font=FONT_SM).pack(side="right", padx=4)
        tk.Button(btn_bar, text="📋 Copy Seller Handles", command=self._copy_sellers, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=12, pady=6, font=FONT_SM).pack(side="right", padx=4)
        tk.Button(btn_bar, text="🏪 Add to Stores Box", command=self._add_all_to_stores, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=12, pady=6, font=FONT_SM).pack(side="right", padx=4)
        tk.Button(btn_bar, text="📥 Add to Results Table", command=self._add_to_results, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=12, pady=6, font=FONT_SM).pack(side="right", padx=4)
        tk.Button(btn_bar, text="➕ Add Sellers to Target Queue", command=self._add_sellers_to_queue, bg=t["accent"], fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=16, pady=6).pack(side="right", padx=6)

    def _on_thumb_size_changed(self, event=None):
        size_name = self.thumb_size_var.get()
        cfg = THUMB_CONFIG.get(size_name, THUMB_CONFIG.get("Medium (100px)", {"rowheight": 110, "img_size": 100, "col_width": 116}))
        style = ttk.Style()
        style.configure("Network.Treeview", rowheight=cfg["rowheight"])
        img_size = cfg.get("img_size", 0)
        col_w = max(50, cfg.get("col_width", 116) + 10) if img_size > 0 else 50
        self.tree.column("#0", width=col_w, minwidth=40)
        self.thumb_cache.clear()
        self._populate_tree()

    def _select_all_rows(self, event=None):
        ch = self.tree.get_children()
        if ch:
            self.tree.selection_set(ch)
            self._on_tree_select()
        return "break"

    def _on_tree_select(self, event=None):
        sel_count = len(self.tree.selection())
        vis_count = len(self.tree.get_children())
        total_count = len(self.discovered_items)
        if sel_count > 0:
            self.count_var.set(f"{vis_count} listings shown ({sel_count} selected) | {total_count} discovered")
        else:
            self.count_var.set(f"{vis_count} listings shown | {total_count} discovered")

    def _load_source_image(self):
        url = self.target_item.get("image_url", "")
        if not url:
            tid = str(self.target_item.get("item_id", "")).strip()
            if tid and hasattr(self.parent, "results"):
                for r in self.parent.results:
                    if str(r.get("item_id", "")).strip() == tid and r.get("image_url"):
                        url = r.get("image_url")
                        break
        if not url:
            self.src_img_lbl.configure(text="No Photo\nAvailable")
            return

        def _w():
            try:
                if hasattr(self.parent, "raw_img_cache") and url in self.parent.raw_img_cache:
                    pimg = self.parent.raw_img_cache[url].copy()
                else:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    with urllib.request.urlopen(req, timeout=8) as r:
                        pimg = Image.open(io.BytesIO(r.read())).convert("RGBA")
                
                pimg.thumbnail((96, 96), Image.Resampling.LANCZOS)
                canvas = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
                canvas.paste(pimg, ((96 - pimg.width)//2, (96 - pimg.height)//2))
                photo = ImageTk.PhotoImage(canvas)
                self.thumb_cache["source"] = photo

                def _set():
                    self.src_img_lbl.configure(image=photo, text="")
                    self.src_img_lbl.image = photo
                self.after(0, _set)
            except Exception:
                self.after(0, lambda: self.src_img_lbl.configure(text="Photo\nUnavailable"))
        threading.Thread(target=_w, daemon=True).start()

    def _start_network_scan(self):
        def _worker():
            item_id = self.target_item.get("item_id", "")
            item_url = self.target_item.get("url", "")
            target_img = self.target_item.get("image_url", "")

            scraper = getattr(self.parent, "scraper", None)
            if not scraper:
                scraper = EbayScraper(headless=True)

            results = scraper.find_connected_network(item_id, item_url, target_img)
            self.discovered_items = results

            # Batch resolve seller countries in parallel
            unique_sellers = list(dict.fromkeys(r["seller"] for r in results if r.get("seller") and r.get("seller") not in ("Resolving...", "Unknown")))
            if unique_sellers and hasattr(self.parent, "data_store"):
                uncached = [s for s in unique_sellers if not self.parent.data_store.get_seller_intel(s).get("country")]
                if uncached:
                    resolved_intel = scraper.batch_resolve_seller_countries(uncached)
                    for s, data in resolved_intel.items():
                        c_val = data.get("country", "Unknown")
                        if c_val and c_val != "Unknown":
                            self.parent.data_store.set_seller_intel(s, c_val, member_since=data.get("member_since", ""))

            def _apply():
                self.pbar.stop()
                self.pbar.pack_forget()

                unique_sellers = set(r["seller"] for r in results if r.get("seller"))
                exact_matches = sum(1 for r in results if "Exact" in r.get("similarity", ""))
                wl_count = sum(1 for r in results if self.parent.data_store.is_seller_whitelisted(r.get("seller", "")))

                status_txt = f"✅ Scan Complete: {len(results)} connected listings found ({exact_matches} exact photo matches, {len(unique_sellers)} resolved sellers)"
                if wl_count > 0:
                    status_txt += f" | 🛡️ {wl_count} Whitelisted Dealer listings"
                self.status_lbl.configure(text=status_txt, fg=self.t["success"])

                self._populate_tree()

            self.after(0, _apply)
        threading.Thread(target=_worker, daemon=True).start()

    def _sort_by_column(self, col):
        """Sort discovered items by column and re-render tree."""
        if not self.discovered_items:
            return
        if not hasattr(self, "sort_directions"):
            self.sort_directions = {}
        descending = self.sort_directions.get(col, False)
        self.sort_directions[col] = not descending

        def get_sort_key(item):
            seller = (item.get("seller") or "").strip()
            if col == "origin":
                intel = self.parent.data_store.get_seller_intel(seller) if hasattr(self.parent, "data_store") else {}
                c_val = intel.get("country", "") if intel else ""
                assessment = self.parent.data_store.compute_threat_assessment(c_val, "") if hasattr(self.parent, "data_store") else {}
                return assessment.get("country", "Unknown").lower()
            elif col == "threat":
                intel = self.parent.data_store.get_seller_intel(seller) if hasattr(self.parent, "data_store") else {}
                c_val = intel.get("country", "") if intel else ""
                assessment = self.parent.data_store.compute_threat_assessment(c_val, "") if hasattr(self.parent, "data_store") else {}
                return assessment.get("score", 0)
            elif col == "price":
                m = re.search(r"[\d,]+(?:\.\d+)?", str(item.get("price", "")))
                if m:
                    try: return float(m.group(0).replace(",", ""))
                    except ValueError: return 0.0
                return 0.0
            elif col == "item_id":
                try: return int(item.get("item_id", 0))
                except ValueError: return 0
            elif col == "similarity":
                return str(item.get("similarity", "")).lower()
            elif col == "seller":
                return seller.lower()
            elif col == "title":
                return str(item.get("title", "")).lower()
            return str(item.get(col, "")).lower()

        self.discovered_items.sort(key=get_sort_key, reverse=descending)
        self._populate_tree()

        # Update headings with sort arrows
        for c, (txt, w) in self.col_cfg.items():
            if c == col:
                arrow = " ▼" if descending else " ▲"
                self.tree.heading(c, text=f"{txt}{arrow}", command=lambda _c=c: self._sort_by_column(_c))
            else:
                self.tree.heading(c, text=txt, command=lambda _c=c: self._sort_by_column(_c))

    def _populate_tree(self):
        """Render discovered items honoring current whitelist/same seller/match filters."""
        self.tree.delete(*self.tree.get_children())
        hide_wl = self.hide_wl_var.get()
        hide_same_seller = self.hide_same_seller_var.get()
        hide_targeted = self.hide_targeted_var.get()
        match_filter = self.match_filter_var.get()
        src_seller = (self.target_item.get("seller") or "").strip().lower()

        # Collect active targeted / queued / harvested store handles
        stores_in_input = set()
        if hasattr(self.parent, "store_text"):
            raw_text = self.parent.store_text.get("1.0", "end")
            placeholder = getattr(self.parent, "store_placeholder", "").strip()
            for line in raw_text.splitlines():
                l = line.strip().lower()
                if l and l != placeholder.lower():
                    lbl = self.parent._store_label(l).lower() if hasattr(self.parent, "_store_label") else l
                    stores_in_input.add(l)
                    stores_in_input.add(lbl)

        queued_stores = set()
        if hasattr(self.parent, "queue"):
            for q in self.parent.queue:
                s = q.get("store", "").strip().lower()
                if s:
                    lbl = self.parent._store_label(s).lower() if hasattr(self.parent, "_store_label") else s
                    queued_stores.add(s)
                    queued_stores.add(lbl)

        executed_stores = set()
        if hasattr(self.parent, "executed_jobs"):
            for ex in self.parent.executed_jobs:
                s = ex.get("store", "").strip().lower()
                if s:
                    lbl = self.parent._store_label(s).lower() if hasattr(self.parent, "_store_label") else s
                    executed_stores.add(s)
                    executed_stores.add(lbl)

        results_stores = set()
        if hasattr(self.parent, "results"):
            for it in self.parent.results:
                s = str(it.get("seller", "")).replace("🛡️", "").replace("(Authorized)", "").strip().lower()
                if s and s not in ("unknown", "resolving..."):
                    results_stores.add(s)

        targeted_or_harvested = stores_in_input | queued_stores | executed_stores | results_stores

        size_name = self.thumb_size_var.get()
        cfg = THUMB_CONFIG.get(size_name, THUMB_CONFIG.get("Medium (100px)", {"rowheight": 110, "img_size": 100, "col_width": 116}))
        img_size = cfg.get("img_size", 0)
        show_images = img_size > 0

        shown_count = 0
        for itm in self.discovered_items:
            seller = (itm.get("seller") or "Unknown").strip()
            seller_clean = seller.lower()
            is_wl = self.parent.data_store.is_seller_whitelisted(seller) if hasattr(self.parent, "data_store") else False
            is_same = bool(src_seller and seller_clean == src_seller)
            is_targeted_or_harvested = bool(seller_clean in targeted_or_harvested)

            if hide_wl and is_wl:
                continue
            if hide_same_seller and is_same:
                continue
            if hide_targeted and is_targeted_or_harvested and not is_same:
                continue

            sim_txt = itm.get("similarity", "Related Listing")
            if "Exact" in match_filter and "Exact" not in sim_txt:
                continue
            if "Visual" in match_filter and not any(k in sim_txt for k in ("Exact", "Visual", "Near-Exact")):
                continue

            if is_wl:
                seller_display = f"🛡️ {seller} (Authorized)"
            elif is_same:
                seller_display = f"🏠 {seller} (Source Seller)"
            elif is_targeted_or_harvested:
                seller_display = f"🎯 {seller} (Targeted/Harvested)"
            else:
                seller_display = f"⚡ {seller}"

            # Evaluate Threat Intel from DataStore
            cached_intel = self.parent.data_store.get_seller_intel(seller) if hasattr(self.parent, "data_store") else {}
            seller_country = cached_intel.get("country", "") if cached_intel else ""
            assessment = self.parent.data_store.compute_threat_assessment(seller_country, "") if hasattr(self.parent, "data_store") else {}
            orig_txt = f"{assessment.get('flag', '❓')} {assessment.get('country', 'Unknown')}" if assessment.get('country') != 'Unknown' else "❓ Unresolved"
            threat_txt = assessment.get("badge", "Unresolved")

            img_url = itm.get("image_url", "")
            img_to_use = self.thumb_cache.get(img_url) if show_images else None

            tags = []
            if is_wl: tags.append("whitelisted")
            elif is_same: tags.append("same_seller")
            elif is_targeted_or_harvested: tags.append("targeted")

            iid = self.tree.insert("", "end", text="", image=img_to_use if img_to_use else "", values=(
                sim_txt,
                seller_display,
                orig_txt,
                threat_txt,
                itm.get("price", ""),
                itm.get("title", ""),
                itm.get("item_id", "")
            ), tags=tuple(tags))

            if show_images and img_url and img_url not in self.thumb_cache:
                self._fetch_thumb(iid, img_url, img_size)

            shown_count += 1

        self.count_var.set(f"{shown_count} listings shown | {len(self.discovered_items)} discovered")

    def _fetch_thumb(self, iid, url, size):
        """Asynchronously download and scale thumbnail with retry loop."""
        def _w():
            for attempt in range(2):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    with urllib.request.urlopen(req, timeout=7) as r:
                        pimg = Image.open(io.BytesIO(r.read())).convert("RGBA")
                    pimg.thumbnail((size, size), Image.Resampling.LANCZOS)
                    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                    canvas.paste(pimg, ((size - pimg.width)//2, (size - pimg.height)//2))
                    photo = ImageTk.PhotoImage(canvas)
                    self.thumb_cache[url] = photo
                    self.after(0, lambda: self.tree.exists(iid) and self.tree.item(iid, image=photo))
                    break
                except Exception:
                    if attempt == 0:
                        time.sleep(0.3)
        threading.Thread(target=_w, daemon=True).start()

    def _open_selected_url(self, event=None):
        sel = self.tree.focus()
        if not sel:
            selected = self.tree.selection()
            if selected: sel = selected[0]
        if sel:
            vals = self.tree.item(sel)["values"]
            if len(vals) > 6:
                item_id = str(vals[6]).strip()
                if item_id:
                    webbrowser.open(f"https://www.ebay.com/itm/{item_id}")
            elif len(vals) > 4:
                item_id = str(vals[4]).strip()
                if item_id:
                    webbrowser.open(f"https://www.ebay.com/itm/{item_id}")

    def _show_row_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            if row_id not in self.tree.selection():
                self.tree.selection_set(row_id)
            self.tree.focus(row_id)
        if not self.tree.selection(): return
        
        t = self.t
        menu = tk.Menu(self, tearoff=0, bg=t["panel"], fg=t["text"], activebackground=t["accent"], activeforeground="white")
        menu.add_command(label="➕ Add This Seller to Target Queue", command=self._add_single_seller_to_queue)
        menu.add_command(label="🏪 Add This Seller to Stores Box", command=self._add_single_seller_to_stores)
        menu.add_command(label="🛡️ Whitelist This Seller (Authorized Dealer)", command=self._whitelist_selected_row_seller)
        menu.add_command(label="🌍 🚨 Resolve Origin & Threat Intel", command=self._resolve_selected_row_threat_intel)
        menu.add_separator()
        menu.add_command(label="☑️ Select All (Ctrl+A)", command=self._select_all_rows)
        menu.add_command(label="🌐 Open in Browser", command=self._open_selected_url)
        menu.add_command(label="📋 Copy Listing URL", command=self._copy_selected_row_url)
        menu.add_command(label="👤 Copy Seller Username", command=self._copy_selected_row_seller)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _clean_seller_handle(self, text: str) -> str:
        """Strip badges, emojis, and status suffixes to extract pure seller username."""
        if not text:
            return ""
        s = str(text)
        for prefix in ("🛡️", "🏠", "🎯", "⚡", "❓", "🚨", "👤", "🏪"):
            s = s.replace(prefix, "")
        for suffix in ("(Authorized)", "(Source Seller)", "(Targeted/Harvested)", "(Targeted)", "(Harvested)"):
            s = s.replace(suffix, "")
        return s.strip()

    def _resolve_selected_row_threat_intel(self):
        sel = self.tree.focus()
        if not sel:
            selected = self.tree.selection()
            if selected: sel = selected[0]
        if not sel: return
        vals = self.tree.item(sel)["values"]
        seller_raw = vals[1] if len(vals) > 1 else ""
        seller_handle = self._clean_seller_handle(seller_raw)
        if not seller_handle or seller_handle in ("Resolving...", "Unknown"):
            return

        def _w():
            scraper = getattr(self.parent, "scraper", None)
            if scraper:
                res = scraper.batch_resolve_seller_countries([seller_handle])
                if seller_handle in res:
                    c_val = res[seller_handle].get("country", "Unknown")
                    m_since = res[seller_handle].get("member_since", "")
                    self.parent.data_store.set_seller_intel(seller_handle, c_val, member_since=m_since)
            self.after(0, self._populate_tree)
        threading.Thread(target=_w, daemon=True).start()

    def _copy_selected_row_url(self):
        sel = self.tree.focus()
        if not sel:
            selected = self.tree.selection()
            if selected: sel = selected[0]
        if sel:
            vals = self.tree.item(sel)["values"]
            item_id = str(vals[6]).strip() if len(vals) > 6 else (str(vals[4]).strip() if len(vals) > 4 else "")
            if item_id:
                url = f"https://www.ebay.com/itm/{item_id}"
                self.clipboard_clear()
                self.clipboard_append(url)
                self.count_var.set(f"📋 Copied listing URL: {url}")
                self.parent._log(f"📋 Copied URL to clipboard: {url}")

    def _copy_selected_row_seller(self):
        sel = self.tree.focus()
        if not sel:
            selected = self.tree.selection()
            if selected: sel = selected[0]
        if sel:
            vals = self.tree.item(sel)["values"]
            seller_raw = vals[1] if len(vals) > 1 else ""
            seller_handle = self._clean_seller_handle(seller_raw)
            if seller_handle and seller_handle not in ("Resolving...", "Unknown"):
                self.clipboard_clear()
                self.clipboard_append(seller_handle)
                self.count_var.set(f"👤 Copied seller handle: '{seller_handle}'")
                self.parent._log(f"👤 Copied seller handle to clipboard: {seller_handle}")
            else:
                self.count_var.set("⚠️ No valid seller username on this listing.")

    def _whitelist_selected_row_seller(self):
        sel = self.tree.focus()
        if not sel:
            selected = self.tree.selection()
            if selected: sel = selected[0]
        if sel:
            vals = self.tree.item(sel)["values"]
            seller_raw = vals[1] if len(vals) > 1 else ""
            seller_handle = self._clean_seller_handle(seller_raw)
            if not seller_handle or seller_handle in ("Resolving...", "Unknown"):
                self.count_var.set("⚠️ No valid seller handle to whitelist.")
                return
            if self.parent.data_store.is_seller_whitelisted(seller_handle):
                self.count_var.set(f"🛡️ '{seller_handle}' is already Whitelisted.")
                return
            d_name = simpledialog.askstring("Authorized Dealership", f"Enter Dealership Name for '{seller_handle}' (optional):", initialvalue="Authorized Dealership", parent=self)
            if d_name is None:
                self.lift()
                return
            notes = simpledialog.askstring("Analyst Notes", f"Notes for '{seller_handle}' (optional):", initialvalue="Client Approved Whitelist", parent=self) or ""
            b_val = self.target_item.get("brand") or "General / All Brands"
            self.parent.data_store.add_to_whitelist(seller_handle, brand=b_val, dealer_name=d_name, notes=notes)
            self.parent._log(f"🛡️ Added '{seller_handle}' to Authorized Whitelist ({b_val}).")
            self.count_var.set(f"🛡️ Whitelisted '{seller_handle}' ({b_val})!")
            self._populate_tree()
            self.lift()

    def _sort_by_column(self, col):
        """Sort discovered items by column and re-render tree."""
        if not self.discovered_items:
            return
        if not hasattr(self, "sort_directions"):
            self.sort_directions = {}
        descending = self.sort_directions.get(col, False)
        self.sort_directions[col] = not descending

        def get_sort_key(item):
            seller = (item.get("seller") or "").strip()
            if col == "origin":
                intel = self.parent.data_store.get_seller_intel(seller) if hasattr(self.parent, "data_store") else {}
                c_val = intel.get("country", "") if intel else ""
                assessment = self.parent.data_store.compute_threat_assessment(c_val, "") if hasattr(self.parent, "data_store") else {}
                return assessment.get("country", "Unknown").lower()
            elif col == "threat":
                intel = self.parent.data_store.get_seller_intel(seller) if hasattr(self.parent, "data_store") else {}
                c_val = intel.get("country", "") if intel else ""
                assessment = self.parent.data_store.compute_threat_assessment(c_val, "") if hasattr(self.parent, "data_store") else {}
                return assessment.get("score", 0)
            elif col == "price":
                m = re.search(r"[\d,]+(?:\.\d+)?", str(item.get("price", "")))
                if m:
                    try: return float(m.group(0).replace(",", ""))
                    except ValueError: return 0.0
                return 0.0
            elif col == "item_id":
                try: return int(item.get("item_id", 0))
                except ValueError: return 0
            elif col == "similarity":
                return str(item.get("similarity", "")).lower()
            elif col == "seller":
                return seller.lower()
            elif col == "title":
                return str(item.get("title", "")).lower()
            return str(item.get(col, "")).lower()

        self.discovered_items.sort(key=get_sort_key, reverse=descending)
        self._populate_tree()

        # Update headings with sort arrows
        for c, (txt, w) in self.col_cfg.items():
            if c == col:
                arrow = " ▼" if descending else " ▲"
                self.tree.heading(c, text=f"{txt}{arrow}", command=lambda _c=c: self._sort_by_column(_c))
            else:
                self.tree.heading(c, text=txt, command=lambda _c=c: self._sort_by_column(_c))

    def _append_to_parent_stores(self, seller_handle: str):
        """Append seller handle to the main Stores/Sellers input box without fusion or duplicates."""
        parent = self.parent
        if not hasattr(parent, "store_text"):
            return
        curr = parent.store_text.get("1.0", "end").strip()
        ph = getattr(parent, "store_placeholder", "").strip()
        if not curr or curr == ph:
            parent.store_text.delete("1.0", "end")
            parent.store_text.insert("1.0", seller_handle + "\n")
            parent.store_text.config(fg=parent.theme["text"])
        else:
            lines = [l.strip() for l in curr.splitlines() if l.strip()]
            existing_lowers = [l.lower() for l in lines]
            if seller_handle.lower() not in existing_lowers:
                lines.append(seller_handle)
                parent.store_text.delete("1.0", "end")
                parent.store_text.insert("1.0", "\n".join(lines) + "\n")
                parent.store_text.config(fg=parent.theme["text"])

    def _add_single_seller_to_stores(self):
        """Add highlighted seller(s) in tree directly to Stores text box (supports multi-select)."""
        selected_iids = self.tree.selection()
        if not selected_iids:
            sel = self.tree.focus()
            if sel:
                selected_iids = [sel]
        if not selected_iids:
            self.count_var.set("⚠️ No listing selected.")
            return

        sellers = []
        for iid in selected_iids:
            vals = self.tree.item(iid)["values"]
            seller_raw = vals[1] if len(vals) > 1 else ""
            seller_handle = self._clean_seller_handle(seller_raw)
            if seller_handle and seller_handle not in ("Resolving...", "Unknown"):
                sellers.append(seller_handle)

        unique_sellers = list(dict.fromkeys(sellers))
        if not unique_sellers:
            self.count_var.set("⚠️ No valid seller handles to add.")
            return

        for s in unique_sellers:
            self._append_to_parent_stores(s)

        if len(unique_sellers) == 1:
            self.count_var.set(f"🏪 Added '{unique_sellers[0]}' to Stores box!")
            self.parent._log(f"🏪 Added connected seller '{unique_sellers[0]}' to Stores box.")
        else:
            self.count_var.set(f"🏪 Added {len(unique_sellers)} selected seller(s) to Stores box!")
            self.parent._log(f"🏪 Added {len(unique_sellers)} connected seller(s) to Stores box: {', '.join(unique_sellers)}")

    def _add_all_to_stores(self):
        """Append all discovered / selected seller handles directly to main Stores/Sellers input."""
        selected_iids = self.tree.selection()
        sellers = []
        if selected_iids:
            for iid in selected_iids:
                vals = self.tree.item(iid)["values"]
                s_clean = self._clean_seller_handle(vals[1]) if len(vals) > 1 else ""
                if s_clean and s_clean not in ("Resolving...", "Unknown"):
                    sellers.append(s_clean)
        else:
            for r in self.discovered_items:
                s = r.get("seller")
                if s and s not in ("Resolving...", "Unknown"):
                    sellers.append(s)

        unique_sellers = list(dict.fromkeys(sellers))
        if not unique_sellers:
            self.count_var.set("⚠️ No resolved seller handles to add.")
            return

        for s in unique_sellers:
            self._append_to_parent_stores(s)

        self.count_var.set(f"🏪 Added {len(unique_sellers)} seller(s) to Stores box!")
        self.parent._log(f"🏪 Added {len(unique_sellers)} connected seller(s) to Stores box: {', '.join(unique_sellers)}")

    def _add_single_seller_to_queue(self):
        """Add highlighted seller(s) in tree to the Target Queue (supports multi-select)."""
        selected_iids = self.tree.selection()
        if not selected_iids:
            sel = self.tree.focus()
            if sel:
                selected_iids = [sel]
        if not selected_iids:
            self.count_var.set("⚠️ No listing selected.")
            return

        sellers = []
        for iid in selected_iids:
            vals = self.tree.item(iid)["values"]
            seller_raw = vals[1] if len(vals) > 1 else ""
            seller_handle = self._clean_seller_handle(seller_raw)
            if seller_handle and seller_handle not in ("Resolving...", "Unknown"):
                sellers.append(seller_handle)

        unique_sellers = list(dict.fromkeys(sellers))
        if not unique_sellers:
            self.count_var.set("⚠️ No valid seller handle to enqueue.")
            return

        parent = self.parent
        whitelisted = [s for s in unique_sellers if parent.data_store.is_seller_whitelisted(s)]
        if whitelisted:
            wl_msg = f"{len(whitelisted)} selected seller(s) are on your Authorized Whitelist:\n{', '.join(whitelisted)}\n\nDo you really want to target them?"
            if not messagebox.askyesno("Whitelisted Seller", wl_msg, parent=self):
                unique_sellers = [s for s in unique_sellers if s not in whitelisted]
                self.lift()
                if not unique_sellers:
                    return

        # 1. Check targeted brands in Brand Library / Presets
        target_brands = [k.split("/")[0] for k, v in parent.brand_states.items() if v == "target"]
        target_brands = list(dict.fromkeys(target_brands))
        if not target_brands:
            target_brands = [self.target_item.get("brand") or "General Brand"]

        custom_includes = [l.strip() for l in parent.include_text.get("1.0", "end").splitlines() if l.strip()]
        generic_excludes = parent._get_active_exclusions() if hasattr(parent, "_get_active_exclusions") else []
        condition = parent.condition_var.get() if hasattr(parent, "condition_var") else "all"

        market = parent.marketplace_var.get() if hasattr(parent, "marketplace_var") else "eBay"
        if "Wish" in market:
            platform_name = "Wish"
        elif "Temu" in market:
            platform_name = "Temu"
        elif "AliExpress" in market:
            platform_name = "AliExpress"
        elif "Printerval" in market:
            platform_name = "Printerval"
        elif "Redbubble" in market:
            platform_name = "Redbubble"
        elif "Mercado" in market:
            platform_name = "Mercado Libre"
        else:
            platform_name = "eBay"

        added_count = 0
        skipped_executed = 0
        for s in unique_sellers:
            self._append_to_parent_stores(s)
            for b_name in target_brands:
                if any(q.get("store", "").strip().lower() == s.strip().lower() and 
                       q.get("brand", "").strip().lower() == b_name.strip().lower() and 
                       q.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for q in parent.queue):
                    continue
                if any(ex.get("store", "").strip().lower() == s.strip().lower() and 
                       ex.get("brand", "").strip().lower() == b_name.strip().lower() and 
                       ex.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for ex in parent.executed_jobs):
                    skipped_executed += 1
                    parent._log(f"ℹ️ Skipped already-completed search on {platform_name}: [{parent._store_label(s, platform=platform_name)} ▸ {b_name}]")
                    continue

                b_terms = [k.split("/")[-1] for k, v in parent.brand_states.items() if v == "target" and k.split("/")[0] == b_name]
                includes = b_terms if b_terms else (custom_includes if custom_includes else [self.target_item.get("product_type") or b_name.lower()])

                entry = {
                    "store": s,
                    "brand": b_name,
                    "marketplace": platform_name,
                    "includes": list(includes),
                    "excludes": list(generic_excludes),
                    "condition": condition
                }
                parent.queue.append(entry)
                lbl = f"{parent._store_label(s, platform=platform_name)} ▸ {b_name} ({len(includes)} terms | {len(generic_excludes)} excl)"
                parent.queue_list.insert("end", lbl)
                added_count += 1

        if added_count > 0:
            if len(unique_sellers) == 1:
                parent._log(f"🎯 Queued connected seller '{unique_sellers[0]}' for {added_count} brand job(s) on {platform_name}.")
                self.count_var.set(f"🎯 Enqueued '{unique_sellers[0]}' for {added_count} brand(s) [{platform_name}]!")
            else:
                parent._log(f"🎯 Enqueued {added_count} batch jobs across {len(unique_sellers)} selected sellers on {platform_name}.")
                self.count_var.set(f"🎯 Enqueued {added_count} job(s) for {len(unique_sellers)} selected seller(s) [{platform_name}]!")
        else:
            self.count_var.set(f"ℹ️ Selected seller(s) already queued or previously executed.")

    def _copy_sellers(self):
        selected_iids = self.tree.selection()
        sellers = []
        if selected_iids:
            for iid in selected_iids:
                vals = self.tree.item(iid)["values"]
                s_clean = self._clean_seller_handle(vals[1]) if len(vals) > 1 else ""
                if s_clean and s_clean not in ("Resolving...", "Unknown"):
                    sellers.append(s_clean)
        else:
            for r in self.discovered_items:
                s = r.get("seller")
                if s and s not in ("Resolving...", "Unknown"):
                    sellers.append(s)

        unique_sellers = list(dict.fromkeys(sellers))
        if not unique_sellers:
            self.count_var.set("⚠️ No resolved seller handles to copy.")
            return
        text = ", ".join(unique_sellers)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.count_var.set(f"📋 Copied {len(unique_sellers)} seller handles to clipboard!")
        self.parent._log(f"📋 Copied {len(unique_sellers)} seller handles to clipboard: {text}")

    def _add_to_results(self):
        selected_iids = self.tree.selection()
        target_records = []
        if selected_iids:
            for iid in selected_iids:
                vals = self.tree.item(iid)["values"]
                for r in self.discovered_items:
                    target_id = str(vals[6]).strip() if len(vals) > 6 else (str(vals[4]).strip() if len(vals) > 4 else "")
                    if target_id and str(r.get("item_id")) == target_id:
                        target_records.append(r)
                        break
        else:
            target_records = self.discovered_items

        added = 0
        brand_name = self.target_item.get("brand", "General Sweep")
        ptype = self.target_item.get("product_type", "")
        for itm in target_records:
            row = {
                "brand": brand_name,
                "product_type": ptype,
                "title": itm.get("title", ""),
                "item_id": str(itm.get("item_id", "")),
                "price": itm.get("price", ""),
                "seller": itm.get("seller", ""),
                "location": "",
                "image_url": itm.get("image_url", ""),
                "url": itm.get("url", f"https://www.ebay.com/itm/{itm.get('item_id', '')}"),
                "marketplace": "eBay (Network Discovery)"
            }
            if row["item_id"] and row["item_id"] not in self.parent.seen_item_ids:
                self.parent.seen_item_ids.add(row["item_id"])
                self.parent.results.append(row)
                added += 1

        if hasattr(self.parent, "_repopulate_results_table"):
            self.parent._repopulate_results_table()
        if hasattr(self.parent, "_log"):
            self.parent._log(f"🔗 Added {added} discovered network listings to Results table.")
        self.count_var.set(f"✓ Added {added} discovered listings to Results!")

    def _add_sellers_to_queue(self):
        selected_iids = self.tree.selection()
        sellers = []
        if selected_iids:
            for iid in selected_iids:
                vals = self.tree.item(iid)["values"]
                s_clean = self._clean_seller_handle(vals[1]) if len(vals) > 1 else ""
                if s_clean and s_clean not in ("Resolving...", "Unknown"):
                    sellers.append(s_clean)
        else:
            for r in self.discovered_items:
                s = r.get("seller")
                if s and s not in ("Resolving...", "Unknown"):
                    sellers.append(s)

        unique_sellers = list(dict.fromkeys(sellers))
        if not unique_sellers:
            self.count_var.set("⚠️ No resolved seller handles to enqueue.")
            return

        parent = self.parent
        eligible_sellers = [s for s in unique_sellers if not parent.data_store.is_seller_whitelisted(s)]
        skipped_count = len(unique_sellers) - len(eligible_sellers)

        if not eligible_sellers:
            self.count_var.set(f"🛡️ All {len(unique_sellers)} sellers are Authorized Dealerships (Skipped).")
            return

        # Check targeted brands in Brand Library
        target_brands = [k.split("/")[0] for k, v in parent.brand_states.items() if v == "target"]
        target_brands = list(dict.fromkeys(target_brands))
        if not target_brands:
            target_brands = [self.target_item.get("brand") or "General Brand"]

        custom_includes = [l.strip() for l in parent.include_text.get("1.0", "end").splitlines() if l.strip()]
        generic_excludes = parent._get_active_exclusions() if hasattr(parent, "_get_active_exclusions") else []
        condition = parent.condition_var.get() if hasattr(parent, "condition_var") else "all"

        market = parent.marketplace_var.get() if hasattr(parent, "marketplace_var") else "eBay"
        if "Wish" in market:
            platform_name = "Wish"
        elif "Temu" in market:
            platform_name = "Temu"
        elif "AliExpress" in market:
            platform_name = "AliExpress"
        elif "Printerval" in market:
            platform_name = "Printerval"
        elif "Redbubble" in market:
            platform_name = "Redbubble"
        elif "Mercado" in market:
            platform_name = "Mercado Libre"
        else:
            platform_name = "eBay"

        added_count = 0
        skipped_executed = 0
        for s in eligible_sellers:
            self._append_to_parent_stores(s)
            for b_name in target_brands:
                if any(q.get("store", "").strip().lower() == s.strip().lower() and 
                       q.get("brand", "").strip().lower() == b_name.strip().lower() and 
                       q.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for q in parent.queue):
                    continue
                if any(ex.get("store", "").strip().lower() == s.strip().lower() and 
                       ex.get("brand", "").strip().lower() == b_name.strip().lower() and 
                       ex.get("marketplace", "eBay").lower() == platform_name.lower() 
                       for ex in parent.executed_jobs):
                    skipped_executed += 1
                    continue
                b_terms = [k.split("/")[-1] for k, v in parent.brand_states.items() if v == "target" and k.split("/")[0] == b_name]
                includes = b_terms if b_terms else (custom_includes if custom_includes else [self.target_item.get("product_type") or b_name.lower()])

                entry = {
                    "store": s,
                    "brand": b_name,
                    "marketplace": platform_name,
                    "includes": list(includes),
                    "excludes": list(generic_excludes),
                    "condition": condition
                }
                parent.queue.append(entry)
                lbl = f"{parent._store_label(s, platform=platform_name)} ▸ {b_name} ({len(includes)} terms | {len(generic_excludes)} excl)"
                parent.queue_list.insert("end", lbl)
                added_count += 1

        msg = f"Enqueued {added_count} job(s) for {len(eligible_sellers)} seller(s)"
        if skipped_count > 0:
            msg += f" (Shielded {skipped_count} Whitelisted Dealers)"
        if skipped_executed > 0:
            msg += f" (Skipped {skipped_executed} already-completed searches)"
        parent._log(f"🎯 Enqueued {added_count} batch jobs across {len(eligible_sellers)} sellers on {platform_name} (Shielded {skipped_count} whitelisted dealers, skipped {skipped_executed} already run).")
        self.count_var.set(f"🎯 {msg}")


# ══════════════════════════════════════════════════════════════════════════════
#  AUTHORIZED DEALERS & MERCHANT WHITELIST MANAGER
# ══════════════════════════════════════════════════════════════════════════════
class WhitelistManagerModal(tk.Toplevel):
    """
    Authorized Dealer & Client Approved Merchant Whitelist Manager.
    Allows analysts to maintain persistent lists of authorized storefronts,
    bulk import dealership lists from client emails/Excel, and auto-shield
    legitimate distributors from false-positive scraping and enforcement.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.t = parent.theme
        self.data_store = parent.data_store
        
        self.title("🛡️ Authorized Dealers & Merchant Whitelist Manager")
        self.geometry("980x640")
        self.configure(bg=self.t["bg"])
        self.minsize(800, 500)
        self.parent._apply_dark_titlebar(self)
        
        # Center modal relative to parent window
        self.update_idletasks()
        p_x = parent.winfo_rootx()
        p_y = parent.winfo_rooty()
        p_w = parent.winfo_width()
        p_h = parent.winfo_height()
        w, h = 980, 640
        x = p_x + (p_w - w) // 2
        y = p_y + (p_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.lift()
        self.focus_force()
        
        self._build_ui()
        self._refresh_table()

    def _build_ui(self):
        t = self.t

        # ── 1. Top Header Card ────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=t["panel"], padx=16, pady=12, relief="flat", highlightbackground=t["border"], highlightthickness=1)
        hdr.pack(side="top", fill="x", padx=12, pady=(12, 6))

        title_row = tk.Frame(hdr, bg=t["panel"])
        title_row.pack(fill="x")
        
        tk.Label(title_row, text="🛡️ AUTHORIZED DEALERS & CLIENT APPROVED WHITELIST", font=("Segoe UI", 11, "bold"), bg=t["panel"], fg=t["accent"]).pack(side="left")
        self.stat_lbl = tk.Label(title_row, text="0 Authorized Dealers Registered", font=("Segoe UI", 9, "bold"), bg=t["entry_bg"], fg=t["success"], padx=8, pady=2)
        self.stat_lbl.pack(side="right")

        desc_lbl = tk.Label(hdr, text="Whitelisted dealers and storefronts are automatically shielded across all scrapers, threat intel modules, and syndicate hunters to prevent false-positive enforcement.", font=FONT_SM, bg=t["panel"], fg=t["subtext"])
        desc_lbl.pack(anchor="w", pady=(4, 0))

        # ── 2. Filter & Search Toolbar ────────────────────────────────────────
        filter_bar = tk.Frame(self, bg=t["bg"], padx=4, pady=4)
        filter_bar.pack(side="top", fill="x", padx=12, pady=(2, 6))

        tk.Label(filter_bar, text="🔍 Search / Filter:", bg=t["bg"], fg=t["text"], font=FONT_SM).pack(side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_table())
        search_entry = tk.Entry(filter_bar, textvariable=self.search_var, bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"], width=28, font=FONT_SM)
        search_entry.pack(side="left", padx=(0, 12))

        tk.Label(filter_bar, text="Portfolio Brand:", bg=t["bg"], fg=t["text"], font=FONT_SM).pack(side="left", padx=(0, 4))
        self.brand_filter_var = tk.StringVar(value="All Brands")
        brands_list = ["All Brands"] + sorted(list(self.data_store.get_brands().keys()))
        self.brand_combo = ttk.Combobox(filter_bar, textvariable=self.brand_filter_var, values=brands_list, state="readonly", width=18, font=FONT_SM)
        self.brand_combo.pack(side="left", padx=(0, 4))
        self.brand_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_table())

        # ── 3. Whitelist Treeview ─────────────────────────────────────────────
        table_frame = tk.Frame(self, bg=t["bg"])
        table_frame.pack(side="top", fill="both", expand=True, padx=12, pady=4)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        cols = ("seller", "brand", "dealer_name", "notes", "added_at")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="extended", style="Whitelist.Treeview")

        style = ttk.Style()
        style.configure("Whitelist.Treeview", background=t["entry_bg"], foreground=t["text"], fieldbackground=t["entry_bg"], rowheight=28, font=FONT_SM)
        style.configure("Whitelist.Treeview.Heading", background=t["panel"], foreground=t["text"], font=("Segoe UI", 9, "bold"))
        style.map("Whitelist.Treeview", background=[("selected", t["select_bg"])], foreground=[("selected", t["select_fg"])])

        col_cfg = {
            "seller": ("Seller Handle / Store Slug", 180),
            "brand": ("Brand Portfolio", 140),
            "dealer_name": ("Dealership / Entity Name", 220),
            "notes": ("Analyst Notes", 240),
            "added_at": ("Date Added", 130)
        }
        for c, (txt, w) in col_cfg.items():
            self.tree.heading(c, text=txt)
            self.tree.column(c, width=w, minwidth=80)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<Button-3>", self._show_context_menu)

        # ── 4. Bottom Action Toolbar ──────────────────────────────────────────
        btn_bar = tk.Frame(self, bg=t["panel"], padx=16, pady=12, relief="flat", highlightbackground=t["border"], highlightthickness=1)
        btn_bar.pack(side="bottom", fill="x", padx=12, pady=(6, 12))

        tk.Button(btn_bar, text="➕ Add Dealer", command=self._add_dealer_dialog, bg=t["accent"], fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=14, pady=6).pack(side="left", padx=(0, 6))
        tk.Button(btn_bar, text="📋 Bulk Import List", command=self._bulk_import_dialog, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=12, pady=6, font=FONT_SM).pack(side="left", padx=4)
        tk.Button(btn_bar, text="🗑️ Remove Selected", command=self._remove_selected, bg=t["entry_bg"], fg=t["danger"], relief="flat", padx=12, pady=6, font=FONT_SM).pack(side="left", padx=4)
        tk.Button(btn_bar, text="💾 Export CSV", command=self._export_csv, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=12, pady=6, font=FONT_SM).pack(side="left", padx=4)
        tk.Button(btn_bar, text="✕ Close", command=self.destroy, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=14, pady=6, font=FONT_SM).pack(side="right")

    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        wl = self.data_store.get_whitelist()
        q = self.search_var.get().lower().strip()
        brand_filter = self.brand_filter_var.get()

        total = len(wl)
        shown = 0

        for handle, data in sorted(wl.items()):
            b = data.get("brand", "")
            d_name = data.get("dealer_name", "")
            notes = data.get("notes", "")
            date = data.get("added_at", "")

            # Filter logic
            if brand_filter != "All Brands" and b.lower() != brand_filter.lower():
                continue
            if q and not any(q in str(x).lower() for x in (handle, b, d_name, notes)):
                continue

            self.tree.insert("", "end", values=(handle, b, d_name, notes, date))
            shown += 1

        self.stat_lbl.config(text=f"{total} Authorized Dealers Registered ({shown} shown)")

    def _show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
        if not self.tree.selection(): return
        
        t = self.t
        menu = tk.Menu(self, tearoff=0, bg=t["panel"], fg=t["text"], activebackground=t["accent"], activeforeground="white")
        menu.add_command(label="🗑️ Remove from Whitelist", command=self._remove_selected)
        menu.add_command(label="📋 Copy Seller Handle", command=self._copy_selected_handle)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _copy_selected_handle(self):
        sel = self.tree.selection()
        if sel:
            handle = self.tree.item(sel[0])["values"][0]
            self.clipboard_clear()
            self.clipboard_append(handle)

    def _add_dealer_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("➕ Add Authorized Dealership")
        dlg.geometry("460x340")
        dlg.configure(bg=self.t["bg"])
        dlg.transient(self)
        dlg.grab_set()
        self.parent._apply_dark_titlebar(dlg)

        t = self.t
        f = tk.Frame(dlg, bg=t["panel"], padx=16, pady=16)
        f.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(f, text="Seller Handle / Store URL:", bg=t["panel"], fg=t["text"], font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        h_entry = tk.Entry(f, bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"], font=FONT_SM, width=32)
        h_entry.grid(row=0, column=1, sticky="w", pady=4)
        h_entry.focus_set()

        tk.Label(f, text="Brand Portfolio:", bg=t["panel"], fg=t["text"], font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        brands = ["General / All Brands"] + sorted(list(self.data_store.get_brands().keys()))
        b_combo = ttk.Combobox(f, values=brands, font=FONT_SM, width=30)
        b_combo.grid(row=1, column=1, sticky="w", pady=4)
        b_combo.set("Toyota")

        tk.Label(f, text="Dealership / Entity Name:", bg=t["panel"], fg=t["text"], font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        d_entry = tk.Entry(f, bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"], font=FONT_SM, width=32)
        d_entry.grid(row=2, column=1, sticky="w", pady=4)

        tk.Label(f, text="Analyst Notes:", bg=t["panel"], fg=t["text"], font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        n_entry = tk.Entry(f, bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"], font=FONT_SM, width=32)
        n_entry.grid(row=3, column=1, sticky="w", pady=4)

        def _save():
            handle = h_entry.get().strip()
            if not handle:
                messagebox.showwarning("Missing Handle", "Please enter a seller handle or store URL.", parent=dlg)
                return
            b = b_combo.get().strip()
            d = d_entry.get().strip() or "Authorized Dealership"
            n = n_entry.get().strip()
            self.data_store.add_to_whitelist(handle, brand=b, dealer_name=d, notes=n)
            self.parent._log(f"🛡️ Whitelisted authorized dealer '{handle}' ({b}).")
            self._refresh_table()
            dlg.destroy()

        btn_box = tk.Frame(f, bg=t["panel"])
        btn_box.grid(row=4, column=0, columnspan=2, pady=(16, 0), sticky="e")
        tk.Button(btn_box, text="Cancel", command=dlg.destroy, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=10, pady=4).pack(side="right", padx=4)
        tk.Button(btn_box, text="💾 Save Dealer", command=_save, bg=t["accent"], fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4).pack(side="right")

    def _bulk_import_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("📋 Bulk Import Authorized Dealerships")
        dlg.geometry("560x480")
        dlg.configure(bg=self.t["bg"])
        dlg.transient(self)
        dlg.grab_set()
        self.parent._apply_dark_titlebar(dlg)

        t = self.t
        f = tk.Frame(dlg, bg=t["panel"], padx=16, pady=14)
        f.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(f, text="Paste List of Store URLs or Seller Usernames (1 per line):", bg=t["panel"], fg=t["text"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        txt = tk.Text(f, height=12, bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"], font=FONT_SM, relief="flat")
        txt.pack(fill="both", expand=True, pady=4)

        opt_frame = tk.Frame(f, bg=t["panel"])
        opt_frame.pack(fill="x", pady=6)
        
        tk.Label(opt_frame, text="Assign Brand:", bg=t["panel"], fg=t["text"], font=FONT_SM).pack(side="left", padx=(0, 4))
        brands = ["General / All Brands"] + sorted(list(self.data_store.get_brands().keys()))
        b_combo = ttk.Combobox(opt_frame, values=brands, font=FONT_SM, width=20)
        b_combo.pack(side="left", padx=(0, 8))
        b_combo.set("Toyota")

        def _do_import():
            raw = txt.get("1.0", "end").strip()
            if not raw:
                messagebox.showwarning("Empty", "Please paste one or more seller handles.", parent=dlg)
                return
            b = b_combo.get().strip()
            added = self.data_store.bulk_add_whitelist(raw, brand=b, notes="Bulk Client Import")
            self.parent._log(f"🛡️ Bulk imported {added} authorized dealers for {b}.")
            self._refresh_table()
            messagebox.showinfo("Import Complete", f"Successfully imported {added} authorized dealers into your Whitelist!", parent=dlg)
            dlg.destroy()

        btn_box = tk.Frame(f, bg=t["panel"])
        btn_box.pack(fill="x", pady=(8, 0))
        tk.Button(btn_box, text="Cancel", command=dlg.destroy, bg=t["entry_bg"], fg=t["text"], relief="flat", padx=10, pady=4).pack(side="right", padx=4)
        tk.Button(btn_box, text="📥 Import Dealers", command=_do_import, bg=t["accent"], fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=14, pady=4).pack(side="right")

    def _remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select one or more dealers to remove.")
            return
        if not messagebox.askyesno("Confirm Removal", f"Remove {len(sel)} dealer(s) from your Authorized Whitelist?"):
            return
        for iid in sel:
            handle = self.tree.item(iid)["values"][0]
            self.data_store.remove_from_whitelist(str(handle))
        self._refresh_table()
        self.parent._log(f"🛡️ Removed {len(sel)} dealer(s) from Authorized Whitelist.")

    def _export_csv(self):
        wl = self.data_store.get_whitelist()
        if not wl:
            messagebox.showinfo("Export", "No whitelisted dealers to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="authorized_dealers_whitelist.csv")
        if not path: return
        try:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Seller Handle", "Brand", "Dealership Name", "Notes", "Date Added"])
                for h, d in wl.items():
                    writer.writerow([h, d.get("brand", ""), d.get("dealer_name", ""), d.get("notes", ""), d.get("added_at", "")])
            messagebox.showinfo("Exported", f"Successfully exported {len(wl)} whitelisted dealers to:\n\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


if __name__ == "__main__":
    app = EbayTool()
    app.mainloop()


