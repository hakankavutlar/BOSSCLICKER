# main.py - BU DOSYAYI ÇALIŞTIR
from config import setup_theme
from app import ModernAutoClicker

if __name__ == "__main__":
    setup_theme()
    app = ModernAutoClicker()
    app.mainloop()