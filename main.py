import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import re
import io
import threading
import urllib.request
from datetime import datetime
import webbrowser
import winsound
from PIL import Image, ImageTk

from scraper import EbayScraper
from aliexpress_scraper import AliExpressScraper
from wish_scraper import WishScraper
from temu_scraper import TemuScraper
from api_client import EbayAPIClient
from exporter import ExcelExporter
from data_store import DataStore

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
        "name": "💻 Matrix Phosphor CRT",
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
        "name": "🍵 Matcha & Forest Zen",
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
    "dracula": {
        "name": "🧛 Classic Dracula Theme",
        "bg": "#282a36",
        "panel": "#21222c",
        "accent": "#bd93f9",
        "accent2": "#ff79c6",
        "success": "#50fa7b",
        "warning": "#f1fa8c",
        "danger": "#ff5555",
        "text": "#f8f8f2",
        "subtext": "#6272a4",
        "entry_bg": "#383a59",
        "border": "#44475a",
        "btn_normal_bg": "#383a59",
        "btn_normal_fg": "#f8f8f2",
        "select_bg": "#bd93f9",
        "select_fg": "#282a36",
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
        "name": "🌸 Kate's Sakura Blossom",
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
        "name": "🌊 Deep Ocean Navy",
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
    "light": {
        "name": "☀️ Clean Executive",
        "bg": "#f1f5f9",
        "panel": "#ffffff",
        "accent": "#2563eb",
        "accent2": "#1d4ed8",
        "success": "#16a34a",
        "warning": "#d97706",
        "danger": "#dc2626",
        "text": "#0f172a",
        "subtext": "#64748b",
        "entry_bg": "#ffffff",
        "border": "#cbd5e1",
        "btn_normal_bg": "#e2e8f0",
        "btn_normal_fg": "#0f172a",
        "select_bg": "#2563eb",
        "select_fg": "#ffffff",
    },
    # ── Client-Inspired Corporate Themes ──────────────────────────────────────
    "lego": {
        "name": "🧱 LEGO Classic Brick",
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
        "border": "#d11013",
        "btn_normal_bg": "#2e313d",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#d11013",
        "select_fg": "#ffffff",
    },
    "auto_steel": {
        "name": "🚗 Automotive Steel",
        "bg": "#1e2229",
        "panel": "#282d37",
        "accent": "#2ec4b6",
        "accent2": "#cbf3f0",
        "success": "#38b000",
        "warning": "#e36414",
        "danger": "#d90429",
        "text": "#f1f5f9",
        "subtext": "#94a3b8",
        "entry_bg": "#333945",
        "border": "#4a5568",
        "btn_normal_bg": "#333945",
        "btn_normal_fg": "#2ec4b6",
        "select_bg": "#2ec4b6",
        "select_fg": "#1e2229",
    },
    "nfl": {
        "name": "🏈 NFL Gridiron Shield",
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
        "border": "#d50a0a",
        "btn_normal_bg": "#1a274d",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#d50a0a",
        "select_fg": "#ffffff",
    },
    "stanley": {
        "name": "🥤 Stanley 1913 Hammertone",
        "bg": "#1b241c",
        "panel": "#263228",
        "accent": "#84a98c",
        "accent2": "#cad2c5",
        "success": "#52b788",
        "warning": "#d4a373",
        "danger": "#bc4749",
        "text": "#f5ebe0",
        "subtext": "#9caf88",
        "entry_bg": "#2e3d30",
        "border": "#475b4b",
        "btn_normal_bg": "#2e3d30",
        "btn_normal_fg": "#f5ebe0",
        "select_bg": "#84a98c",
        "select_fg": "#1b241c",
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
        "border": "#ff6f00",
        "btn_normal_bg": "#292929",
        "btn_normal_fg": "#ff6f00",
        "select_bg": "#ff6f00",
        "select_fg": "#000000",
    },
    "mls": {
        "name": "⚽ MLS Matchday Pitch",
        "bg": "#0d1f18",
        "panel": "#142e24",
        "accent": "#00ff87",
        "accent2": "#60efff",
        "success": "#00ff87",
        "warning": "#ffd166",
        "danger": "#ef476f",
        "text": "#f0fdf4",
        "subtext": "#74c69d",
        "entry_bg": "#1c3d31",
        "border": "#2d5a49",
        "btn_normal_bg": "#1c3d31",
        "btn_normal_fg": "#00ff87",
        "select_bg": "#00ff87",
        "select_fg": "#0d1f18",
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
        "border": "#5b3b8c",
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
        "border": "#ff0033",
        "btn_normal_bg": "#242424",
        "btn_normal_fg": "#ffd600",
        "select_bg": "#ff0033",
        "select_fg": "#ffffff",
    },
    # ── Automotive & Motorsport Legends ───────────────────────────────────────
    "toyota_gr": {
        "name": "🏁 Toyota Gazoo Racing",
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
        "border": "#eb0a1e",
        "btn_normal_bg": "#282a30",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#eb0a1e",
        "select_fg": "#ffffff",
    },
    "subaru_wrc": {
        "name": "⭐ Subaru World Rally",
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
        "border": "#0055b8",
        "btn_normal_bg": "#1a2744",
        "btn_normal_fg": "#ffd100",
        "select_bg": "#0055b8",
        "select_fg": "#ffffff",
    },
    "corvette": {
        "name": "🟡 Corvette Racing",
        "bg": "#121316",
        "panel": "#1a1c21",
        "accent": "#ffeb3b",
        "accent2": "#fff176",
        "success": "#4caf50",
        "warning": "#ff9800",
        "danger": "#f44336",
        "text": "#ffffff",
        "subtext": "#9e9e9e",
        "entry_bg": "#262930",
        "border": "#ffeb3b",
        "btn_normal_bg": "#262930",
        "btn_normal_fg": "#ffeb3b",
        "select_bg": "#ffeb3b",
        "select_fg": "#000000",
    },
    "gm_heritage": {
        "name": "💎 General Motors & ACDelco",
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
        "border": "#ffb81c",
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
        "name": "⚡ Kia GT-Line & Stinger",
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
        "border": "#e60026",
        "btn_normal_bg": "#2e232c",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#e60026",
        "select_fg": "#ffffff",
    },
    "ford_racing": {
        "name": "🔵 Ford Racing Performance",
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
        "border": "#00a3e0",
        "btn_normal_bg": "#182e4d",
        "btn_normal_fg": "#00a3e0",
        "select_bg": "#0050b3",
        "select_fg": "#ffffff",
    },
    "hyundai_n": {
        "name": "⚡ Hyundai N Performance",
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
        "border": "#e53935",
        "btn_normal_bg": "#252b36",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#e53935",
        "select_fg": "#ffffff",
    },
    "ferrari": {
        "name": "🐎 Ferrari Corsa Rosso",
        "bg": "#111215",
        "panel": "#191a1f",
        "accent": "#d40000",
        "accent2": "#ffea00",
        "success": "#00c853",
        "warning": "#ffea00",
        "danger": "#d40000",
        "text": "#ffffff",
        "subtext": "#ffea00",
        "entry_bg": "#24252c",
        "border": "#d40000",
        "btn_normal_bg": "#24252c",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#d40000",
        "select_fg": "#ffffff",
    },
    "porsche_gt": {
        "name": "🏆 Porsche Weissach GT",
        "bg": "#16171a",
        "panel": "#202126",
        "accent": "#a3e635",
        "accent2": "#bef264",
        "success": "#a3e635",
        "warning": "#fbbf24",
        "danger": "#ef4444",
        "text": "#f3f4f6",
        "subtext": "#9ca3af",
        "entry_bg": "#2b2c33",
        "border": "#a3e635",
        "btn_normal_bg": "#2b2c33",
        "btn_normal_fg": "#a3e635",
        "select_bg": "#a3e635",
        "select_fg": "#16171a",
    },
    "jeep_trail": {
        "name": "🚙 Jeep Trail Rated 4x4",
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
        "border": "#f77f00",
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
        "border": "#d90429",
        "btn_normal_bg": "#2d2433",
        "btn_normal_fg": "#ffffff",
        "select_bg": "#d90429",
        "select_fg": "#ffffff",
    },
    "bmw_m": {
        "name": "🏁 BMW M Motorsport",
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
        "border": "#0099ff",
        "btn_normal_bg": "#1f2937",
        "btn_normal_fg": "#0099ff",
        "select_bg": "#0099ff",
        "select_fg": "#ffffff",
    }
}

FONT      = ("Segoe UI", 10)
FONT_SM   = ("Segoe UI", 9)
FONT_LG   = ("Segoe UI", 12, "bold")
FONT_HEAD = ("Segoe UI", 11, "bold")

QUOTES = [
    "🕵️ Trademark Shield: Online and Protecting Brand Assets!",
    "🛡️ Infringement Detection Engine: 100% Calibrated!",
    "🏎️ 'I live my life a quarter mile at a time. For those 10 seconds or less... I'm free.' — Dom Toretto",
    "💨 'Too soon, Junior! You didn't double-clutch like you should!'",
    "🔥 'DANGER TO MANIFOLD: Floor pan intact, scraping at maximum velocity!'",
    "🏁 'It don't matter if you win by an inch or a mile. Winning's winning.'",
    "🐎 'Eleanor... Don't you stall on me now, girl!' — Memphis Raines",
    "☕ Converting Caffeine into Intellectual Property Compliance...",
    "⚡ Searching through the eBay Matrix with Supercharged Precision!",
    "🚗 'I need NOS. One of the big ones. No, make it two. By tonight.'",
]

