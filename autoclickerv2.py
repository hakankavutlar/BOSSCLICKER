import customtkinter as ctk
import tkinter as tk
import threading
import time
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener

# --- YENİ TEMA RENKLERİ (GÖRSELE UYGUN) ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#0b0e1a"        # Daha koyu arka plan
COLOR_PANEL = "#111221"     # Panel rengi
COLOR_KEY = "#181a29"       # Klavye tuş rengi
COLOR_ACCENT = "#00eaff"    # Neon Mavi (Cyan) - Daha parlak
COLOR_ACCENT_SOFT = "#2f33ff"  # Yumuşak neon
COLOR_ACCENT_2 = "#fc00ff"  # Neon Mor
COLOR_TEXT = "#e6e6ff"      # Açık mavi-beyaz metin
COLOR_TEXT_DIM = "#8888aa"
COLOR_HOVER = "#23264a"     # Tuş üzerine gelince
COLOR_BORDER = "#2b2f55"    # Çerçeve rengi

class ModernAutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Neon Auto Clicker Pro")
        self.geometry("1100x700")
        self.configure(fg_color=COLOR_BG)
        self.resizable(False, False)

        # Değişkenler
        self.target_key = "RMB"  # Varsayılan tıklanacak tuş
        self.trigger_key = "R"   # Başlatma tuşu
        self.click_mode = tk.StringVar(value="interval") # interval veya cps
        self.is_running = False
        self.listening_for_trigger = False
        
        # Kontrolcüler
        self.mouse_ctrl = MouseController()
        self.keyboard_ctrl = KeyboardController()
        self.click_thread = None
        
        # UI Elemanlarını saklamak için
        self.key_buttons = {}  # Klavye tuşlarını sakla
        self.mouse_parts = {}  # Mouse parçalarını sakla

        # Arayüz Kurulumu
        self.setup_ui()
        
        # Global Klavye Dinleyicisi (Başlat/Durdur için)
        self.listener = KeyboardListener(on_press=self.on_global_press)
        self.listener.start()

    def setup_ui(self):
        # --- SOL MENÜ (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLOR_PANEL)
        self.sidebar.pack(side="left", fill="y")
        
        # Logo
        ctk.CTkLabel(self.sidebar, text="NEON", font=("Segoe UI", 22, "bold"), 
                    text_color=COLOR_ACCENT).pack(pady=30)
        ctk.CTkLabel(self.sidebar, text="AUTOCLICKER", font=("Segoe UI", 12), 
                    text_color=COLOR_TEXT_DIM).pack(pady=(0, 30))
        
        # Stil butonları
        self.btn_style1 = ctk.CTkButton(self.sidebar, text="Stil 1", fg_color="transparent", 
                                       border_width=1, border_color=COLOR_ACCENT_SOFT,
                                       hover_color=COLOR_HOVER, font=("Segoe UI", 12))
        self.btn_style1.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="+ Yeni Stil Ekle", fg_color="transparent", 
                     text_color="#aaa", hover_color="#333").pack(pady=10, side="bottom")

        # --- ANA ALAN ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        # 1. BÖLÜM: ÜST SEÇİMLER
        self.frame_top = ctk.CTkFrame(self.main_area, fg_color=COLOR_PANEL, 
                                     corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.frame_top.pack(fill="x", pady=(0, 15), ipady=10)

        # Seçili Tuş Göstergesi
        ctk.CTkLabel(self.frame_top, text="SEÇİLİ TUŞ :", font=("Segoe UI", 12, "bold"),
                    text_color=COLOR_TEXT).pack(side="left", padx=(20, 10))
        self.lbl_selected_target = ctk.CTkButton(self.frame_top, text=self.target_key, width=80, 
                                                 fg_color="transparent", border_width=2, 
                                                 border_color=COLOR_ACCENT,
                                                 state="disabled", text_color=COLOR_ACCENT,
                                                 font=("Segoe UI", 12, "bold"))
        self.lbl_selected_target.pack(side="left")

        # Açma Tuşu (Trigger) Atama
        ctk.CTkLabel(self.frame_top, text="AÇMA TUŞU :", font=("Segoe UI", 12, "bold"),
                    text_color=COLOR_TEXT).pack(side="left", padx=(40, 10))
        self.btn_trigger = ctk.CTkButton(self.frame_top, text=self.trigger_key, width=80,
                                         fg_color="transparent", border_width=2, 
                                         border_color=COLOR_ACCENT_SOFT,
                                         hover_color=COLOR_HOVER, text_color=COLOR_TEXT,
                                         font=("Segoe UI", 12, "bold"),
                                         command=self.wait_for_trigger_input)
        self.btn_trigger.pack(side="left")

        # Başlat Butonu
        self.btn_start = ctk.CTkButton(self.frame_top, text="BAŞLAT", 
                                      fg_color=COLOR_ACCENT_2, hover_color="#b000b2", 
                                      width=120, font=("Segoe UI", 12, "bold"),
                                      command=self.toggle_running)
        self.btn_start.pack(side="right", padx=20)

        # 2. BÖLÜM: ZAMANLAMA AYARLARI
        self.frame_settings = ctk.CTkFrame(self.main_area, fg_color=COLOR_PANEL, 
                                          corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.frame_settings.pack(fill="x", pady=(0, 15), ipady=15)

        # Interval Modu
        self.radio_interval = ctk.CTkRadioButton(self.frame_settings, text="", 
                                                variable=self.click_mode, value="interval", 
                                                width=0, border_color=COLOR_ACCENT, 
                                                fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_SOFT)
        self.radio_interval.grid(row=0, column=0, padx=(20, 5), pady=10)
        
        self.entry_interval = ctk.CTkEntry(self.frame_settings, width=80, 
                                          border_color=COLOR_ACCENT_2, fg_color=COLOR_KEY,
                                          text_color=COLOR_TEXT, font=("Segoe UI", 11))
        self.entry_interval.insert(0, "4")
        self.entry_interval.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(self.frame_settings, text="X SANİYEDE BİR TIKLA (Limit: 0.01 - 99999)",
                    text_color=COLOR_TEXT_DIM, font=("Segoe UI", 11)).grid(row=0, column=2, padx=10, sticky="w")

        # CPS Modu
        self.radio_cps = ctk.CTkRadioButton(self.frame_settings, text="", 
                                           variable=self.click_mode, value="cps", 
                                           width=0, border_color=COLOR_ACCENT, 
                                           fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_SOFT)
        self.radio_cps.grid(row=0, column=4, padx=(40, 5))
        
        self.entry_cps = ctk.CTkEntry(self.frame_settings, width=80, 
                                     border_color=COLOR_BORDER, fg_color=COLOR_KEY,
                                     text_color=COLOR_TEXT_DIM, font=("Segoe UI", 11))
        self.entry_cps.insert(0, "10")
        self.entry_cps.grid(row=0, column=5, padx=5)
        
        ctk.CTkLabel(self.frame_settings, text="CPM İLE TIKLA (Limit: 0 - 23.1)",
                    text_color=COLOR_TEXT_DIM, font=("Segoe UI", 11)).grid(row=0, column=6, padx=10, sticky="w")

        # 3. BÖLÜM: GÖRSEL SEÇİCİLER (MOUSE & KLAVYE)
        self.frame_visuals = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.frame_visuals.pack(expand=True, fill="both")

        # Sol: Mouse Çizimi
        self.setup_mouse_visual(self.frame_visuals)
        
        # Sağ: Klavye Çizimi
        self.setup_keyboard_visual(self.frame_visuals)

    def setup_mouse_visual(self, parent):
        """Gelişmiş mouse görseli"""
        frame = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=18, 
                            border_width=1, border_color=COLOR_BORDER, width=300)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)
        
        ctk.CTkLabel(frame, text="MOUSE KONTROL", font=("Segoe UI", 12, "bold"),
                    text_color=COLOR_TEXT).pack(side="top", pady=(15, 5))
        
        ctk.CTkLabel(frame, text="Tıklanacak tuşu seçin", font=("Segoe UI", 10),
                    text_color=COLOR_TEXT_DIM).pack(side="top", pady=(0, 15))

        # Canvas çizimi
        canvas_frame = ctk.CTkFrame(frame, fg_color="transparent")
        canvas_frame.pack(expand=True, pady=10)
        
        self.mouse_canvas = tk.Canvas(canvas_frame, width=240, height=350, 
                                     bg=COLOR_PANEL, highlightthickness=0)
        self.mouse_canvas.pack(pady=10)

        # Mouse gövdesi - daha gerçekçi tasarım
        # Sol Tık (LMB)
        lmb_id = self.create_neon_rounded_rect(self.mouse_canvas, 20, 20, 100, 120, 12, 
                                              fill=COLOR_KEY, outline=COLOR_BORDER, 
                                              glow_color=COLOR_BORDER, tags="LMB")
        self.mouse_canvas.create_text(60, 70, text="LMB", fill=COLOR_TEXT, 
                                      font=("Segoe UI", 10, "bold"), state="disabled")
        
        # Sağ Tık (RMB) - Varsayılan seçili (neon efekti)
        rmb_id = self.create_neon_rounded_rect(self.mouse_canvas, 110, 20, 190, 120, 12,
                                              fill=COLOR_ACCENT, outline=COLOR_ACCENT,
                                              glow_color=COLOR_ACCENT, tags="RMB")
        self.mouse_canvas.create_text(150, 70, text="RMB", fill="#0b0e1a", 
                                      font=("Segoe UI", 10, "bold"), state="disabled")
        
        # Scroll Tekerlek (Wheel) - Modern tasarım
        wheel_id = self.mouse_canvas.create_oval(95, 130, 115, 170, fill=COLOR_KEY, 
                                                outline=COLOR_BORDER, width=2, tags="WHEEL")
        
        # Gövde - Modern mouse şekli
        body_points = [20, 120, 190, 120, 190, 280, 150, 320, 60, 320, 20, 280]
        body_id = self.mouse_canvas.create_polygon(body_points, fill=COLOR_KEY, 
                                                  outline=COLOR_BORDER, width=2, 
                                                  smooth=True)
        
        # Yan Tuşlar - Öne çıkan tasarım
        side1_id = self.create_neon_rounded_rect(self.mouse_canvas, 5, 160, 20, 210, 5,
                                                fill=COLOR_KEY, outline=COLOR_BORDER,
                                                glow_color=COLOR_BORDER, tags="SIDE1")
        side2_id = self.create_neon_rounded_rect(self.mouse_canvas, 5, 220, 20, 270, 5,
                                                fill=COLOR_KEY, outline=COLOR_BORDER,
                                                glow_color=COLOR_BORDER, tags="SIDE2")
        
        # Scroll butonları (üst/alt)
        scroll_up_id = self.mouse_canvas.create_rectangle(85, 80, 125, 100, 
                                                         fill=COLOR_KEY, 
                                                         outline=COLOR_BORDER, 
                                                         width=2, tags="SCROLL_UP")
        scroll_down_id = self.mouse_canvas.create_rectangle(85, 100, 125, 120, 
                                                           fill=COLOR_KEY, 
                                                           outline=COLOR_BORDER, 
                                                           width=2, tags="SCROLL_DOWN")
        
        # Etiketler
        self.mouse_canvas.create_text(60, 140, text="Sol Tık", fill=COLOR_TEXT_DIM, 
                                      font=("Segoe UI", 8))
        self.mouse_canvas.create_text(150, 140, text="Sağ Tık", fill=COLOR_TEXT_DIM, 
                                      font=("Segoe UI", 8))
        self.mouse_canvas.create_text(105, 185, text="Tekerlek", fill=COLOR_TEXT_DIM, 
                                      font=("Segoe UI", 8))
        
        # Etkileşimler
        mouse_tags = ["LMB", "RMB", "WHEEL", "SIDE1", "SIDE2", "SCROLL_UP", "SCROLL_DOWN"]
        for tag in mouse_tags:
            self.mouse_canvas.tag_bind(tag, "<Enter>", lambda e, t=tag: self.on_mouse_hover(t, True))
            self.mouse_canvas.tag_bind(tag, "<Leave>", lambda e, t=tag: self.on_mouse_hover(t, False))
            self.mouse_canvas.tag_bind(tag, "<Button-1>", lambda e, t=tag: self.select_target(t))

    def create_neon_rounded_rect(self, canvas, x1, y1, x2, y2, r, **kwargs):
        """Neon glow efekti için yuvarlak dikdörtgen"""
        # Glow efekti (alt katman)
        glow_color = kwargs.pop('glow_color', COLOR_ACCENT)
        glow_width = kwargs.get('width', 2) + 2
        
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        
        # Glow katmanı
        canvas.create_polygon(points, fill="", outline=glow_color, width=glow_width, 
                            smooth=True, tags=f"{kwargs.get('tags', '')}_glow")
        
        # Ana katman
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def setup_keyboard_visual(self, parent):
        """Gelişmiş klavye görseli"""
        frame = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=18,
                            border_width=1, border_color=COLOR_BORDER)
        frame.pack(side="right", fill="both", expand=True, pady=5)
        
        ctk.CTkLabel(frame, text="KLAVYE KONTROL", font=("Segoe UI", 12, "bold"),
                    text_color=COLOR_TEXT).pack(side="top", pady=(15, 5))
        
        ctk.CTkLabel(frame, text="Tıklanacak tuşu seçin", font=("Segoe UI", 10),
                    text_color=COLOR_TEXT_DIM).pack(side="top", pady=(0, 10))

        # Klavye Kasa (Shell)
        keyboard_shell = ctk.CTkFrame(frame, fg_color="#111221", corner_radius=12,
                                     border_width=1, border_color="#2b2f55")
        keyboard_shell.pack(padx=25, pady=15, fill="both", expand=True)

        # Ana Klavye Container
        kb_container = ctk.CTkFrame(keyboard_shell, fg_color="transparent")
        kb_container.pack(expand=True, padx=15, pady=15)

        # Klavye düzeni - Daha gerçekçi
        keys_layout = [
            ["ESC", "F1", "F2", "F3", "F4", "F5", "F6", "PRT"],
            ["~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BKSP"],
            ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
            ["CAPS", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "ENTER"],
            ["SHIFT", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "SHIFT"],
            ["CTRL", "WIN", "ALT", "SPACE", "ALT", "FN", "CTRL"]
        ]

        # Special keys that need different styling
        special_keys = ["ESC", "TAB", "CAPS", "SHIFT", "ENTER", "BKSP", "CTRL", "WIN", "ALT", "FN", "SPACE"]
        accent_keys = ["ESC", "FN", "ENTER"]
        
        # Ana klavye satırları
        for r, row in enumerate(keys_layout):
            row_frame = ctk.CTkFrame(kb_container, fg_color="transparent", height=40)
            row_frame.pack(pady=2)
            
            for key in row:
                # Tuş boyutları
                if key in ["SPACE"]:
                    width = 180
                    height = 38
                elif key in ["ENTER", "BKSP", "TAB", "CAPS", "SHIFT"]:
                    width = 70
                    height = 38
                elif key in ["CTRL", "WIN", "ALT", "FN"]:
                    width = 55
                    height = 38
                else:
                    width = 38
                    height = 38
                
                # Tuş renkleri
                if key in accent_keys:
                    fg_color = COLOR_ACCENT_SOFT
                    text_color = "#0b0e1a"
                    border_color = COLOR_ACCENT
                elif key in special_keys:
                    fg_color = "#1a1c33"
                    text_color = COLOR_TEXT
                    border_color = COLOR_ACCENT_SOFT
                else:
                    fg_color = COLOR_KEY
                    text_color = COLOR_TEXT
                    border_color = COLOR_BORDER
                
                # Tuş oluştur
                btn = ctk.CTkButton(
                    row_frame,
                    text=key,
                    width=width,
                    height=height,
                    fg_color=fg_color,
                    hover_color=COLOR_HOVER,
                    border_width=1,
                    border_color=border_color,
                    corner_radius=6,
                    font=("Segoe UI", 9, "bold"),
                    text_color=text_color,
                    command=lambda k=key: self.select_target_keyboard(k)
                )
                btn.pack(side="left", padx=1, pady=1)
                
                # Tuşu sakla
                self.key_buttons[key] = btn
                
                # Hover efektleri için bağla
                btn.bind("<Enter>", lambda e, b=btn, k=key: self.on_key_hover(b, k, True))
                btn.bind("<Leave>", lambda e, b=btn, k=key: self.on_key_hover(b, k, False))

    # --- GÖRSEL FONKSİYONLARI ---

    def on_mouse_hover(self, tag, entering):
        """Mouse parçaları üzerine gelince neon efekti"""
        if entering and tag != self.target_key:
            # Glow efekti ver
            self.mouse_canvas.itemconfig(tag, outline=COLOR_ACCENT_SOFT)
            # Glow katmanını aktif et
            glow_tag = f"{tag}_glow"
            if glow_tag in self.mouse_canvas.get_tags():
                self.mouse_canvas.itemconfig(glow_tag, outline=COLOR_ACCENT, width=4)
        else:
            if tag != self.target_key:
                self.mouse_canvas.itemconfig(tag, outline=COLOR_BORDER)
                glow_tag = f"{tag}_glow"
                if glow_tag in self.mouse_canvas.get_tags():
                    self.mouse_canvas.itemconfig(glow_tag, outline=COLOR_BORDER, width=2)

    def on_key_hover(self, btn, key, entering):
        """Klavye tuşları üzerine gelince efekt"""
        if entering and key != self.target_key:
            btn.configure(border_color=COLOR_ACCENT_SOFT)
        else:
            if key != self.target_key:
                # Tuş tipine göre orijinal rengine dön
                if key in ["ESC", "FN", "ENTER"]:
                    btn.configure(border_color=COLOR_ACCENT)
                elif key in ["TAB", "CAPS", "SHIFT", "BKSP", "CTRL", "WIN", "ALT", "SPACE"]:
                    btn.configure(border_color=COLOR_ACCENT_SOFT)
                else:
                    btn.configure(border_color=COLOR_BORDER)

    def select_target(self, key_name):
        """Mouse tuşu seçimi"""
        # Eski seçiliyi normale döndür
        if self.target_key in ["LMB", "RMB", "WHEEL", "SIDE1", "SIDE2", "SCROLL_UP", "SCROLL_DOWN"]:
            self.mouse_canvas.itemconfig(self.target_key, fill=COLOR_KEY, outline=COLOR_BORDER)
            glow_tag = f"{self.target_key}_glow"
            if glow_tag in self.mouse_canvas.get_tags():
                self.mouse_canvas.itemconfig(glow_tag, outline=COLOR_BORDER, width=2)
        
        # Yeni seçiliyi parlat
        self.target_key = key_name
        self.lbl_selected_target.configure(text=key_name)
        
        # Mouse parçaları için neon efekti
        if key_name in ["LMB", "RMB", "WHEEL", "SIDE1", "SIDE2", "SCROLL_UP", "SCROLL_DOWN"]:
            self.mouse_canvas.itemconfig(key_name, fill=COLOR_ACCENT, outline=COLOR_ACCENT)
            glow_tag = f"{key_name}_glow"
            if glow_tag in self.mouse_canvas.get_tags():
                self.mouse_canvas.itemconfig(glow_tag, outline=COLOR_ACCENT, width=4)

    def select_target_keyboard(self, key_name):
        """Klavye tuşu seçimi"""
        # Eski seçiliyi normale döndür
        if self.target_key in self.key_buttons:
            old_btn = self.key_buttons[self.target_key]
            # Tuş tipine göre orijinal renk
            if self.target_key in ["ESC", "FN", "ENTER"]:
                old_btn.configure(fg_color=COLOR_ACCENT_SOFT, text_color="#0b0e1a", border_color=COLOR_ACCENT)
            elif self.target_key in ["TAB", "CAPS", "SHIFT", "BKSP", "CTRL", "WIN", "ALT", "SPACE"]:
                old_btn.configure(fg_color="#1a1c33", text_color=COLOR_TEXT, border_color=COLOR_ACCENT_SOFT)
            else:
                old_btn.configure(fg_color=COLOR_KEY, text_color=COLOR_TEXT, border_color=COLOR_BORDER)
        
        # Yeni seçiliyi parlat
        self.target_key = key_name
        self.lbl_selected_target.configure(text=key_name)
        
        # Yeni tuşa neon efekti
        if key_name in self.key_buttons:
            btn = self.key_buttons[key_name]
            btn.configure(fg_color=COLOR_ACCENT, text_color="#0b0e1a", border_color=COLOR_ACCENT)

    # --- MANTIK FONKSİYONLARI (Aynı kaldı) ---

    def wait_for_trigger_input(self):
        """Açma tuşu için bekleme modu"""
        self.btn_trigger.configure(text="TUŞA BAS...", text_color="red", 
                                 border_color="red", font=("Segoe UI", 12, "bold"))
        self.listening_for_trigger = True

    def on_global_press(self, key):
        """Tüm klavye olaylarını dinler"""
        try:
            key_char = key.char.upper()
        except AttributeError:
            key_char = str(key).replace("Key.", "").upper()
            
            # Özel tuşlar için dönüşüm
            special_keys = {
                "SPACE": "SPACE",
                "ENTER": "ENTER",
                "BACKSPACE": "BKSP",
                "TAB": "TAB",
                "SHIFT": "SHIFT",
                "CTRL": "CTRL",
                "ALT": "ALT",
                "ESC": "ESC"
            }
            key_char = special_keys.get(key_char, key_char)

        # Tuş atama modu
        if self.listening_for_trigger:
            self.trigger_key = key_char
            self.btn_trigger.configure(text=self.trigger_key, 
                                     text_color=COLOR_TEXT,
                                     border_color=COLOR_ACCENT_SOFT,
                                     font=("Segoe UI", 12, "bold"))
            self.listening_for_trigger = False
            return

        # Başlat / Durdur
        if key_char == self.trigger_key:
            self.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.btn_start.configure(text="BAŞLAT", fg_color=COLOR_ACCENT_2,
                                   hover_color="#b000b2")
            if self.click_thread:
                self.click_thread.join(0.1)
        else:
            if self.validate_inputs():
                self.is_running = True
                self.btn_start.configure(text="DURDUR", fg_color="#ff004f",
                                       hover_color="#cc003d")
                self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
                self.click_thread.start()

    def validate_inputs(self):
        """Kullanıcı girdilerini kontrol et"""
        try:
            if self.click_mode.get() == "interval":
                val = float(self.entry_interval.get())
                if val < 0.01: val = 0.01
                if val > 99999: val = 99999
                self.entry_interval.delete(0, tk.END)
                self.entry_interval.insert(0, str(val))
            else: # cps
                val = float(self.entry_cps.get())
                if val < 0: val = 0
                if val > 23.1: val = 23.1
                self.entry_cps.delete(0, tk.END)
                self.entry_cps.insert(0, str(val))
            return True
        except ValueError:
            tk.messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin!")
            return False

    def click_loop(self):
        """Arka planda çalışan tıklama döngüsü"""
        while self.is_running:
            # 1. Bekleme Süresi Hesabı
            if self.click_mode.get() == "interval":
                delay = float(self.entry_interval.get())
            else:
                cps = float(self.entry_cps.get())
                delay = 1.0 / cps if cps > 0 else 1.0

            # 2. Tıklama İşlemi
            if self.target_key == "LMB":
                self.mouse_ctrl.click(Button.left)
            elif self.target_key == "RMB":
                self.mouse_ctrl.click(Button.right)
            elif self.target_key == "WHEEL":
                self.mouse_ctrl.click(Button.middle)
            elif self.target_key in ["SCROLL_UP", "SCROLL_DOWN"]:
                # Scroll işlemi
                self.mouse_ctrl.scroll(1 if self.target_key == "SCROLL_UP" else -1)
            elif len(self.target_key) == 1 or self.target_key in self.key_buttons:
                # Klavye tuşu
                try:
                    self.keyboard_ctrl.press(self.target_key.lower())
                    self.keyboard_ctrl.release(self.target_key.lower())
                except:
                    # Özel tuşlar için
                    pass
            
            # 3. Uyuma
            time.sleep(delay)

if __name__ == "__main__":
    app = ModernAutoClicker()
    app.mainloop()