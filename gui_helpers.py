import tkinter as tk
from tkinter import messagebox, font
from typing import Optional
from constants import LANGUAGES, DEFAULT_LANGUAGE

class Translator:
    def __init__(self, language_code: str = DEFAULT_LANGUAGE):
        self.set_language(language_code)

    def set_language(self, language_code: str):
        if language_code in LANGUAGES:
            self.lang = language_code
            self.translations = LANGUAGES[language_code]
        else:
            self.lang = DEFAULT_LANGUAGE
            self.translations = LANGUAGES[DEFAULT_LANGUAGE]

    def translate(self, key: str) -> str:
        return self.translations.get(key, key)

def register_fonts() -> None:
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=10)

def show_about(root: tk.Tk) -> None:
    messagebox.showinfo("Hakkında", "Kesim Optimizasyon Uygulaması\n© 2025")

def update_status(status_bar: tk.Label, message: str, duration_ms: Optional[int] = None) -> None:
    status_bar.config(text=message)
    status_bar.update_idletasks()
    if duration_ms is not None:
        status_bar.after(duration_ms, lambda: status_bar.config(text=""))

def validate_positive_number(value: str) -> bool:
    try:
        val = float(value)
        return val > 0
    except ValueError:
        return False