THEME_QUOTES = {
    "lego": "🧱 Careful! Stepped on a red 2x4 Lego brick! Enforcement Defense +100.",
    "taylor_swift": "✨ 'I knew you were counterfeit when you walked in...' 🎶",
    "toyota_gr": "🏁 Toyota Gazoo Racing: Twin-turbo spooling at 8,500 RPM on the Nürburgring!",
    "dodge_hellcat": "🔥 6.2L Supercharged HEMI V8 idling at 797 Horsepower. Zero infringement allowed!",
    "bmw_m": "🏁 BMW M shift lights flashing red... Ultimate Driving Machine compliance active!",
    "corvette": "🟡 Corvette C8.R Flat-Plane V8 screaming down the Mulsanne straight!",
    "subaru_wrc": "⭐ Symmetrical AWD launching through muddy stages at 120 MPH!",
    "ford_racing": "🔵 Ford Performance EcoBoost twin-turbos delivering high-octane enforcement!",
    "hyundai_n": "⚡ Hyundai N Corner Rascal mode engaged... Zero slip compliance!",
    "ferrari": "🐎 Ferrari V12 singing at 9,000 RPM through Monza's Parabolica!",
    "porsche_gt": "🏆 Porsche Weissach GT package active: Aerodynamic downforce maximized!",
    "jeep_trail": "🚙 Trail-Rated 4x4 crawling through rocky listings... Nothing gets past.",
    "stanley": "🥤 Dropped from a 2-story construction site into a bonfire... Still ice cold.",
    "black_decker": "🔨 High-torque brushless impact driver drilling through database records!",
    "sprayground": "🎒 Shark mouth teeth exposed... Biting down on unauthorized listings!",
    "pastel": "🌸 Cherry blossoms drifting gently across the brand library... Zen mode active.",
    "nfl": "🏈 4th & inches on the goal line... Defense holds the perimeter!",
    "auto_steel": "🚗 Hand-hammered forged aluminum with rich copper patina... Built to last.",
    "gm_heritage": "💎 General Motors & ACDelco: Protecting genuine American craftsmanship from Detroit to the world!",
    "eleanor": "🐎 'Eleanor: The unicorn of muscle cars. Push the Go-Baby-Go button and hold on tight!' — Memphis Raines",
    "kia_gt": "⚡ Kia GT-Line & Stinger: Twin-turbo 368 HP compliance scanning running at full boost!",
    "matrix": "💻 'You take the blue pill—the story ends. You run this tool—you stay in Wonderland.'",
    "cyberpunk": "⚡ 'Wake up, Samurai. We have counterfeit listings to harvest.'",
    "catppuccin": "☕ A velvety warm mocha brewed to perfection. Smooth and cozy.",
    "synthwave": "🕹️ High Score: 999,999 PTS! Insert coin to continue.",
}

