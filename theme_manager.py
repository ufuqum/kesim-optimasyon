import tkinter as tk
from tkinter import ttk, messagebox

try:
    from ttkthemes import ThemedStyle
    TTKTHEMES_AVAILABLE = True
except ImportError:
    TTKTHEMES_AVAILABLE = False

class ThemeManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        if TTKTHEMES_AVAILABLE:
            self.style = ThemedStyle(self.root)
            self.available_themes = list(self.style.theme_names())
        else:
            self.style = ttk.Style(self.root)
            self.available_themes = self._get_standard_themes()

        self.current_theme = self.style.theme_use()

    def _get_standard_themes(self):
        standard_themes = [
            'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative'
        ]
        existing = self.style.theme_names()
        return [t for t in standard_themes if t in existing]

    def set_theme(self, theme_name: str):
        if theme_name in self.available_themes:
            if TTKTHEMES_AVAILABLE:
                self.style.set_theme(theme_name)
            else:
                self.style.theme_use(theme_name)
            self.current_theme = theme_name
            print(f"Tema değiştirildi: {theme_name}")
        else:
            messagebox.showerror("Hata", f"Geçersiz tema seçimi: {theme_name}")

    def get_themes(self):
        return self.available_themes

    def get_current_theme(self):
        return self.current_theme

    def show_theme_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Tema Seçimi")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Tema seçin:").pack(pady=8)

        selected_theme = tk.StringVar(value=self.get_current_theme())

        for theme in self.available_themes:
            ttk.Radiobutton(dialog, text=theme, variable=selected_theme, value=theme).pack(anchor="w", padx=20)

        def apply_theme():
            self.set_theme(selected_theme.get())
            dialog.destroy()

        ttk.Button(dialog, text="Uygula", command=apply_theme).pack(pady=10)
        dialog.grab_set()
