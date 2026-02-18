# app.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener
from config import (
    COLOR_KEY, COLOR_BORDER, COLOR_BG, COLOR_PANEL, 
    COLOR_ACCENT, COLOR_ACCENT_2, COLOR_TEXT, COLOR_TEXT_DIM,
    COLOR_HOVER, COLOR_ACTIVE, KEYBOARD_LAYOUTS, SPECIAL_KEYS,
    KEY_SIZES, SPECIAL_KEYS_MAP, TURKISH_CHARS
)

class ModernAutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Pencere Ayarları
        self.title("BOSSCLICKER")
        self.geometry("1100x700")
        self.configure(fg_color=COLOR_BG)
        self.resizable(False, False)
        
        # Değişkenler
        self.key_buttons = {}
        self.target_key = None
        self.trigger_key = None
        self.click_mode = tk.StringVar(value="interval")
        self.is_running = False
        self.listening_for_trigger = False
        self.selected_keyboard_layout = "Türkçe Q"
        
        # Kontrolcüler
        self.mouse_ctrl = MouseController()
        self.keyboard_ctrl = KeyboardController()
        self.click_thread = None
        
        # Klavye dinleyicisi - başlangıçta None
        self.keyboard_listener = None
        
        # Arayüz Kurulumu
        self.setup_ui()
        
        # Global klavye dinleyicisini başlat
        self.start_keyboard_listener()
        
        # Pencere kapatıldığında dinleyiciyi durdur
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # --- SOL MENÜ ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLOR_PANEL)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="LOGO", font=("Arial", 20, "bold"), 
                     text_color="#7b68ee").pack(pady=30)
        
        ctk.CTkButton(self.sidebar, text="Stil 1", fg_color="transparent", 
                     border_width=1, border_color=COLOR_ACCENT_2).pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="+ Yeni Stil Ekle", fg_color="transparent", 
                     text_color="#aaa", hover_color="#333").pack(side="bottom", pady=20)
        
        # --- ANA ALAN ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", expand=True, fill="both", padx=20, pady=20)
        
        # ÜST BÖLÜM
        self.setup_top_section()
        
        # ORTA BÖLÜM - GÖRSEL SEÇİCİLER
        self.setup_visual_selectors()
        
        # ALT BÖLÜM - KLAVYE SEÇİCİ
        self.setup_keyboard_selector()
        
        # Focus yönetimi
        self.setup_focus_management()
    
    def setup_top_section(self):
        frame_top = ctk.CTkFrame(self.main_area, fg_color=COLOR_PANEL, corner_radius=15)
        frame_top.pack(fill="x", pady=(0, 15), ipady=10)
        
        # Hedef tuş göstergesi
        ctk.CTkLabel(frame_top, text="Seçili Tuş :", font=("Arial", 12, "bold")
                    ).pack(side="left", padx=(20, 10))
        
        self.lbl_selected_target = ctk.CTkButton(
            frame_top, text="Lütfen Seçiniz", width=120,
            fg_color="transparent", border_width=2, border_color=COLOR_BORDER,
            state="disabled", text_color=COLOR_TEXT_DIM, font=("Arial", 11)
        )
        self.lbl_selected_target.pack(side="left")
        
        # Trigger tuşu
        ctk.CTkLabel(frame_top, text="Açma Tuşu :", font=("Arial", 12, "bold")
                    ).pack(side="left", padx=(40, 10))
        
        self.btn_trigger = ctk.CTkButton(
            frame_top, text="Lütfen Seçiniz", width=120,
            fg_color="transparent", border_width=2, border_color=COLOR_BORDER,
            hover_color=COLOR_HOVER, text_color=COLOR_TEXT_DIM,
            font=("Arial", 11), command=self.wait_for_trigger_input
        )
        self.btn_trigger.pack(side="left")
        
        # Başlat/Durdur butonu
        self.btn_start = ctk.CTkButton(
            frame_top, text="BAŞLAT", fg_color=COLOR_ACCENT_2,
            hover_color="#b000b2", width=100, command=self.toggle_running
        )
        self.btn_start.pack(side="right", padx=20)
        
        # Ayarlar bölümü
        self.setup_settings_section()
    
    def setup_settings_section(self):
        frame_settings = ctk.CTkFrame(self.main_area, fg_color=COLOR_PANEL, corner_radius=15)
        frame_settings.pack(fill="x", pady=(0, 15), ipady=15)
        
        # Interval modu
        self.radio_interval = ctk.CTkRadioButton(
            frame_settings, text="", variable=self.click_mode, value="interval",
            border_color=COLOR_ACCENT, fg_color=COLOR_ACCENT, width=20
        )
        self.radio_interval.grid(row=0, column=0, padx=(20, 5), pady=10)
        
        self.entry_interval = ctk.CTkEntry(
            frame_settings, width=80, border_color=COLOR_ACCENT_2,
            placeholder_text="4"
        )
        self.entry_interval.grid(row=0, column=1, padx=5)
        self.entry_interval.insert(0, "4")
        
        ctk.CTkLabel(frame_settings, text="SANİYEDE BİR TIKLA (0.01 - 99999)"
                    ).grid(row=0, column=2, padx=10, sticky="w")
        
        # CPS modu
        self.radio_cps = ctk.CTkRadioButton(
            frame_settings, text="", variable=self.click_mode, value="cps",
            border_color=COLOR_ACCENT, fg_color=COLOR_ACCENT, width=20
        )
        self.radio_cps.grid(row=0, column=3, padx=(40, 5))
        
        self.entry_cps = ctk.CTkEntry(
            frame_settings, width=80, border_color="#555",
            placeholder_text="10"
        )
        self.entry_cps.grid(row=0, column=4, padx=5)
        self.entry_cps.insert(0, "10")
        
        ctk.CTkLabel(frame_settings, text="CPM İLE TIKLA (0 - 23.1)"
                    ).grid(row=0, column=5, padx=10, sticky="w")
    
    def setup_visual_selectors(self):
        frame_visuals = ctk.CTkFrame(self.main_area, fg_color="transparent")
        frame_visuals.pack(expand=True, fill="both", pady=(0, 10))
        
        # Mouse görseli (SOL)
        mouse_frame = ctk.CTkFrame(frame_visuals, fg_color=COLOR_PANEL, corner_radius=15)
        mouse_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(mouse_frame, text="(Mouse)", text_color=COLOR_TEXT_DIM
                    ).pack(side="bottom", pady=10)
        
        # Canvas için bir container frame
        mouse_canvas_frame = ctk.CTkFrame(mouse_frame, fg_color=COLOR_PANEL)
        mouse_canvas_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        self.mouse_canvas = tk.Canvas(
            mouse_canvas_frame, width=250, height=350,
            bg=COLOR_PANEL, highlightthickness=0
        )
        self.mouse_canvas.pack(expand=True)
        self.draw_mouse()
        
        # Klavye görseli (SAĞ)
        keyboard_frame = ctk.CTkFrame(frame_visuals, fg_color=COLOR_PANEL, corner_radius=15)
        keyboard_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.keyboard_title = ctk.CTkLabel(
            keyboard_frame, text=f"({self.selected_keyboard_layout})",
            text_color=COLOR_TEXT_DIM, font=("Arial", 11)
        )
        self.keyboard_title.pack(side="bottom", pady=10)
        
        # Klavye container
        kb_container_frame = ctk.CTkFrame(keyboard_frame, fg_color=COLOR_PANEL, corner_radius=12)
        kb_container_frame.pack(expand=True, fill="both", padx=15, pady=15)
        
        self.kb_container = ctk.CTkFrame(kb_container_frame, fg_color="transparent")
        self.kb_container.pack(expand=True, fill="both")
        
        self.load_keyboard_layout()
    
    def draw_mouse(self):
        """Mouse çizimini oluştur"""
        canvas = self.mouse_canvas
        outline = COLOR_BORDER
        fill = COLOR_KEY
        
        # Mouse gövdesi
        body_points = [40, 40, 210, 40, 210, 280, 125, 320, 125, 320, 40, 280]
        canvas.create_polygon(body_points, fill=fill, outline=outline, width=2, smooth=True)
        
        # Tuşlar
        self.mouse_parts = {}
        
        # Sol tuş (LMB)
        self.mouse_parts["LMB"] = canvas.create_rectangle(
            40, 40, 125, 130, fill=fill, outline=outline, width=2, tags="LMB"
        )
        canvas.create_text(82, 85, text="LMB", fill=COLOR_TEXT, font=("Arial", 10, "bold"))
        
        # Sağ tuş (RMB)
        self.mouse_parts["RMB"] = canvas.create_rectangle(
            125, 40, 210, 130, fill=fill, outline=outline, width=2, tags="RMB"
        )
        canvas.create_text(167, 85, text="RMB", fill=COLOR_TEXT, font=("Arial", 10, "bold"))
        
        # Scroll tekerleği
        self.mouse_parts["WHEEL"] = canvas.create_oval(
            110, 135, 140, 165, fill=fill, outline=outline, width=2, tags="WHEEL"
        )
        canvas.create_text(125, 150, text="●", fill=COLOR_TEXT_DIM, font=("Arial", 8))
        
        # Yan tuşlar
        self.mouse_parts["SIDE1"] = canvas.create_rectangle(
            20, 170, 35, 210, fill=fill, outline=outline, width=2, tags="SIDE1"
        )
        self.mouse_parts["SIDE2"] = canvas.create_rectangle(
            20, 215, 35, 255, fill=fill, outline=outline, width=2, tags="SIDE2"
        )
        
        # Scroll yön tuşları
        self.mouse_parts["SCROLL_UP"] = canvas.create_rectangle(
            100, 105, 150, 125, fill=fill, outline=outline, width=1, tags="SCROLL_UP"
        )
        canvas.create_text(125, 115, text="▲", fill=COLOR_TEXT_DIM, font=("Arial", 8))
        
        self.mouse_parts["SCROLL_DOWN"] = canvas.create_rectangle(
            100, 170, 150, 190, fill=fill, outline=outline, width=1, tags="SCROLL_DOWN"
        )
        canvas.create_text(125, 180, text="▼", fill=COLOR_TEXT_DIM, font=("Arial", 8))
        
        # Etiketler
        canvas.create_text(82, 140, text="Sol", fill=COLOR_TEXT_DIM, font=("Arial", 8))
        canvas.create_text(167, 140, text="Sağ", fill=COLOR_TEXT_DIM, font=("Arial", 8))
        
        # Etkileşimler
        for tag in self.mouse_parts.keys():
            canvas.tag_bind(tag, "<Enter>", lambda e, t=tag: self.on_mouse_hover(t, True))
            canvas.tag_bind(tag, "<Leave>", lambda e, t=tag: self.on_mouse_hover(t, False))
            canvas.tag_bind(tag, "<Button-1>", lambda e, t=tag: self.select_mouse_target(t))
    
    def on_mouse_hover(self, tag, entering):
        """Mouse tuşları üzerine gelince efekt"""
        canvas = self.mouse_canvas
        
        if self.target_key == tag:
            return
            
        if entering:
            canvas.itemconfig(tag, fill="#2d3047")
        else:
            canvas.itemconfig(tag, fill=COLOR_KEY)
    
    def select_mouse_target(self, key_name):
        """Mouse tuşunu hedef olarak seç"""
        # Eski seçimi temizle
        if self.target_key:
            self.clear_previous_selection()
        
        # Yeni tuşu seç
        self.target_key = key_name
        self.lbl_selected_target.configure(
            text=key_name, text_color=COLOR_ACCENT, border_color=COLOR_ACCENT
        )
        
        # Canvas'ta vurgula
        if key_name in self.mouse_parts:
            self.mouse_canvas.itemconfig(key_name, fill=COLOR_ACCENT, outline=COLOR_ACCENT)
    
    def clear_previous_selection(self):
        """Önceki seçimi temizle"""
        if self.target_key in self.mouse_parts:
            self.mouse_canvas.itemconfig(self.target_key, fill=COLOR_KEY, outline=COLOR_BORDER)
        elif self.target_key in self.key_buttons:
            btn = self.key_buttons[self.target_key]
            if self.target_key in SPECIAL_KEYS:
                btn.configure(fg_color="#1a1c33", text_color=COLOR_TEXT, border_color=COLOR_BORDER)
            else:
                btn.configure(fg_color=COLOR_KEY, text_color=COLOR_TEXT, border_color=COLOR_BORDER)
    
    def load_keyboard_layout(self):
        """Klavye düzenini yükle"""
        # Eski tuşları temizle
        for widget in self.kb_container.winfo_children():
            widget.destroy()
        
        layout = KEYBOARD_LAYOUTS[self.selected_keyboard_layout]
        
        for r, row in enumerate(layout):
            row_frame = ctk.CTkFrame(self.kb_container, fg_color="transparent")
            row_frame.pack(pady=2)
            
            for key in row:
                if key:  # Boş tuşları atla
                    self.create_key_button(row_frame, key)
    
    def create_key_button(self, parent, key):
        """Klavye tuşu oluştur"""
        key_size = KEY_SIZES.get(key, KEY_SIZES["DEFAULT"])
        width = key_size["width"]
        height = key_size["height"]
        
        fg_color = "#1a1c33" if key in SPECIAL_KEYS else COLOR_KEY
        
        btn = ctk.CTkButton(
            parent,
            text=key,
            width=width,
            height=height,
            fg_color=fg_color,
            hover_color=COLOR_HOVER,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=6,
            font=("Arial", 9, "bold"),
            text_color=COLOR_TEXT,
            command=lambda k=key: self.select_keyboard_target(k)
        )
        btn.pack(side="left", padx=1, pady=1)
        
        self.key_buttons[key] = btn
    
    def select_keyboard_target(self, key_name):
        """Klavye tuşunu hedef olarak seç"""
        # Eski seçimi temizle
        if self.target_key:
            self.clear_previous_selection()
        
        # Yeni tuşu seç
        self.target_key = key_name
        self.lbl_selected_target.configure(
            text=key_name, text_color=COLOR_ACCENT, border_color=COLOR_ACCENT
        )
        
        # Butonu vurgula
        if key_name in self.key_buttons:
            self.key_buttons[key_name].configure(
                fg_color=COLOR_ACCENT, text_color="#13141f", border_color=COLOR_ACCENT
            )
    
    def setup_keyboard_selector(self):
        """Klavye düzeni seçici"""
        selector_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        selector_frame.pack(fill="x", pady=(5, 0))
        
        ctk.CTkLabel(selector_frame, text="Klavye Düzeni:", 
                     text_color=COLOR_TEXT_DIM, font=("Arial", 11)
                    ).pack(side="left", padx=(0, 10))
        
        self.keyboard_var = tk.StringVar(value=self.selected_keyboard_layout)
        
        for layout in KEYBOARD_LAYOUTS.keys():
            btn = ctk.CTkRadioButton(
                selector_frame,
                text=layout,
                variable=self.keyboard_var,
                value=layout,
                command=self.change_keyboard_layout,
                border_color=COLOR_ACCENT,
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_2,
                text_color=COLOR_TEXT,
                font=("Arial", 10)
            )
            btn.pack(side="left", padx=5)
    
    def change_keyboard_layout(self):
        """Klavye düzenini değiştir"""
        self.selected_keyboard_layout = self.keyboard_var.get()
        self.keyboard_title.configure(text=f"({self.selected_keyboard_layout})")
        self.load_keyboard_layout()
    
    def setup_focus_management(self):
        """Focus yönetimi"""
        def on_entry_focus_in(event):
            event.widget.configure(border_color=COLOR_ACCENT)
            event.widget.select_range(0, tk.END)
        
        def on_entry_focus_out(event):
            if event.widget == self.entry_interval:
                event.widget.configure(border_color=COLOR_ACCENT_2)
            else:
                event.widget.configure(border_color="#555")
            event.widget.selection_clear()
        
        # Entry'ler için focus event'leri
        self.entry_interval.bind("<FocusIn>", on_entry_focus_in)
        self.entry_interval.bind("<FocusOut>", on_entry_focus_out)
        
        self.entry_cps.bind("<FocusIn>", on_entry_focus_in)
        self.entry_cps.bind("<FocusOut>", on_entry_focus_out)
        
        # Sadece ana pencereye tıklayınca focus'u temizle (entry'lere değil)
        def on_window_click(event):
            # Tıklanan widget bir entry değilse focus'u temizle
            if not isinstance(event.widget, (ctk.CTkEntry, tk.Entry)):
                self.focus_set()
        
        self.bind("<Button-1>", on_window_click)
    
    def start_keyboard_listener(self):
        """Global klavye dinleyicisini başlat"""
        try:
            self.keyboard_listener = KeyboardListener(on_press=self.on_global_press)
            self.keyboard_listener.start()
        except Exception as e:
            print(f"Klavye dinleyicisi başlatılamadı: {e}")
    
    def on_global_press(self, key):
        """Global klavye tuş basımı"""
        try:
            if hasattr(key, 'char') and key.char:
                key_char = key.char.upper()
            else:
                key_name = str(key).replace("Key.", "")
                key_char = key_name.upper()
        except:
            return
        
        if self.listening_for_trigger:
            self.trigger_key = key_char
            self.btn_trigger.configure(
                text=self.trigger_key,
                text_color=COLOR_ACCENT,
                border_color=COLOR_ACCENT,
                font=("Arial", 11, "bold")
            )
            self.listening_for_trigger = False
            return
        
        if key_char == self.trigger_key and self.trigger_key:
            self.after(0, self.toggle_running)
    
    def wait_for_trigger_input(self):
        """Trigger tuşu atama modu"""
        self.btn_trigger.configure(
            text="Tuşa Bas...",
            text_color="red",
            border_color="red"
        )
        self.listening_for_trigger = True
    
    def toggle_running(self):
        """Başlat/Durdur"""
        if self.is_running:
            self.is_running = False
            self.btn_start.configure(text="BAŞLAT", fg_color=COLOR_ACCENT_2)
        else:
            # Kontroller
            if not self.target_key:
                messagebox.showwarning("Uyarı", "Lütfen önce tıklanacak bir tuş seçin!")
                return
            if not self.trigger_key:
                messagebox.showwarning("Uyarı", "Lütfen önce bir başlatma tuşu seçin!")
                return
            
            if not self.validate_inputs():
                return
            
            self.is_running = True
            self.btn_start.configure(text="DURDUR", fg_color="#ff004f")
            
            # Tıklama thread'ini başlat
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
    
    def validate_inputs(self):
        """Girdi doğrulama"""
        try:
            if self.click_mode.get() == "interval":
                val = float(self.entry_interval.get())
                if val < 0.01:
                    val = 0.01
                elif val > 99999:
                    val = 99999
                self.entry_interval.delete(0, tk.END)
                self.entry_interval.insert(0, str(val))
            else:
                val = float(self.entry_cps.get())
                if val < 0:
                    val = 0
                elif val > 23.1:
                    val = 23.1
                self.entry_cps.delete(0, tk.END)
                self.entry_cps.insert(0, str(val))
            return True
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin!")
            return False
    
    def click_loop(self):
        """Tıklama döngüsü"""
        while self.is_running:
            if self.click_mode.get() == "interval":
                delay = float(self.entry_interval.get())
            else:
                cps = float(self.entry_cps.get())
                delay = 1.0 / cps if cps > 0 else 1.0
            
            # Tıklama işlemi
            self.perform_click()
            
            time.sleep(delay)
    
    def perform_click(self):
        """Tıklama işlemini gerçekleştir"""
        try:
            # Mouse tıklamaları
            if self.target_key == "LMB":
                self.mouse_ctrl.click(Button.left)
            elif self.target_key == "RMB":
                self.mouse_ctrl.click(Button.right)
            elif self.target_key == "WHEEL":
                self.mouse_ctrl.click(Button.middle)
            elif self.target_key == "SCROLL_UP":
                self.mouse_ctrl.scroll(1)
            elif self.target_key == "SCROLL_DOWN":
                self.mouse_ctrl.scroll(-1)
            elif self.target_key in ["SIDE1", "SIDE2"]:
                # Yan tuşlar için varsayılan olarak X1 ve X2
                if self.target_key == "SIDE1":
                    self.mouse_ctrl.click(Button.x1)
                else:
                    self.mouse_ctrl.click(Button.x2)
            
            # Klavye tuşları
            elif self.target_key in SPECIAL_KEYS_MAP:
                key_name = SPECIAL_KEYS_MAP[self.target_key]
                key_obj = getattr(Key, key_name.lower(), None)
                if key_obj:
                    self.keyboard_ctrl.press(key_obj)
                    self.keyboard_ctrl.release(key_obj)
            
            elif self.target_key in TURKISH_CHARS:
                char = TURKISH_CHARS[self.target_key]
                self.keyboard_ctrl.press(char)
                self.keyboard_ctrl.release(char)
            
            elif self.target_key and len(self.target_key) == 1:
                # Normal karakter tuşu
                self.keyboard_ctrl.press(self.target_key.lower())
                self.keyboard_ctrl.release(self.target_key.lower())
            
            elif self.target_key in self.key_buttons:
                # Klavye butonundan gelen tuş
                if self.target_key in SPECIAL_KEYS_MAP:
                    key_name = SPECIAL_KEYS_MAP[self.target_key]
                    key_obj = getattr(Key, key_name.lower(), None)
                    if key_obj:
                        self.keyboard_ctrl.press(key_obj)
                        self.keyboard_ctrl.release(key_obj)
                else:
                    self.keyboard_ctrl.press(self.target_key.lower())
                    self.keyboard_ctrl.release(self.target_key.lower())
                    
        except Exception as e:
            print(f"Tıklama hatası: {e}")
    
    def on_closing(self):
        """Pencere kapatılırken"""
        self.is_running = False
        
        # Thread'i bekle
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=0.5)
        
        # Klavye dinleyicisini durdur
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        self.destroy()


if __name__ == "__main__":
    app = ModernAutoClicker()
    app.mainloop()