THEME_SUBHEADERS = {
    "toyota_gr": "🏁 TOYOTA GAZOO RACING & LEXUS — BRAND PROTECTION SUITE",
    "gm_heritage": "💎 GENERAL MOTORS & ACDELCO — IP COMPLIANCE HARVESTER",
    "corvette": "🟡 CORVETTE RACING — PERFORMANCE ENFORCEMENT ENGINE",
    "subaru_wrc": "⭐ SUBARU MOTORSPORTS — SYMMETRICAL COMPLIANCE SHIELD",
    "kia_gt": "⚡ KIA GT-LINE & STINGER — HIGH-BOOST TRADEMARK DEFENSE",
    "hyundai_n": "⚡ HYUNDAI N PERFORMANCE — CORNER RASCAL COMPLIANCE",
    "ford_racing": "🔵 FORD PERFORMANCE RACING — ECOBOOST DEFENSE SUITE",
    "dodge_hellcat": "🔥 DODGE SRT HELLCAT & MOPAR — SUPERCHARGED TRADEMARK SHIELD",
    "jeep_trail": "🚙 JEEP TRAIL RATED 4x4 — ALL-TERRAIN BRAND PROTECTION",
    "bmw_m": "🏁 BMW M MOTORSPORT — ULTIMATE COMPLIANCE MACHINE",
    "porsche_gt": "🏆 PORSCHE WEISSACH GT — AERODYNAMIC COUNTERFEIT INTERCEPTOR",
    "ferrari": "🐎 SCUDERIA FERRARI — CORSA ROSSO IP DEFENSE",
    "lego": "🧱 THE LEGO GROUP — GLOBAL TRADEMARK GUARDIAN",
    "stanley": "🥤 STANLEY 1913 — HAMMERTONE TOUGH TRADEMARK PROTECTION",
    "black_decker": "🔨 BLACK & DECKER — INDUSTRIAL BRAND COMPLIANCE",
    "nfl": "🏈 NFL GRIDIRON — OFFICIAL MERCHANDISE ENFORCEMENT",
    "mls": "⚽ MLS MATCHDAY — PITCHSIDE COUNTERFEIT INTERCEPTION",
    "taylor_swift": "✨ TAYLOR SWIFT ERAS — OFFICIAL TRADEMARK DEFENSE",
    "sprayground": "🎒 SPRAYGROUND SHARK — STREETWEAR AUTHENTICITY SHIELD",
    "pastel": "🌸 KATE'S SAKURA TREE — ZEN BRAND HARVESTER",
    "eleanor": "🐎 1967 SHELBY GT500 ELEANOR — GO-BABY-GO UNICORN EDITION",
    "synthwave": "🕹️ RETRO SYNTHWAVE 80s — ARCADE COMPLIANCE SPECIAL",
    "cyberpunk": "⚡ CYBERPUNK 2077 — NIGHT CITY BRAND RUNNER",
    "matrix": "💻 THE MATRIX HARVESTER — ZERO INFRINGEMENT CONSTRUCT",
    "auto_steel": "🚗 AUTOMOTIVE HERITAGE — FORGED ALUMINUM & PATINA SHIELD",
    "midnight": "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER",
    "dark": "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER",
    "slate": "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER",
    "navy": "🛡️ ENTERPRISE BRAND ENFORCEMENT & IP HARVESTER",
    "catppuccin": "☕ MOCHA VELVET — ARTISAN BRAND ENFORCEMENT",
    "forest": "🌲 FOREST CANOPY — SUSTAINABLE IP COMPLIANCE",
    "nord": "❄️ NORDIC ARCTIC — PRECISION ICE DEFENSE",
}


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
        self.marketplace_var= tk.StringVar(value="🛒 eBay.com")
        self.exporter       = ExcelExporter()

        # Load saved theme
        saved_theme_key = self.data_store.get_setting("theme", "midnight")
        if saved_theme_key not in THEMES:
            saved_theme_key = "midnight"
        self.current_theme_key = saved_theme_key
        self.theme = THEMES[self.current_theme_key]

        # Responsive window sizing
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = min(1640, max(1360, screen_w - 40))
        win_h = min(1140, max(960, screen_h - 60))
        pos_x = max(10, (screen_w - win_w) // 2)
        pos_y = max(5, (screen_h - win_h - 40) // 2)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(1200, 800)
        self.configure(bg=self.theme["bg"])

        self.use_api        = tk.BooleanVar(value=bool(self.data_store.get_setting("use_api", False)))
        self.api_app_id_var = tk.StringVar(value=self.data_store.get_setting("api_app_id", ""))
        self.api_cert_id_var= tk.StringVar(value=self.data_store.get_setting("api_cert_id", ""))
        self.condition_var  = tk.StringVar(value="all")
        self.theme_var      = tk.StringVar(value=self.theme["name"])
        self.show_preview_var = tk.BooleanVar(value=True)
        self.sound_enabled_var = tk.BooleanVar(value=True)

        # Brand targeting states: { item_id: "target" | "exclude" | "neutral" }
        self.brand_states   = {}

        self.results        = []          # all harvested rows this session
        self.seen_item_ids  = set()       # session deduplication
        self.queue          = []          # list of jobs
        self.executed_jobs  = []          # record of executed jobs for audit log
        self.sort_directions= {}          # col -> bool (True = descending)

        # Image thumbnail cache & Hover popup window
        self.img_cache      = {}          # url -> PhotoImage
        self.preview_win    = None
        self.last_hovered_iid = None
        self.preview_cancel_id = None
        self._drag_data     = None

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

        self._build_ui()
        self._refresh_brand_tree()
        self._refresh_exclusion_list()

        # Listen globally for Konami Code
        self.bind_all("<Key>", self._check_konami)

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
        top_right.pack(side="right", padx=16)
        self.themed_widgets["panel_frames"].append(top_right)

        # 1. Professional / Core Operations
        market_lbl = tk.Label(top_right, text="🌐 Platform:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        market_lbl.pack(side="left", padx=(0, 4))
        self.themed_widgets["subtext_labels"].append(market_lbl)

        self.market_combo = ttk.Combobox(top_right, textvariable=self.marketplace_var,
                                         values=["🛒 eBay.com", "🌐 AliExpress.com", "🌠 Wish.com", "🟠 Temu.com"],
                                         state="readonly", width=15, font=FONT_SM)
        self.market_combo.pack(side="left", padx=(0, 8))
        self.market_combo.bind("<<ComboboxSelected>>", self._on_market_changed)

        self._btn(top_right, "🛡️ A2C2 Registry", self._open_enforcement_registry_window).pack(side="left", padx=(0, 4))
        self._btn(top_right, "🕵️ Threat Intel", self._open_threat_intel_window, accent=True).pack(side="left", padx=(0, 10))

        # 2. Additional Automation Settings
        bg_cb = tk.Checkbutton(top_right, text="👻 Background Search",
                               variable=self.headless_var, command=self._toggle_headless,
                               bg=t["panel"], fg=t["text"], selectcolor=t["entry_bg"],
                               activebackground=t["panel"], font=FONT_SM)
        bg_cb.pack(side="left", padx=(0, 6))
        self.themed_widgets["checks"].append(bg_cb)

        self.api_cb = tk.Checkbutton(top_right, text="Use API",
                                     variable=self.use_api, command=self._toggle_api,
                                     bg=t["panel"], fg=t["text"], selectcolor=t["entry_bg"],
                                     activebackground=t["panel"], font=FONT_SM)
        self.api_cb.pack(side="left", padx=(0, 8))
        self.themed_widgets["checks"].append(self.api_cb)

        self.app_id_lbl = tk.Label(top_right, text="App ID:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        self.app_id_lbl.pack(side="left", padx=(4, 2))
        self.themed_widgets["subtext_labels"].append(self.app_id_lbl)

        self.app_id_entry = tk.Entry(top_right, textvariable=self.api_app_id_var, width=14,
                                     bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                     relief="flat", font=FONT_SM)
        self.app_id_entry.pack(side="left")
        self.themed_widgets["text_inputs"].append(self.app_id_entry)

        self.cert_id_lbl = tk.Label(top_right, text="Cert ID:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        self.cert_id_lbl.pack(side="left", padx=(6, 2))
        self.themed_widgets["subtext_labels"].append(self.cert_id_lbl)

        self.cert_id_entry = tk.Entry(top_right, textvariable=self.api_cert_id_var, width=14,
                                      bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                      relief="flat", font=FONT_SM, show="•")
        self.cert_id_entry.pack(side="left")
        self.themed_widgets["text_inputs"].append(self.cert_id_entry)

        self.save_keys_btn = self._btn(top_right, "Save Keys", self._save_api_keys, accent=True)
        self.save_keys_btn.pack(side="left", padx=4)

        # 3. Customization & System Info (Rightmost)
        theme_lbl = tk.Label(top_right, text="🎨 Theme:", bg=t["panel"], fg=t["subtext"], font=FONT_SM)
        theme_lbl.pack(side="left", padx=(6, 4))
        self.themed_widgets["subtext_labels"].append(theme_lbl)

        current_key = self.current_theme_key
        theme_names = [th["name"] for k, th in THEMES.items() if not th.get("hidden", False) or k == current_key]
        self.theme_combo = ttk.Combobox(top_right, textvariable=self.theme_var, values=theme_names,
                                        state="readonly", width=30, font=FONT_SM)
        self.theme_combo.pack(side="left", padx=(0, 6))
        self.theme_combo.bind("<<ComboboxSelected>>", self._on_theme_changed)

        self.about_btn = self._btn(top_right, "ℹ", self._show_about_dialog)
        self.about_btn.pack(side="left", padx=(0, 0))

        self._toggle_api()

        # ── main paned layout ─────────────────────────────────────────────────
        self.paned = tk.PanedWindow(self, orient="horizontal", bg=t["bg"], sashwidth=6,
                                    sashrelief="flat", bd=0)
        self.paned.pack(fill="both", expand=True, padx=8, pady=6)

        left  = self._build_left_panel(self.paned)
        right = self._build_right_panel(self.paned)

        self.paned.add(left,  minsize=440, width=490)
        self.paned.add(right, minsize=620)

        # ── status bar ───────────────────────────────────────────────────────
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

        self.progress = ttk.Progressbar(self.status_bar, mode="indeterminate", length=180)
        self.progress.pack(side="right", padx=12)

    # ── LEFT PANEL ────────────────────────────────────────────────────
    def _build_left_panel(self, parent):
        t = self.theme
        frame = tk.Frame(parent, bg=t["bg"])
        self.themed_widgets["bg_frames"].append(frame)

        # ── Stores / Sellers input (Multi-store support) ──────────────────────
        self._section(frame, "🏪 Stores / Sellers (One per line or URL)")
        
        store_frame = tk.Frame(frame, bg=t["bg"])
        store_frame.pack(fill="x", padx=8, pady=(0, 4))
        self.themed_widgets["bg_frames"].append(store_frame)
        
        self.store_text = tk.Text(store_frame, height=3, bg=t["entry_bg"], fg=t["text"],
                                  insertbackground=t["text"], relief="flat", font=FONT_SM,
                                  wrap="none")
        store_vsb = ttk.Scrollbar(store_frame, orient="vertical", command=self.store_text.yview)
        self.store_text.configure(yscrollcommand=store_vsb.set)
        self.store_text.pack(side="left", fill="both", expand=True)
        store_vsb.pack(side="right", fill="y")
        self.themed_widgets["text_inputs"].append(self.store_text)
        
        self.store_placeholder = "https://www.ebay.com/str/store1\nhttps://www.aliexpress.com/store/110123456\nseller3"
        self.store_text.insert("1.0", self.store_placeholder)
        self.store_text.config(fg=t["subtext"])
        self.store_text.bind("<FocusIn>", self._clear_store_ph)
        self.store_text.bind("<FocusOut>", self._restore_store_ph)
        self.store_text.bind("<KeyRelease>", self._on_store_text_key)

        # Condition filter
        cond_row = tk.Frame(frame, bg=t["bg"])
        cond_row.pack(fill="x", padx=8, pady=(0, 4))
        self.themed_widgets["bg_frames"].append(cond_row)

        cond_lbl = tk.Label(cond_row, text="Condition:", bg=t["bg"], fg=t["subtext"], font=FONT_SM)
        cond_lbl.pack(side="left")
        self.themed_widgets["subtext_labels"].append(cond_lbl)

        ttk.Radiobutton(cond_row, text="All", variable=self.condition_var, value="all").pack(side="left", padx=6)
        ttk.Radiobutton(cond_row, text="New Only", variable=self.condition_var, value="new").pack(side="left", padx=6)
        ttk.Radiobutton(cond_row, text="Used Only", variable=self.condition_var, value="used").pack(side="left", padx=6)

        # ── Brand Library & Targeting ─────────────────────────────────────────
        self._section(frame, "🏷  Brand Library (Target & Exclude)")

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
        target_tools_2.pack(fill="x", padx=8, pady=(0, 4))
        self.themed_widgets["bg_frames"].append(target_tools_2)

        self._btn(target_tools_2, "⚡ Excl Other Brands", self._auto_exclude_other_brands).pack(side="left", padx=(0, 3))
        self._btn(target_tools_2, "⚡ Excl Other Models", self._auto_exclude_other_models).pack(side="left", padx=(0, 3))
        self._btn(target_tools_2, "⚡ Excl All Others", self._auto_exclude_all_others).pack(side="left")

        brand_ctrl = tk.Frame(frame, bg=t["bg"])
        brand_ctrl.pack(fill="x", padx=8, pady=(0, 3))
        self.themed_widgets["bg_frames"].append(brand_ctrl)

        self.brand_tree = ttk.Treeview(brand_ctrl, height=8, selectmode="extended")
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

        # Include terms preview
        prev_lbl = tk.Label(frame, text="Active Target Terms Preview (editable for custom keywords):",
                            bg=t["bg"], fg=t["subtext"], font=FONT_SM)
        prev_lbl.pack(anchor="w", padx=8, pady=(4, 2))
        self.themed_widgets["subtext_labels"].append(prev_lbl)

        self.include_text = tk.Text(frame, height=3, bg=t["entry_bg"], fg=t["text"],
                                    insertbackground=t["text"], relief="flat", font=FONT_SM,
                                    wrap="word")
        self.include_text.pack(fill="x", padx=8)
        self.themed_widgets["text_inputs"].append(self.include_text)

        # ── Exclusion list ────────────────────────────────────────────────────
        self._section(frame, "🚫 Generic Exclusion Terms")

        # Select all / unselect all toolbar
        excl_tools = tk.Frame(frame, bg=t["bg"])
        excl_tools.pack(fill="x", padx=8, pady=(0, 3))
        self.themed_widgets["bg_frames"].append(excl_tools)

        self._btn(excl_tools, "☑ Select All", self._select_all_exclusions).pack(side="left", padx=(0, 4))
        self._btn(excl_tools, "☐ Unselect All", self._unselect_all_exclusions).pack(side="left")

        excl_outer = tk.Frame(frame, bg=t["bg"])
        excl_outer.pack(fill="x", padx=8)
        self.themed_widgets["bg_frames"].append(excl_outer)

        self.excl_canvas = tk.Canvas(excl_outer, bg=t["entry_bg"], height=85,
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
        self.new_excl_entry.bind("<KeyRelease>", self._on_excl_entry_key)
        self._btn(excl_btn_row, "＋ Add", self._add_exclusion).pack(side="left")
        self._btn(excl_btn_row, "✕", self._remove_exclusion, danger=True).pack(side="left", padx=4)

        # ── Queue / Run Controls ──────────────────────────────────────────────
        self._section(frame, "📋 Search Queue & Batch Execution")

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

        self._btn(q_actions_row, "➕ Add to Queue", self._add_to_queue).pack(side="left", fill="x", expand=True, padx=(0, 3))
        self._btn(q_actions_row, "🎯 Clean Brand Sweep", self._queue_clean_targeted_brands, accent=True).pack(side="right", fill="x", expand=True, padx=(3, 0))

        self.queue_list = tk.Listbox(frame, height=4, bg=t["entry_bg"], fg=t["text"],
                                     selectbackground=t["accent"], font=FONT_SM,
                                     relief="flat", activestyle="none")
        self.queue_list.pack(fill="x", padx=8)
        self.queue_list.bind("<Delete>", lambda e: self._remove_selected_from_queue())
        self.queue_list.bind("<BackSpace>", lambda e: self._remove_selected_from_queue())
        self.themed_widgets["text_inputs"].append(self.queue_list)

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

        self.del_q_btn = self._btn(q_btn_row, "✕ Remove Selected", self._remove_selected_from_queue)
        self.del_q_btn.pack(side="left", padx=(4, 0))

        self.clear_q_btn = self._btn(q_btn_row, "🗑 Clear All", self._clear_queue)
        self.clear_q_btn.pack(side="right")

        return frame

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

        # Hover preview toggle
        preview_cb = tk.Checkbutton(toolbar, text="🖼 Hover Thumbnail Preview",
                                    variable=self.show_preview_var,
                                    bg=t["panel"], fg=t["text"], selectcolor=t["entry_bg"],
                                    activebackground=t["panel"], font=FONT_SM)
        preview_cb.pack(side="left", padx=12)
        self.themed_widgets["checks"].append(preview_cb)

        self._btn(toolbar, "🗑 Clear All", self._clear_results, danger=True).pack(side="right", padx=4)
        self._btn(toolbar, "✕ Remove Selected", self._remove_selected_results).pack(side="right", padx=4)
        self._btn(toolbar, "✂ Deduplicate", self._remove_duplicates).pack(side="right", padx=4)
        self._btn(toolbar, "🏪 Enrich Sellers", self._enrich_sellers).pack(side="right", padx=4)
        self._btn(toolbar, "💾 Export to Excel", self._export, accent=True).pack(side="right", padx=6)

        # ── 1.5 Filter & Bulk Tagging Toolbar ────────────────────────────────
        filter_bar = tk.Frame(frame, bg=t["panel"], pady=5, padx=8)
        filter_bar.pack(side="top", fill="x", padx=4, pady=(2, 2))
        self.themed_widgets["panel_frames"].append(filter_bar)

        # Left side: Live search filter
        f_lbl = tk.Label(filter_bar, text="🔍 Filter:", font=FONT_SM, bg=t["panel"], fg=t["accent"])
        f_lbl.pack(side="left", padx=(0, 4))
        self.themed_widgets["section_labels"].append(f_lbl)

        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", self._on_filter_changed)
        self.filter_entry = tk.Entry(filter_bar, textvariable=self.filter_var, width=16,
                                     bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                     relief="flat", font=FONT_SM)
        self.filter_entry.pack(side="left", padx=(0, 4))
        self.themed_widgets["text_inputs"].append(self.filter_entry)

        self._btn(filter_bar, "✕ Clear", self._clear_filter).pack(side="left", padx=(0, 8))
        self._btn(filter_bar, "✓ Select All Visible", self._select_all_visible).pack(side="left", padx=(0, 14))

        # Right side: Bulk tag brand & product type
        tag_lbl = tk.Label(filter_bar, text="🏷️ Bulk Tag Selected:", font=("Segoe UI", 9, "bold"),
                           bg=t["panel"], fg=t["text"])
        tag_lbl.pack(side="left", padx=(0, 6))
        self.themed_widgets["text_labels"].append(tag_lbl)

        b_lbl = tk.Label(filter_bar, text="Brand:", font=FONT_SM, bg=t["panel"], fg=t["subtext"])
        b_lbl.pack(side="left", padx=(0, 2))
        self.themed_widgets["subtext_labels"].append(b_lbl)

        self.bulk_brand_var = tk.StringVar(value="(No change)")
        self.bulk_brand_combo = ttk.Combobox(filter_bar, textvariable=self.bulk_brand_var,
                                             width=14, state="readonly", font=FONT_SM)
        self.bulk_brand_combo.pack(side="left", padx=(0, 8))

        pt_lbl = tk.Label(filter_bar, text="Product Type:", font=FONT_SM, bg=t["panel"], fg=t["subtext"])
        pt_lbl.pack(side="left", padx=(0, 2))
        self.themed_widgets["subtext_labels"].append(pt_lbl)

        self.bulk_product_var = tk.StringVar(value="(Select or type...)")
        product_categories = [
            "(Select or type...)",
            "Brakes & Calipers",
            "Air & Fuel Delivery",
            "Suspension & Steering",
            "Wheel Center Caps",
            "Emblems & Badges",
            "Grilles & Front Trim",
            "Key Fobs & Keys",
            "Sensors & Modules",
            "Exhaust & Headers",
            "Lighting & Headlamps",
            "Interior Trim & Mats",
            "Engine & Drivetrain",
            "Apparel & Merchandise",
            "Drinkware & Bottles",
            "Bags & Backpacks",
            "Toys & Building Sets",
            "Uncategorized",
        ]
        self.bulk_product_combo = ttk.Combobox(filter_bar, textvariable=self.bulk_product_var,
                                               values=product_categories, width=18, font=FONT_SM)
        self.bulk_product_combo.pack(side="left", padx=(0, 8))

        self._btn(filter_bar, "⚡ Apply to Selected", self._apply_bulk_tag, accent=True).pack(side="left")

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

        cols = ("brand", "product_type", "title", "item_id", "price", "seller", "location", "thumbnail", "url")
        self.result_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="extended")
        col_widths = {
            "brand": 75,
            "product_type": 110,
            "title": 260,
            "item_id": 100,
            "price": 70,
            "seller": 100,
            "location": 110,
            "thumbnail": 120,
            "url": 130
        }
        for c in cols:
            self.result_tree.heading(c, text=self.col_labels[c],
                                     command=lambda _c=c: self._sort_by_column(_c))
            self.result_tree.column(c, width=col_widths[c], minwidth=45)
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
                if isinstance(inp, tk.Listbox):
                    inp.configure(
                        bg=t["entry_bg"],
                        fg=t["text"],
                        selectbackground=t["accent"],
                        selectforeground="white" if t["bg"] != "#08080a" else "black"
                    )
                elif isinstance(inp, tk.Text):
                    bg_col = t["panel"] if inp == self.log_text else t["entry_bg"]
                    inp.configure(
                        bg=bg_col,
                        fg=t["text"],
                        insertbackground=t["text"],
                        selectbackground=t["accent"],
                        selectforeground="white" if t["bg"] != "#08080a" else "black"
                    )
                elif isinstance(inp, tk.Entry):
                    inp.configure(
                        bg=t["entry_bg"],
                        fg=t["text"],
                        insertbackground=t["text"],
                        selectbackground=t["accent"],
                        selectforeground="white" if t["bg"] != "#08080a" else "black"
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
            try: btn.configure(bg=t["accent"], fg="black" if t.get("name", "").startswith("⚡") else "white", activebackground=t["accent2"])
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
            try: cb.configure(bg=cb.master["bg"], fg=t["text"], selectcolor=t["entry_bg"], activebackground=cb.master["bg"])
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

        # Refresh Trees & Exclusions list with new colors
        self._refresh_brand_tree()
        self._refresh_exclusion_list()
        self._repopulate_results_table()
        self._hide_preview_popup()
        self._log(f"Theme switched to: {t['name']}")

    # ══════════════════════════════════════════════════════════════════════════
    #  WIDGET HELPERS
    # ══════════════════════════════════════════════════════════════════════════
    def _section(self, parent, text):
        t = self.theme
        f = tk.Frame(parent, bg=t["bg"])
        f.pack(fill="x", padx=8, pady=(6, 2))
        self.themed_widgets["bg_frames"].append(f)

        lbl = tk.Label(f, text=text, font=FONT_HEAD, bg=t["bg"], fg=t["accent"])
        lbl.pack(side="left")
        self.themed_widgets["section_labels"].append(lbl)

        div = tk.Frame(f, bg=t["border"], height=1)
        div.pack(side="left", fill="x", expand=True, padx=6)
        self.themed_widgets["dividers"].append(div)

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

        if "AliExpress" in market:
            self.store_placeholder = "🌐 Global Wholesale Search: https://www.aliexpress.com/w/wholesale-\n(Leave blank to sweep entire AliExpress marketplace, or enter specific store URLs)"
            if not current_text or "ebay.com" in current_text or "wish.com" in current_text or "temu.com" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🌐 Switched platform to: AliExpress.com (Global Wholesale & Store Search active)")
        elif "Wish" in market:
            self.store_placeholder = "🌐 Global Wish Search: https://www.wish.com/search/\n(Leave blank to sweep entire Wish marketplace, or enter specific merchant URLs)"
            if not current_text or "ebay.com" in current_text or "aliexpress.com" in current_text or "temu.com" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🌠 Switched platform to: Wish.com (Global Catalog & Merchant Sweeps active)")
        elif "Temu" in market:
            self.store_placeholder = "🌐 Global Temu Search: https://www.temu.com/search_result.html\n(Leave blank to sweep entire Temu marketplace, or enter specific mall URLs)"
            if not current_text or "ebay.com" in current_text or "aliexpress.com" in current_text or "wish.com" in current_text or "store2" in current_text or "Global" in current_text:
                self.store_text.delete("1.0", "end")
                self.store_text.insert("1.0", self.store_placeholder)
                self.store_text.config(fg=t["subtext"])
            self._log("🟠 Switched platform to: Temu.com (Global Catalog & Mall Sweeps active)")
        else:
            self.store_placeholder = "https://www.ebay.com/str/store1\nstore2\nseller3"
            if not current_text or "aliexpress.com" in current_text or "wish.com" in current_text or "temu.com" in current_text or "Global" in current_text:
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
            "https://www.temu.com/search_result.html"
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

        return valid_stores

    def _btn(self, parent, text, cmd, accent=False, danger=False):
        t = self.theme
        if accent:
            bg = t["accent"]
            fg = "black" if t.get("name", "").startswith("⚡") else "white"
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
        style.configure("Treeview",
                        background=t["entry_bg"], foreground=t["text"],
                        fieldbackground=t["entry_bg"], rowheight=24,
                        font=FONT_SM)
        style.configure("Treeview.Heading",
                        background=t["panel"], foreground=t["text"],
                        font=FONT_SM, relief="flat")
        style.map("Treeview", background=[("selected", t["select_bg"])],
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
        """Save currently targeted brands as a new custom portfolio preset."""
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

        name = simpledialog.askstring("Save Preset", "Enter a name for this Portfolio Preset:", parent=self)
        if not name or not name.strip():
            return
        name = name.strip()

        self.data_store.save_preset(name, target_brands)
        self._refresh_preset_list()
        self.preset_var.set(name)
        self._log(f"💾 Saved Portfolio Preset '{name}' with {len(target_brands)} brand(s): {', '.join(target_brands)}")
        messagebox.showinfo("Preset Saved", f"Saved Portfolio Preset '{name}' with {len(target_brands)} brand(s):\n{', '.join(target_brands)}")

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

        # 2. Get explicitly targeted terms
        target_keys = [k for k, v in self.brand_states.items() if v == "target"]
        if not target_keys:
            sel = self.brand_tree.selection()
            if sel:
                target_keys = list(sel)

        if not target_keys:
            messagebox.showwarning("No Target Brands", "Mark at least one brand as 🎯 Target in the brand library first.")
            return

        target_terms = []
        for k in target_keys:
            name = k.split("/")[-1]
            if name not in target_terms:
                target_terms.append(name)

        generic_excludes = self._get_active_exclusions()
        condition = self.condition_var.get()
        market = self.marketplace_var.get()
        if "Wish" in market:
            platform_name = "Wish"
        elif "Temu" in market:
            platform_name = "Temu"
        elif "AliExpress" in market:
            platform_name = "AliExpress"
        else:
            platform_name = "eBay"

        queued_count = 0
        for store in stores:
            for term in target_terms:
                entry = {
                    "store": store,
                    "brand": term,
                    "includes": [term],  # Clean, standalone single keyword!
                    "excludes": list(generic_excludes),
                    "condition": condition
                }
                self.queue.append(entry)
                label = f"{self._store_label(store)} ▸ {term} [Clean 1-Term Sweep]"
                self.queue_list.insert("end", label)
                queued_count += 1

        self._log(f"🎯 Queued {queued_count} Clean Individual Search(es) for [{', '.join(target_terms)}] across {len(stores)} target(s) [{platform_name}]")
        self._status(f"🎯 Queued {queued_count} Clean Term Search(es)!")
        messagebox.showinfo("Clean Searches Queued", f"Queued {queued_count} clean, individual search job(s) for:\n\n{', '.join(target_terms)}\n\nClick '▶ Run' to start harvesting!")

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

        queued_count = 0
        for store in stores:
            for parent_brand in preset_brands:
                if parent_brand not in all_library_brands:
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
                    "includes": includes,
                    "excludes": job_excludes,
                    "condition": condition
                }
                self.queue.append(entry)
                label = f"{self._store_label(store)} ▸ {parent_brand} ({len(includes)} terms | {len(job_excludes)} excl)"
                self.queue_list.insert("end", label)
                queued_count += 1

        self._log(f"📦 [PORTFOLIO SWEEP] Queued {queued_count} batch job(s) for Preset '{preset_name}' ({len(stores)} target(s) × {len(preset_brands)} brand(s))")
        self._status(f"📦 1-Click Sweep: Queued {queued_count} job(s) for {len(stores)} target(s)!")
        messagebox.showinfo("Portfolio Sweep Queued", f"Successfully queued {queued_count} search job(s) for '{preset_name}' across {len(stores)} target(s)!\n\nClick '▶ Run' to start harvesting!")

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
                messagebox.showwarning("Missing", "Mark at least one brand as 🎯 Target (or double-click a brand in the tree).")
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
            top_targets = ["Targeted Search"]

        queued_count = 0
        for store in stores:
            for parent_brand in top_targets:
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
                    "includes": includes,
                    "excludes": job_excludes,
                    "condition": condition
                }
                self.queue.append(entry)
                label = f"{self._store_label(store)} ▸ {parent_brand} ({len(includes)} terms | {len(job_excludes)} excl)"
                self.queue_list.insert("end", label)
                queued_count += 1

        self._log(f"Queued {queued_count} job(s) ({len(stores)} target(s) × {len(top_targets)} brand(s))")

    def _store_label(self, url):
        if not url:
            return "Search"
        low = url.lower()
        if "wish" in low and ("global" in low or "search" in low):
            return "Wish Search"
        if "temu" in low and ("global" in low or "search" in low):
            return "Temu Search"
        if "aliexpress" in low and ("global" in low or "wholesale" in low):
            return "AliExpress Wholesale"
        if "global" in low:
            return "Global Search"
        parts = url.rstrip("/").split("/")
        return parts[-1] if parts else url

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

        if use_api and app_id:
            client = EbayAPIClient(app_id=app_id, cert_id=cert_id)
        else:
            client = None

        total_new_items = 0
        for i, job in enumerate(self.queue):
            if self.stop_event.is_set():
                break

            store_raw = job["store"]
            is_wish = "wish.com" in store_raw.lower() or "Wish" in self.marketplace_var.get()
            is_temu = "temu.com" in store_raw.lower() or "Temu" in self.marketplace_var.get()
            is_aliexpress = "aliexpress.com" in store_raw.lower() or "AliExpress" in self.marketplace_var.get()

            if is_wish:
                platform_name = "Wish"
                mkt_tag = "wish.com"
            elif is_temu:
                platform_name = "Temu"
                mkt_tag = "temu.com"
            elif is_aliexpress:
                platform_name = "AliExpress"
                mkt_tag = "aliexpress.com"
            else:
                platform_name = "eBay"
                mkt_tag = "ebay.com"

            seller_label = self._store_label(store_raw)
            self._status(f"Processing {i+1}/{len(self.queue)} [{platform_name}]: {job['brand']} in {seller_label}")
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
                    for item in items:
                        item_id = item.get("item_id")
                        dedup_key = item_id if item_id else item.get("url")
                        if dedup_key and dedup_key not in self.seen_item_ids:
                            self.seen_item_ids.add(dedup_key)
                            item["brand"] = job["brand"]
                            item["keyword"] = include_term
                            if "marketplace" not in item or not item["marketplace"]:
                                item["marketplace"] = mkt_tag
                            self.results.append(item)
                            new_items.append(item)
                            total_new_items += 1
                        elif not dedup_key:
                            item["brand"] = job["brand"]
                            item["keyword"] = include_term
                            if "marketplace" not in item or not item["marketplace"]:
                                item["marketplace"] = mkt_tag
                            self.results.append(item)
                            new_items.append(item)
                            total_new_items += 1

                    job_record["term_counts"][include_term] = len(items)
                    job_record["total_harvested"] += len(new_items)

                    if new_items:
                        self._update_results_table(new_items)
                    self._log(f"  → Found {len(items)} listings ({len(new_items)} new) for '{include_term}' in {seller_label} [{platform_name}]")

            except Exception as e:
                self._log(f"ERROR on {job['brand']} in {seller_label} [{platform_name}]: {e}", error=True)
                job_record["error"] = str(e)

            self.executed_jobs.append(job_record)

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

        # Ingest session results into Master Enforcement & Recidivism Registry
        if self.results:
            seller_items = {}
            for item in self.results:
                seller = item.get("seller") or "Unknown"
                seller_items.setdefault(seller, []).append(item)
            for seller, s_items in seller_items.items():
                self.data_store.record_enforcement_scan(seller, s_items)
            self._log(f"🛡️ Logged {len(self.results)} listing(s) across {len(seller_items)} seller(s) into A2C2 Master Enforcement Registry.")

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

    def _update_results_table(self, items):
        """Append newly scraped items honoring the active live search filter."""
        def _add():
            query = self.filter_var.get().strip().lower() if hasattr(self, "filter_var") else ""
            for item in items:
                if "product_type" not in item:
                    item["product_type"] = ""

                if query:
                    fields = [
                        str(item.get("brand", "")),
                        str(item.get("product_type", "")),
                        str(item.get("title", "")),
                        str(item.get("item_id", "")),
                        str(item.get("seller", "")),
                        str(item.get("location", "")),
                        str(item.get("price", "")),
                        str(item.get("keyword", "")),
                    ]
                    if not any(query in f.lower() for f in fields):
                        continue

                self.result_tree.insert("", "end", values=(
                    item.get("brand", ""),
                    item.get("product_type", ""),
                    item.get("title", ""),
                    item.get("item_id", ""),
                    item.get("price", ""),
                    item.get("seller", ""),
                    item.get("location", ""),
                    item.get("image_url", ""),
                    item.get("url", ""),
                ))

            if query:
                vis = len(self.result_tree.get_children())
                self.result_count.set(f"{vis} / {len(self.results)} listings (filtered)")
            else:
                self.result_count.set(f"{len(self.results)} listings")
        self.after(0, _add)

    def _repopulate_results_table(self):
        """Clear and refill result_tree from self.results honoring current filter."""
        self.result_tree.delete(*self.result_tree.get_children())
        query = self.filter_var.get().strip().lower() if hasattr(self, "filter_var") else ""

        count = 0
        for item in self.results:
            if "product_type" not in item:
                item["product_type"] = ""

            if query:
                fields = [
                    str(item.get("brand", "")),
                    str(item.get("product_type", "")),
                    str(item.get("title", "")),
                    str(item.get("item_id", "")),
                    str(item.get("seller", "")),
                    str(item.get("location", "")),
                    str(item.get("price", "")),
                    str(item.get("keyword", "")),
                ]
                if not any(query in f.lower() for f in fields):
                    continue

            self.result_tree.insert("", "end", values=(
                item.get("brand", ""),
                item.get("product_type", ""),
                item.get("title", ""),
                item.get("item_id", ""),
                item.get("price", ""),
                item.get("seller", ""),
                item.get("location", ""),
                item.get("image_url", ""),
                item.get("url", ""),
            ))
            count += 1

        if query:
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
            listing_url = values[8] if len(values) > 8 else (values[7] if len(values) > 7 else "")
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

        menu.add_command(label="🌐 Open in Browser", command=lambda: self._open_url(None))
        menu.add_command(label="🏪 Enrich Selected Seller Names (AliExpress)", command=self._enrich_sellers)
        menu.add_separator()
        menu.add_command(label="✕ Remove Selected", command=self._remove_selected_results)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _enrich_sellers(self):
        """Enrich real seller/merchant/store names across AliExpress, Wish, and Temu listings."""
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
                    for it in self.results:
                        if str(it.get("item_id", "")).strip() == item_id:
                            target_items.append(it)
                            break
        else:
            # Check all items in session needing seller enrichment
            for it in self.results:
                mkt = it.get("marketplace", "").lower()
                url = it.get("url", "").lower()
                seller = it.get("seller", "")
                if any(k in mkt or k in url for k in ("aliexpress", "wish", "temu")):
                    if not seller or any(g in seller.lower() for g in ("global", "seller", "aliexpress store", "wish")):
                        target_items.append(it)

        if not target_items:
            messagebox.showinfo("Enrich Sellers", "No listings requiring seller enrichment found (all items already have specific store/merchant names).")
            return

        if not messagebox.askyesno("Enrich Sellers", f"Enrich real merchant/store names for {len(target_items)} listing(s)?\n\nThis will look up the specific seller/store ID for each listing."):
            return

        self._log(f"🏪 Starting Seller Name Enrichment for {len(target_items)} item(s)...")
        self._status(f"🏪 Enriching {len(target_items)} sellers...")
        self.stop_event.clear()
        self.stop_btn.config(state="normal")

        def _worker():
            enriched_count = 0
            
            def _on_prog(current, total, item):
                nonlocal enriched_count
                s_name = item.get("seller")
                if s_name and not any(g in s_name.lower() for g in ("global", "seller")):
                    enriched_count += 1
                self.after(0, lambda: self._status(f"🏪 Enriching Sellers: {current}/{total} -> '{s_name}'"))
                self.after(0, lambda: self._repopulate_results_table())

            try:
                # Group items by platform
                ali_items = [it for it in target_items if "ali" in it.get("marketplace", "").lower() or "aliexpress" in it.get("url", "").lower()]
                wish_items = [it for it in target_items if "wish" in it.get("marketplace", "").lower() or "wish" in it.get("url", "").lower()]
                temu_items = [it for it in target_items if "temu" in it.get("marketplace", "").lower() or "temu" in it.get("url", "").lower()]

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

            finally:
                self.after(0, lambda: self.stop_btn.config(state="disabled"))
                self.after(0, lambda: self._status(f"🏪 Seller enrichment complete! ({enriched_count} updated)"))
                self.after(0, lambda: self._log(f"🏪 Seller enrichment finished: Updated store names for {enriched_count} item(s)."))
                self.after(0, lambda: self._repopulate_results_table())

        threading.Thread(target=_worker, daemon=True).start()

    # ── Hover Thumbnail Preview Engine ───────────────────────────────────────
    def _on_tree_mouse_motion(self, event):
        """Handle cursor motion over results table to trigger thumbnail preview."""
        if not self.show_preview_var.get():
            self._hide_preview_popup()
            return

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

        # Position window near cursor, keeping on screen
        win_x = x_root + 18
        win_y = max(10, y_root - 70)
        self.preview_win.geometry(f"+{win_x}+{win_y}")

        # Check in-memory cache
        if image_url in self.img_cache:
            img_lbl.configure(image=self.img_cache[image_url], text="", width=0, height=0)
        else:
            threading.Thread(target=self._fetch_and_render_img,
                             args=(image_url, img_lbl, self.preview_win), daemon=True).start()

    def _fetch_and_render_img(self, url, img_lbl, target_win):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
            pil_img = Image.open(io.BytesIO(data))
            pil_img.thumbnail((170, 170), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_img)
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
        """Konami code detection & secret word listener (e.g. typing 'rick' anywhere)."""
        key = event.keysym
        self.konami_buffer.append(key)
        if len(self.konami_buffer) > len(self.konami_sequence):
            self.konami_buffer.pop(0)

        if self.konami_buffer == self.konami_sequence:
            self._trigger_konami_easter_egg()
            self.konami_buffer.clear()
            return

        # Secret word detection across typed keys anywhere in application
        if hasattr(event, "char") and event.char and event.char.isprintable():
            self.word_buffer += event.char.lower()
            if len(self.word_buffer) > 20:
                self.word_buffer = self.word_buffer[-20:]
            if any(w in self.word_buffer for w in ("rick", "astley", "nevergonna", "rickroll")):
                self._trigger_rickroll_easter_egg()
                self.word_buffer = ""
            elif any(w in self.word_buffer for w in ("eleanor", "gobabygo", "shelby")):
                self._trigger_eleanor_easter_egg()
                self.word_buffer = ""

    def _on_excl_entry_key(self, event=None):
        """Instant Rickroll or Eleanor detection when typing in generic exclusions box."""
        txt = self.new_excl_entry.get().lower().strip()
        if any(w in txt for w in ("rick", "astley", "never gonna", "rickroll")):
            if not getattr(self, "_rickrolled_excl", False):
                self._rickrolled_excl = True
                self._trigger_rickroll_easter_egg()
        elif any(w in txt for w in ("eleanor", "gobabygo", "shelby")):
            self._trigger_eleanor_easter_egg()
        else:
            self._rickrolled_excl = False

    def _on_store_text_key(self, event=None):
        """Instant Rickroll or Eleanor detection when typing in store / seller box."""
        txt = self.store_text.get("1.0", "end").lower().strip()
        if any(w in txt for w in ("rick", "astley", "never gonna", "rickroll")):
            if not getattr(self, "_rickrolled_store", False):
                self._rickrolled_store = True
                self._trigger_rickroll_easter_egg()
        elif any(w in txt for w in ("eleanor", "gobabygo", "shelby")):
            self._trigger_eleanor_easter_egg()
        else:
            self._rickrolled_store = False

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
        if t_key in THEME_QUOTES and (self.quote_idx % 2 == 1):
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
            (1000, "⚔️ A2C2 DEFENDER", "1,000 Infringements Purged from the Marketplace!"),
            (2000, "🏆 A2C2 ELITE ENFORCER", "2,000 Counterfeits Logged! (Monthly Target Reached!)"),
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
                self._log(f"Exported {len(self.results)} rows → {path}")
                messagebox.showinfo("Exported", f"Saved {len(self.results)} rows to:\n{path}")
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
        self.data_store.set_setting("headless", is_headless)
        self._log(f"Browser search mode: {'👻 Silent Background' if is_headless else '🖥 Visible Browser Window'}")

    def _toggle_api(self):
        state = "normal" if self.use_api.get() else "disabled"
        self.app_id_entry.config(state=state)
        self.cert_id_entry.config(state=state)

    def _save_api_keys(self):
        self.data_store.set_setting("use_api", self.use_api.get())
        self.data_store.set_setting("api_app_id", self.api_app_id_var.get().strip())
        self.data_store.set_setting("api_cert_id", self.api_cert_id_var.get().strip())
        self._log("eBay API settings saved.")
        messagebox.showinfo("Saved", "API settings saved.")

    # ══════════════════════════════════════════════════════════════════════════
    #  A2C2 MASTER STORE ENFORCEMENT & RECIDIVISM REGISTRY
    # ══════════════════════════════════════════════════════════════════════════
    def _open_enforcement_registry_window(self):
        """Open the executive A2C2 Master Store Enforcement & Recidivism Registry dialog."""
        t = self.theme
        win = tk.Toplevel(self)
        win.title("🛡️ A2C2 Master Store Enforcement & Recidivism Registry")
        win.configure(bg=t["bg"])
        win.geometry("1180x680")
        win.minsize(980, 580)
        win.grab_set()

        # Center relative to main window
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 1180) // 2
        y = self.winfo_y() + (self.winfo_height() - 680) // 2
        win.geometry(f"+{max(10, x)}+{max(10, y)}")

        pad_f = tk.Frame(win, bg=t["bg"], padx=14, pady=12)
        pad_f.pack(fill="both", expand=True)

        # ── Header Banner ────────────────────────────────────────────────────
        head_f = tk.Frame(pad_f, bg=t["bg"])
        head_f.pack(fill="x", pady=(0, 8))

        tk.Label(head_f, text="🛡️ A2C2 Master Store Enforcement & Recidivism Registry",
                 font=("Segoe UI", 13, "bold"), bg=t["bg"], fg=t["accent"]).pack(side="left")

        tk.Label(head_f, text="Cross-Brand Infringement Tracking & Repeat Offender Intelligence",
                 font=FONT_SM, bg=t["bg"], fg=t["subtext"]).pack(side="left", padx=12, pady=(2, 0))

        # ── Top KPI Stat Badges ──────────────────────────────────────────────
        kpi_f = tk.Frame(pad_f, bg=t["panel"], padx=12, pady=8)
        kpi_f.pack(fill="x", pady=(0, 8))

        reg_data = self.data_store.get_enforcement_registry()
        total_stores = len(reg_data)
        repeat_offenders = sum(1 for d in reg_data.values() if d.get("scan_count", 1) > 1 or d.get("total_listings", 0) > 10)
        total_infringing_items = sum(d.get("total_listings", len(d.get("items", []))) for d in reg_data.values())
        total_infringing_val = sum(d.get("total_value", 0.0) for d in reg_data.values())

        def _kpi(parent, title, val, color=None):
            f = tk.Frame(parent, bg=t["panel"], padx=12)
            f.pack(side="left", fill="y")
            tk.Label(f, text=title, font=("Segoe UI", 8, "bold"), bg=t["panel"], fg=t["subtext"]).pack(anchor="w")
            tk.Label(f, text=val, font=("Segoe UI", 12, "bold"), bg=t["panel"], fg=color or t["text"]).pack(anchor="w")

        _kpi(kpi_f, "🏬 Stores Harvested", f"{total_stores:,}")
        _kpi(kpi_f, "🚨 Repeat Offender Stores", f"{repeat_offenders:,}", color=t["danger"])
        _kpi(kpi_f, "📦 Infringing Listings Captured", f"{total_infringing_items:,}", color=t["accent"])
        _kpi(kpi_f, "💰 Total Counterfeit Market Value", f"${total_infringing_val:,.2f}", color=t["success"])

        # ── Filter & Search Toolbar ──────────────────────────────────────────
        filter_toolbar = tk.Frame(pad_f, bg=t["bg"])
        filter_toolbar.pack(fill="x", pady=(0, 6))

        tk.Label(filter_toolbar, text="🔍 Search:", font=FONT_SM, bg=t["bg"], fg=t["text"]).pack(side="left", padx=(0, 4))
        reg_filter_var = tk.StringVar()
        reg_filter_entry = tk.Entry(filter_toolbar, textvariable=reg_filter_var, width=20,
                                    bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"],
                                    relief="flat", font=FONT_SM)
        reg_filter_entry.pack(side="left", padx=(0, 8))

        offense_filter_var = tk.StringVar(value="All Stores")
        offense_combo = ttk.Combobox(filter_toolbar, textvariable=offense_filter_var,
                                     values=["All Stores", "🚨 Repeat Offenders Only", "⚠️ First Strike Only"],
                                     state="readonly", width=22, font=FONT_SM)
        offense_combo.pack(side="left", padx=(0, 8))

        # ── Treeview Table ───────────────────────────────────────────────────
        tree_frame = tk.Frame(pad_f, bg=t["bg"])
        tree_frame.pack(fill="both", expand=True)

        cols = ("seller", "status", "brands", "product_types", "listings", "total_val", "locations", "first_seen", "last_scanned", "scans")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        
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

        def _populate_tree():
            tree.delete(*tree.get_children())
            q = reg_filter_var.get().strip().lower()
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

                if q:
                    fields = [seller, status, brands_str, pts_str, locs_str, str(data.get("total_value", ""))]
                    if not any(q in f.lower() for f in fields):
                        continue

                tree.insert("", "end", iid=seller, values=(
                    seller,
                    status,
                    brands_str,
                    pts_str,
                    data.get("total_listings", len(data.get("items", []))),
                    f"${data.get('total_value', 0.0):,.2f}",
                    locs_str,
                    data.get("first_seen", ""),
                    data.get("last_scanned", ""),
                    scans
                ), tags=("repeat" if is_repeat else "normal",))

        reg_filter_var.trace_add("write", lambda *a: _populate_tree())
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

        def _delete_selected_entry():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Select Store", "Select an entry to remove.", parent=win)
                return
            seller_key = sel[0]
            if messagebox.askyesno("Delete Entry", f"Remove store record '{seller_key}' from registry?", parent=win):
                self.data_store.delete_registry_entry(seller_key)
                _populate_tree()
                self._log(f"🗑 Removed '{seller_key}' from Enforcement Registry.")

        self._btn(btn_row, "📄 Export A2C2 Dossier (.xlsx)", _export_dossier, accent=True).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "🔍 Inspect Store Listings", _inspect_selected_seller).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "⚡ Queue Re-Enforcement Sweep", _queue_reenforcement_sweep).pack(side="left", padx=(0, 6))
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
        win.grab_set()

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
        t = self.theme
        win = tk.Toplevel(self)
        win.title("🕵️ Cross-Marketplace Threat Intelligence & Enforcement ROI Hub")
        win.configure(bg=t["bg"])
        win.geometry("1240x720")
        win.minsize(1020, 600)
        win.grab_set()

        # Center relative to main window
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 1240) // 2
        y = self.winfo_y() + (self.winfo_height() - 720) // 2
        win.geometry(f"+{max(10, x)}+{max(10, y)}")

        pad_f = tk.Frame(win, bg=t["bg"], padx=14, pady=12)
        pad_f.pack(fill="both", expand=True)

        # ── Data Aggregation & Intelligence Computation ───────────────────────
        all_items = list(self.results)
        reg = self.data_store.get_enforcement_registry()
        for s_name, s_data in reg.items():
            for it in s_data.get("items", []):
                if it not in all_items:
                    all_items.append(it)

        # 1. Platform counts & price parsing
        mkt_counts = {"eBay": 0, "AliExpress": 0, "Wish": 0, "Temu": 0, "Other": 0}
        total_cf_value = 0.0
        total_msrp_est = 0.0

        brand_stats = {}  # brand -> {count, total_cf_val, total_msrp, mkts: set()}

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
            else:
                mkt_key = "Other"
            mkt_counts[mkt_key] += 1

            # Parse numeric price
            p_val = 0.0
            m_p = re.search(r"[\d,]+(?:\.\d+)?", str(it.get("price", "")))
            if m_p:
                try:
                    p_val = float(m_p.group(0).replace(",", ""))
                except ValueError:
                    p_val = 0.0
            if p_val <= 0:
                p_val = 14.50  # conservative average counterfeit baseline

            total_cf_value += p_val

            # OEM Genuine Replacement Multiplier (Industry standard ~5.5x retail MSRP)
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

        # 2. Cross-Marketplace Threat Correlations (eBay vs. Chinese Suppliers)
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
                        "supplier": ch.get("seller") or "Chinese Supplier",
                        "platform": ch.get("marketplace", "aliexpress.com"),
                        "china_price": f"${ch_p:.2f}" if ch_p > 0 else "$2.50",
                        "spread": f"+${spread:.2f}",
                        "margin": f"+{margin_pct:,}%",
                        "threat": threat,
                        "ebay_url": eb.get("url", ""),
                        "china_url": ch.get("url", "")
                    })

                    if len(supply_chain_matches) >= 80:
                        break

        # ── KPI Header Banner (4 Metric Cards) ───────────────────────────────
        kpi_frame = tk.Frame(pad_f, bg=t["bg"])
        kpi_frame.pack(fill="x", pady=(0, 10))

        def _kpi(parent, icon, title, val, sub, accent_col):
            card = tk.Frame(parent, bg=t["panel"], padx=12, pady=8, highlightbackground=t["border"], highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=4)
            h_row = tk.Frame(card, bg=t["panel"])
            h_row.pack(fill="x")
            tk.Label(h_row, text=f"{icon} {title}", font=FONT_SM, bg=t["panel"], fg=t["subtext"]).pack(side="left")
            tk.Label(card, text=val, font=("Segoe UI", 15, "bold"), bg=t["panel"], fg=accent_col).pack(anchor="w", pady=(2, 0))
            tk.Label(card, text=sub, font=("Segoe UI", 8), bg=t["panel"], fg=t["subtext"]).pack(anchor="w")

        _kpi(kpi_frame, "🛡️", "INFRINGEMENTS IDENTIFIED", f"{len(all_items):,} Listings", f"{len(self.results):,} in current active session", t["accent"])
        _kpi(kpi_frame, "💰", "ESTIMATED MSRP PROTECTED", f"${total_msrp_est:,.2f}", f"${total_cf_value:,.2f} illegal GMV captured", t["success"])
        _kpi(kpi_frame, "🌐", "MULTI-MARKETPLACE REACH", f"{len([k for k, v in mkt_counts.items() if v > 0])} Platforms", f"eBay: {mkt_counts['eBay']} | Ali: {mkt_counts['AliExpress']} | Wish: {mkt_counts['Wish']} | Temu: {mkt_counts['Temu']}", t.get("accent2", t["accent"]))
        _kpi(kpi_frame, "🔗", "SUPPLY CHAINS LINKED", f"{len(supply_chain_matches)} Rogue Links", "Cross-marketplace dropship matches", t["warning"])

        # ── Notebook Navigation Tabs ──────────────────────────────────────────
        nb_frame = tk.Frame(pad_f, bg=t["bg"])
        nb_frame.pack(fill="both", expand=True)

        notebook = ttk.Notebook(nb_frame)
        notebook.pack(fill="both", expand=True)

        # ── TAB 1: Supply Chain & Arbitrage Matrix ────────────────────────────
        tab1 = tk.Frame(notebook, bg=t["bg"], padx=6, pady=6)
        notebook.add(tab1, text="🔗 Cross-Marketplace Supply Chain & Price Arbitrage Matrix")

        t1_head = tk.Frame(tab1, bg=t["bg"])
        t1_head.pack(fill="x", pady=(0, 6))
        tk.Label(t1_head, text="🕵️ Detected Cross-Marketplace Supply Chain Links (eBay Dropshippers ⟷ Upstream Chinese Manufacturers):",
                 font=FONT_HEAD, bg=t["bg"], fg=t["text"]).pack(side="left")

        tree1_frame = tk.Frame(tab1, bg=t["bg"])
        tree1_frame.pack(fill="both", expand=True)

        cols1 = ("keyword", "brand", "dropshipper", "ebay_price", "supplier", "platform", "china_price", "spread", "margin", "threat")
        tree1 = ttk.Treeview(tree1_frame, columns=cols1, show="headings", selectmode="browse")
        w1 = {"keyword": 130, "brand": 90, "dropshipper": 120, "ebay_price": 75, "supplier": 130, "platform": 95, "china_price": 75, "spread": 85, "margin": 80, "threat": 95}
        l1 = {"keyword": "Product Match", "brand": "Brand", "dropshipper": "eBay Dropshipper", "ebay_price": "eBay Price", "supplier": "Upstream Supplier", "platform": "Platform", "china_price": "Source Price", "spread": "Gross Spread", "margin": "Est. Margin", "threat": "Threat Level"}
        for c in cols1:
            tree1.heading(c, text=l1[c])
            tree1.column(c, width=w1.get(c, 90))
        self._style_tree(tree1)

        vsb1 = ttk.Scrollbar(tree1_frame, orient="vertical", command=tree1.yview)
        tree1.configure(yscrollcommand=vsb1.set)
        tree1.pack(side="left", fill="both", expand=True)
        vsb1.pack(side="right", fill="y")

        for m in supply_chain_matches:
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
        tk.Label(t2_head, text="📈 Brand Portfolio Enforcement Value & Threat Concentration:",
                 font=FONT_HEAD, bg=t["bg"], fg=t["text"]).pack(side="left")

        tree2_frame = tk.Frame(tab2, bg=t["bg"])
        tree2_frame.pack(fill="both", expand=True)

        cols2 = ("brand", "count", "avg_price", "msrp_protected", "platforms", "threat_rating")
        tree2 = ttk.Treeview(tree2_frame, columns=cols2, show="headings", selectmode="browse")
        w2 = {"brand": 140, "count": 100, "avg_price": 95, "msrp_protected": 150, "platforms": 160, "threat_rating": 110}
        l2 = {"brand": "Client / Brand", "count": "Seized Listings", "avg_price": "Avg Illegal Price", "msrp_protected": "Est. Genuine MSRP Protected", "platforms": "Marketplace Footprint", "threat_rating": "Priority Rating"}
        for c in cols2:
            tree2.heading(c, text=l2[c])
            tree2.column(c, width=w2.get(c, 100))
        self._style_tree(tree2)

        vsb2 = ttk.Scrollbar(tree2_frame, orient="vertical", command=tree2.yview)
        tree2.configure(yscrollcommand=vsb2.set)
        tree2.pack(side="left", fill="both", expand=True)
        vsb2.pack(side="right", fill="y")

        sorted_brands = sorted(brand_stats.items(), key=lambda x: x[1]["msrp_val"], reverse=True)
        for b_name, b_info in sorted_brands:
            avg_p = b_info["cf_val"] / b_info["count"] if b_info["count"] > 0 else 0.0
            rating = "🔥 HIGH PRIORITY" if b_info["msrp_val"] > 50000 else "⚡ ACTIVE TARGET"
            tree2.insert("", "end", values=(
                b_name,
                f"{b_info['count']:,} listings",
                f"${avg_p:.2f}",
                f"${b_info['msrp_val']:,.2f}",
                ", ".join(b_info["mkts"]),
                rating
            ))

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
                messagebox.showinfo("Export Complete", f"Saved Threat Intelligence & ROI Dossier to:\n{path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")

        def _copy_summary():
            summary_txt = (
                f"═══════════════════════════════════════════════════════════════════\n"
                f"       EXECUTIVE BRAND ENFORCEMENT & THREAT INTEL SUMMARY          \n"
                f"═══════════════════════════════════════════════════════════════════\n"
                f"Report Date           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Total Infringements   : {len(all_items):,} Listings\n"
                f"Estimated MSRP Seized : ${total_msrp_est:,.2f}\n"
                f"Illegal GMV Identified: ${total_cf_value:,.2f}\n"
                f"Marketplace Breakdown : eBay ({mkt_counts['eBay']}) | AliExpress ({mkt_counts['AliExpress']}) | Wish ({mkt_counts['Wish']}) | Temu ({mkt_counts['Temu']})\n"
                f"Rogue Supply Chains   : {len(supply_chain_matches)} Connected Dropship Links\n"
                f"═══════════════════════════════════════════════════════════════════\n"
            )
            self.clipboard_clear()
            self.clipboard_append(summary_txt)
            messagebox.showinfo("Copied", "Executive Summary copied to clipboard!")

        self._btn(btn_row, "📄 Export Threat Intel Dossier (.xlsx)", _export_threat_intel, accent=True).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "📋 Copy Executive Summary", _copy_summary).pack(side="left", padx=(0, 6))
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
        win.grab_set()

        # Center dialog relative to main window
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 880) // 2
        y = self.winfo_y() + (self.winfo_height() - 700) // 2
        win.geometry(f"+{max(10, x)}+{max(10, y)}")

        pad_f = tk.Frame(win, bg=t["bg"], padx=20, pady=16)
        pad_f.pack(fill="both", expand=True)

        # ── Header ───────────────────────────────────────────────────────────
        head_f = tk.Frame(pad_f, bg=t["bg"])
        head_f.pack(fill="x", pady=(0, 10))

        tk.Label(head_f, text="🔺 Valknut Brand Intelligence",
                 font=("Segoe UI", 16, "bold"), bg=t["bg"], fg=t["accent"]).pack(anchor="w")

        tk.Label(head_f, text="Enterprise Cross-Marketplace Threat Harvester & Supply Chain Defense Suite",
                 font=FONT_SM, bg=t["bg"], fg=t["subtext"]).pack(anchor="w", pady=(2, 0))

        div = tk.Frame(pad_f, bg=t["border"], height=1)
        div.pack(fill="x", pady=(6, 10))

        # ── Notebook / Tabs ──────────────────────────────────────────────────
        style = ttk.Style(win)
        style.theme_use("clam")
        style.configure("About.TNotebook", background=t["bg"], borderwidth=0)
        style.configure("About.TNotebook.Tab", background=t["panel"], foreground=t["text"],
                        padding=[16, 8], font=("Segoe UI", 9, "bold"))
        style.map("About.TNotebook.Tab",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", "#ffffff" if t["bg"] != "#08080a" else "#000000")])

        nb = ttk.Notebook(pad_f, style="About.TNotebook")
        nb.pack(fill="both", expand=True)

        # ── TAB 1: Ethos & Architecture ──────────────────────────────────────
        tab_ethos = tk.Frame(nb, bg=t["panel"], padx=16, pady=12)
        nb.add(tab_ethos, text="🔺 The Valknut Ethos & Architecture")

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
        narrative_hdr = tk.Label(ethos_scroll_frame, text="The Symbol: The Shield & The Spear",
                                 font=("Segoe UI", 11, "bold"), bg=t["panel"], fg=t["accent"])
        narrative_hdr.pack(anchor="w", padx=4, pady=(0, 4))
        narrative_hdr.bind("<MouseWheel>", _on_mousewheel)

        narrative_txt = (
            "Named after the legendary Norse Valknut (3 interlocking Borromean triangles with 9 vertices), "
            "this platform embodies both an impenetrable shield for corporate intellectual property and a "
            "high-precision spear for active enforcement. If you pull on one triangle, the entire structure tightens."
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
            ("🔍", "Triangle 1: Reconnaissance", "Automated stealth sweeps across global marketplaces with zero bot detection."),
            ("🛡",  "Triangle 2: Threat Intelligence", "Reconstructing supply chains, mapping dropship arbitrage margins & A2C2 Recidivism."),
            ("⚡", "Triangle 3: Rapid Enforcement", "1-click legal evidence dossiers, bulk categorization & dismantling upstream factories."),
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
            ("1. Vigilance", "360° global marketplace surveillance"),
            ("2. Stealth", "Undetectable anti-bot evasion"),
            ("3. Precision", "Zero-false-positive filtering"),
            ("4. Traceability", "Connecting domestic links to China factories"),
            ("5. Tenacity", "Tracking repeat offenders across rebrands"),
            ("6. Integrity", "Courtroom-ready evidentiary chain of custody"),
            ("7. Velocity", "Harvesting thousands of listings in seconds"),
            ("8. Impact", "Quantified client MSRP revenue protected"),
            ("9. Elimination", "Permanent takedown of illicit trade networks"),
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
                             font=FONT_SM, relief="flat", wrap="word", padx=10, pady=8)
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


if __name__ == "__main__":
    app = EbayTool()
    app.mainloop()
