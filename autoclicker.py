import customtkinter as ctk
import tkinter as tk
import threading
import time
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener

# --- AYARLAR VE RENKLER  ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#13141f"        # Arka plan
COLOR_PANEL = "#1c1e2e"     # Panel rengi
COLOR_ACCENT = "#00dbde"    # Neon Mavi (Cyan)
COLOR_ACCENT_2 = "#fc00ff"  # Neon Mor
COLOR_TEXT = "#ffffff"
COLOR_TEXT_DIM = "#888888"
COLOR_HOVER = "#2d3047"     # Tuş üzerine gelince
COLOR_ACTIVE = "#00dbde"    # Seçili tuş

class ModernAutoClicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("BOSSCLICKER") #İsim
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

        # Arayüz Kurulumu
        self.setup_ui()
        
        # Global Klavye Dinleyicisi (Başlat/Durdur için)
        self.listener = KeyboardListener(on_press=self.on_global_press)
        self.listener.start()

    def setup_ui(self):
        # --- SOL MENÜ (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLOR_PANEL)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="LOGO", font=("Arial", 20, "bold"), text_color="#7b68ee").pack(pady=30)
        
        self.btn_style1 = ctk.CTkButton(self.sidebar, text="Stil 1", fg_color="transparent", border_width=1, border_color=COLOR_ACCENT_2)
        self.btn_style1.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="+ Yeni Stil Ekle", fg_color="transparent", text_color="#aaa", hover_color="#333").pack(pady=10, side="bottom")

        # --- ANA ALAN ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        # 1. BÖLÜM: ÜST SEÇİMLER
        self.frame_top = ctk.CTkFrame(self.main_area, fg_color=COLOR_PANEL, corner_radius=15)
        self.frame_top.pack(fill="x", pady=(0, 15), ipady=10)

        # Seçili Tuş Göstergesi
        ctk.CTkLabel(self.frame_top, text="Seçili Tuş :", font=("Arial", 12, "bold")).pack(side="left", padx=(20, 10))
        self.lbl_selected_target = ctk.CTkButton(self.frame_top, text=self.target_key, width=80, 
                                                 fg_color="transparent", border_width=2, border_color=COLOR_ACCENT,
                                                 state="disabled", text_color=COLOR_ACCENT)
        self.lbl_selected_target.pack(side="left")

        # Açma Tuşu (Trigger) Atama
        ctk.CTkLabel(self.frame_top, text="Açma Tuşu :", font=("Arial", 12, "bold")).pack(side="left", padx=(40, 10))
        self.btn_trigger = ctk.CTkButton(self.frame_top, text=self.trigger_key, width=80,
                                         fg_color="transparent", border_width=2, border_color=COLOR_ACCENT,
                                         command=self.wait_for_trigger_input)
        self.btn_trigger.pack(side="left")

        # Başlat Butonu (UI üzerinden manuel başlatmak için)
        self.btn_start = ctk.CTkButton(self.frame_top, text="BAŞLAT", fg_color=COLOR_ACCENT_2, hover_color="#b000b2", width=100, command=self.toggle_running)
        self.btn_start.pack(side="right", padx=20)

        # 2. BÖLÜM: ZAMANLAMA AYARLARI
        self.frame_settings = ctk.CTkFrame(self.main_area, fg_color=COLOR_PANEL, corner_radius=15)
        self.frame_settings.pack(fill="x", pady=(0, 15), ipady=15)

        # Interval Modu
        self.radio_interval = ctk.CTkRadioButton(self.frame_settings, text="", variable=self.click_mode, value="interval", width=0, border_color=COLOR_ACCENT, fg_color=COLOR_ACCENT)
        self.radio_interval.grid(row=0, column=0, padx=(20, 5), pady=10)
        
        self.entry_interval = ctk.CTkEntry(self.frame_settings, width=80, border_color=COLOR_ACCENT_2)
        self.entry_interval.insert(0, "4")
        self.entry_interval.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(self.frame_settings, text="X SANİYEDE BİR TIKLA (Limit: 0.01 - 99999)").grid(row=0, column=2, padx=10, sticky="w")

        # CPS Modu
        self.radio_cps = ctk.CTkRadioButton(self.frame_settings, text="", variable=self.click_mode, value="cps", width=0, border_color=COLOR_ACCENT, fg_color=COLOR_ACCENT)
        self.radio_cps.grid(row=0, column=4, padx=(40, 5))
        
        self.entry_cps = ctk.CTkEntry(self.frame_settings, width=80, border_color="#555")
        self.entry_cps.insert(0, "10")
        self.entry_cps.grid(row=0, column=5, padx=5)
        
        ctk.CTkLabel(self.frame_settings, text="CPM İLE TIKLA (Limit: 0 - 23.1)").grid(row=0, column=6, padx=10, sticky="w")

        # 3. BÖLÜM: GÖRSEL SEÇİCİLER (MOUSE & KLAVYE)
        self.frame_visuals = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.frame_visuals.pack(expand=True, fill="both")

        # Mouse Çizimi (Canvas kullanarak özel şekil)
        self.setup_mouse_visual(self.frame_visuals)
        
        # Klavye Çizimi
        self.setup_keyboard_visual(self.frame_visuals)

    def setup_mouse_visual(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=15, width=300)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(frame, text="(Mouse)", text_color=COLOR_TEXT_DIM).pack(side="bottom", pady=10)

        # Canvas çizimi
        self.mouse_canvas = tk.Canvas(frame, width=220, height=350, bg=COLOR_PANEL, highlightthickness=0)
        self.mouse_canvas.pack(pady=20)

        # Renkler
        outline = "#555"
        fill = "#1c1e2e"
        
        # Mouse Gövdesi (Basit şekillerle)
        # Sol Tık (LMB)
        self.id_lmb = self.create_rounded_rect(self.mouse_canvas, 20, 20, 100, 120, 20, fill=fill, outline=outline, tags="LMB")
        self.mouse_canvas.create_text(60, 70, text="LMB", fill="white", state="disabled")
        
        # Sağ Tık (RMB) - Varsayılan seçili olduğu için renkli başlatacağız
        self.id_rmb = self.create_rounded_rect(self.mouse_canvas, 110, 20, 190, 120, 20, fill=COLOR_ACCENT, outline=COLOR_ACCENT, tags="RMB")
        self.mouse_canvas.create_text(150, 70, text="RMB", fill="white", state="disabled")
        
        # Scroll Tekerlek (Wheel) - Yukarı/Aşağı/Tık
        self.id_wheel = self.mouse_canvas.create_oval(95, 40, 115, 90, fill="#333", outline=outline, tags="WHEEL")
        
        # Gövde alt kısım
        self.mouse_canvas.create_arc(20, 100, 190, 320, start=180, extent=180, fill=fill, outline=outline, style=tk.CHORD)
        
        # Yan Tuşlar
        self.id_side1 = self.create_rounded_rect(self.mouse_canvas, 5, 140, 25, 190, 5, fill=fill, outline=outline, tags="SIDE1")
        self.id_side2 = self.create_rounded_rect(self.mouse_canvas, 5, 200, 25, 250, 5, fill=fill, outline=outline, tags="SIDE2")

        # Scroll Eklentileri (Görselde istendiği gibi butonlar)
        # Döndürülebilir tuşlar için canvas içine widget gömülebilir veya çizim yapılabilir.
        # Basitlik için canvas altına buton ekliyorum.
        
        # Etkileşimler (Hover ve Click)
        for tag in ["LMB", "RMB", "WHEEL", "SIDE1", "SIDE2"]:
            self.mouse_canvas.tag_bind(tag, "<Enter>", lambda e, t=tag: self.on_hover(t, True))
            self.mouse_canvas.tag_bind(tag, "<Leave>", lambda e, t=tag: self.on_hover(t, False))
            self.mouse_canvas.tag_bind(tag, "<Button-1>", lambda e, t=tag: self.select_target(t))

    def create_rounded_rect(self, canvas, x1, y1, x2, y2, r, **kwargs):
        # Tkinter canvas'ta yuvarlak dikdörtgen için yardımcı fonksiyon
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def setup_keyboard_visual(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=15)
        frame.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="(Klavye - Q Numpad)", text_color=COLOR_TEXT_DIM).pack(side="bottom", pady=10)

        # Klavye Container
        kb_container = ctk.CTkFrame(frame, fg_color="transparent")
        kb_container.pack(expand=True)

        # Basit Q Klavye Düzeni (Örnek tuşlar)
        keys_layout = [
            ["ESC", "F1", "F2", "F3", "F4", "F5", "PRT"],
            ["TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["CAPS", "A", "S", "D", "F", "G", "H", "J", "K", "L", "ENT"],
            ["SHFT", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "UP"],
            ["CTRL", "WIN", "ALT", "SPACE", "ALT", "FN", "LFT", "DWN", "RGT"]
        ]
        
        # Numpad (Sağ taraf)
        numpad_layout = [
            ["NUM", "/", "*", "-"],
            ["7", "8", "9", "+"],
            ["4", "5", "6", ""],
            ["1", "2", "3", "ENT"],
            ["0", ".", "", ""]
        ]

        # Ana Klavye Render
        for r, row in enumerate(keys_layout):
            row_frame = ctk.CTkFrame(kb_container, fg_color="transparent")
            row_frame.pack()
            for key in row:
                width = 35 if len(key) < 2 else 55
                if key == "SPACE": width = 150
                
                # Tuş Rengi
                btn_color = COLOR_BG
                text_color = "#ccc"
                if key == "ESC": text_color = COLOR_ACCENT
                
                btn = ctk.CTkButton(row_frame, text=key, width=width, height=35, 
                                    fg_color=btn_color, hover_color=COLOR_HOVER,
                                    corner_radius=4, font=("Arial", 10, "bold"),
                                    command=lambda k=key: self.select_target(k))
                btn.pack(side="left", padx=2, pady=2)

        # Numpad'i yanına eklemek için layout biraz daha karmaşıklaşır, 
        # şimdilik basitlik adına ana bloğun altına ekliyorum ama 
        # görseldeki gibi sağa almak için frame yapısı değiştirilebilir.

    # --- MANTIK FONKSİYONLARI ---

    def on_hover(self, tag, entering):
        """Mouse görseli üzerine gelince koyulaşma efekti"""
        canvas = self.mouse_canvas
        # Mevcut rengi koru, sadece hover rengini değiştir
        current_fill = canvas.itemcget(tag, "fill")
        
        # Eğer bu tuş zaten seçiliyse rengini değiştirme
        if tag == self.target_key:
            return

        if entering:
            canvas.itemconfig(tag, fill="#2d3047") # Koyulaş
        else:
            canvas.itemconfig(tag, fill="#1c1e2e") # Orijinal

    def select_target(self, key_name):
        """Hangi tuşun taklit edileceğini seçer"""
        # Eski seçiliyi normale döndür (Sadece Mouse için görsel güncelleme örneği)
        old_key = self.target_key
        if old_key in ["LMB", "RMB", "WHEEL", "SIDE1", "SIDE2"]:
            self.mouse_canvas.itemconfig(old_key, fill="#1c1e2e", outline="#555")

        self.target_key = key_name
        self.lbl_selected_target.configure(text=key_name)
        
        # Yeni seçiliyi parlat (Mouse ise)
        if key_name in ["LMB", "RMB", "WHEEL", "SIDE1", "SIDE2"]:
            self.mouse_canvas.itemconfig(key_name, fill=COLOR_ACCENT, outline=COLOR_ACCENT)

    def wait_for_trigger_input(self):
        """Açma tuşu için bekleme modu"""
        self.btn_trigger.configure(text="Tuşa Bas...", text_color="red")
        self.listening_for_trigger = True

    def on_global_press(self, key):
        """Tüm klavye olaylarını dinler"""
        try:
            key_char = key.char.upper()
        except AttributeError:
            key_char = str(key).replace("Key.", "").upper()

        # Tuş atama modu
        if self.listening_for_trigger:
            self.trigger_key = key_char
            self.btn_trigger.configure(text=self.trigger_key, text_color="white")
            self.listening_for_trigger = False
            return

        # Başlat / Durdur
        if key_char == self.trigger_key:
            # Tkinter thread güvenliği için after kullanılır
            self.after(0, self.toggle_running)

    def toggle_running(self):
        if self.is_running:
            self.is_running = False
            self.btn_start.configure(text="BAŞLAT", fg_color=COLOR_ACCENT_2)
            if self.click_thread:
                self.click_thread.join(0.1)
        else:
            if self.validate_inputs():
                self.is_running = True
                self.btn_start.configure(text="DURDUR", fg_color="#ff004f") # Kırmızımsı
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
            elif len(self.target_key) == 1: # Klavye harfi
                self.keyboard_ctrl.press(self.target_key.lower())
                self.keyboard_ctrl.release(self.target_key.lower())
            
            # 3. Uyuma
            time.sleep(delay)

if __name__ == "__main__":
    app = ModernAutoClicker()
    app.mainloop()