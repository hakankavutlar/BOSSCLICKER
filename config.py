# config.py
import customtkinter as ctk

# RENK AYARLARI
COLOR_KEY = "#181a29"       
COLOR_BORDER = "#2b2f55"    
COLOR_BG = "#13141f"        
COLOR_PANEL = "#1c1e2e"     
COLOR_ACCENT = "#00dbde"    
COLOR_ACCENT_2 = "#fc00ff"  
COLOR_TEXT = "#ffffff"
COLOR_TEXT_DIM = "#888888"
COLOR_HOVER = "#2d3047"     
COLOR_ACTIVE = "#00dbde"  
COLOR_ACCENT_SOFT = "#2f33ff"  

# KLAVYE DÜZENLERİ
KEYBOARD_LAYOUTS = {
    "Türkçe Q": [
        ["ESC", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
        ["~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BKSP"],
        ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "Ğ", "Ü", "*"],
        ["CAPS", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Ş", "İ", "ENTER"],
        ["SHIFT", "<", "Z", "X", "C", "V", "B", "N", "M", "Ö", "Ç", ".", "SHIFT"],
        ["CTRL", "WIN", "ALT", "SPACE", "ALTGR", "FN", "CTRL"]
    ],
    "İngilizce Q": [
        ["ESC", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
        ["~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BKSP"],
        ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
        ["CAPS", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "ENTER"],
        ["SHIFT", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "SHIFT"],
        ["CTRL", "WIN", "ALT", "SPACE", "ALT", "FN", "CTRL"]
    ],
    "Türkçe F": [
        ["ESC", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
        ["~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BKSP"],
        ["TAB", "F", "G", "Ğ", "I", "O", "D", "R", "N", "H", "P", "Q", "W", "\\"],
        ["CAPS", "U", "İ", "E", "A", "Ü", "T", "K", "M", "L", "Y", "Ş", "ENTER"],
        ["SHIFT", "J", "Ö", "V", "C", "Ç", "Z", "S", "B", ".", "/", "SHIFT"],
        ["CTRL", "WIN", "ALT", "SPACE", "ALTGR", "FN", "CTRL"]
    ],
    "İngilizce F": [
        ["ESC", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
        ["~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BKSP"],
        ["TAB", "F", "G", "H", "J", "K", "L", ":", "'", "[", "]", "\\", ""],
        ["CAPS", "D", "S", "A", "U", "I", "E", "O", ",", ".", "/", "ENTER", ""],
        ["SHIFT", "Z", "X", "C", "V", "B", "N", "M", "<", ">", "?", "SHIFT", ""],
        ["CTRL", "WIN", "ALT", "SPACE", "ALT", "FN", "CTRL", "", "", "", "", ""]
    ]
}

# ÖZEL TUŞLAR
SPECIAL_KEYS = ["ESC", "TAB", "CAPS", "SHIFT", "ENTER", "BKSP", "CTRL", "WIN", "ALT", "ALTGR", "FN", "SPACE"]

# TUŞ BOYUTLARI
KEY_SIZES = {
    "SPACE": {"width": 200, "height": 38},
    "ENTER": {"width": 90, "height": 38},
    "BKSP": {"width": 90, "height": 38},
    "TAB": {"width": 65, "height": 38},
    "CAPS": {"width": 65, "height": 38},
    "SHIFT": {"width": 65, "height": 38},
    "CTRL": {"width": 65, "height": 38},
    "WIN": {"width": 65, "height": 38},
    "ALT": {"width": 65, "height": 38},
    "ALTGR": {"width": 65, "height": 38},
    "FN": {"width": 65, "height": 38},
    "ESC": {"width": 60, "height": 38},
    "DEFAULT": {"width": 38, "height": 38}
}

# ÖZEL TUŞ HARİTASI
SPECIAL_KEYS_MAP = {
    "SPACE": "space",
    "ENTER": "enter",
    "ESC": "esc",
    "TAB": "tab",
    "SHIFT": "shift",
    "CTRL": "ctrl",
    "ALT": "alt",
    "ALTGR": "alt_gr",
    "BKSP": "backspace",
    "CAPS": "caps_lock",
    "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4",
    "F5": "f5", "F6": "f6", "F7": "f7", "F8": "f8",
    "F9": "f9", "F10": "f10", "F11": "f11", "F12": "f12",
}

# TÜRKÇE KARAKTERLER
TURKISH_CHARS = {
    "Ğ": "g", "Ü": "u", "Ş": "s", 
    "İ": "i", "Ö": "o", "Ç": "c"
}

def setup_theme():
    """Tema ayarlarını yapar"""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")