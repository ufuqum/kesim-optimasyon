import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Optional
from optimization import optimize_parts, draw_cutting_plan
from file_handlers import (
    save_project, load_project,
    export_to_excel, export_to_pdf,
    import_from_csv, export_to_csv,
    safe_get_part_attr,
)
from gui_helpers import register_fonts, show_about, update_status, Translator, validate_positive_number
from theme_manager import ThemeManager
from constants import DEFAULT_STOCK_LENGTH, DEFAULT_KERF, DEFAULT_LANGUAGE, DEFAULT_THEME, LANGUAGES


class OptimizationApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        register_fonts()

        self.translator = Translator(DEFAULT_LANGUAGE)
        self.theme_manager = ThemeManager(root)
        self.theme_manager.set_theme(DEFAULT_THEME)

        # Parametreler
        self.stock_length = DEFAULT_STOCK_LENGTH
        self.kerf = DEFAULT_KERF
        self.trials = 20
        self.algorithm = "first_fit"
        self.stock_unit_price = 1.0

        self.parts_data: List[Dict[str, Any]] = []
        self.optimization_result_data: Optional[Any] = None

        self._create_widgets()
        self._setup_menu()
        self._setup_status_bar()

    def _create_widgets(self) -> None:
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Parça Giriş Alanları
        entry_frame = ttk.Frame(self.main_frame)
        entry_frame.pack(fill="x", pady=5)

        ttk.Label(entry_frame, text="Parça Adı:").grid(row=0, column=0, sticky="w")
        self.part_name_var = tk.StringVar()
        ttk.Entry(entry_frame, width=15, textvariable=self.part_name_var).grid(row=0, column=1)

        ttk.Label(entry_frame, text="Parça Uzunluğu (mm):").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.part_length_var = tk.StringVar()
        ttk.Entry(entry_frame, width=10, textvariable=self.part_length_var).grid(row=0, column=3)

        ttk.Label(entry_frame, text="Adet:").grid(row=0, column=4, sticky="w", padx=(10,0))
        self.part_quantity_var = tk.StringVar()
        ttk.Entry(entry_frame, width=5, textvariable=self.part_quantity_var).grid(row=0, column=5)

        add_part_btn = ttk.Button(entry_frame, text=self.translator.translate("add_part"), command=self._add_part)
        add_part_btn.grid(row=0, column=6, padx=10)

        # Butonlar çerçevesi
        button_frame_2 = ttk.Frame(self.main_frame)
        button_frame_2.pack(fill="x", pady=5)

        edit_part_btn = ttk.Button(button_frame_2, text=self.translator.translate("edit_part"), command=self._edit_selected_part)
        edit_part_btn.pack(side="left", padx=(0,10))

        delete_part_btn = ttk.Button(button_frame_2, text=self.translator.translate("delete_part"), command=self._delete_selected_part)
        delete_part_btn.pack(side="left", padx=(0,10))

        delete_all_btn = ttk.Button(button_frame_2, text=self.translator.translate("delete_all_parts"), command=self._delete_all_parts)
        delete_all_btn.pack(side="left", padx=(0,10))

        # Parça Listesi Treeview
        self.parts_tree = ttk.Treeview(self.main_frame, columns=("name", "length", "quantity"), show="headings", height=8)
        self.parts_tree.heading("name", text=self.translator.translate("add_part"))
        self.parts_tree.heading("length", text="Uzunluk (mm)")
        self.parts_tree.heading("quantity", text="Adet")
        self.parts_tree.pack(fill="both", expand=True, pady=5)

        # Matplotlib Görselleştirme Tuvali
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        self.fig, self.ax = plt.subplots(figsize=(7,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

        # Optimize Et, Excel ve PDF Butonları yanyana frame içinde
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        self.optimize_button = ttk.Button(button_frame, text=self.translator.translate("optimize"), command=self._optimize)
        self.optimize_button.pack(side="left", padx=5)

        self.export_excel_button = ttk.Button(button_frame, text=self.translator.translate("export_excel"), command=self._export_excel)
        self.export_excel_button.pack(side="left", padx=5)

        self.export_pdf_button = ttk.Button(button_frame, text=self.translator.translate("export_pdf"), command=self._export_pdf)
        self.export_pdf_button.pack(side="left", padx=5)

    def _setup_menu(self) -> None:
        menubar = tk.Menu(self.root)

        # Dosya Menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.translator.translate("project_save"), command=self._save_project)
        file_menu.add_command(label=self.translator.translate("project_load"), command=self._load_project)
        file_menu.add_command(label=self.translator.translate("import_csv"), command=self._import_csv)
        file_menu.add_command(label=self.translator.translate("export_csv"), command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label=self.translator.translate("export_excel"), command=self._export_excel)
        file_menu.add_command(label=self.translator.translate("export_pdf"), command=self._export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label=self.translator.translate("exit"), command=self.root.quit)
        menubar.add_cascade(label=self.translator.translate("file"), menu=file_menu)

        # Tema Menüsü
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label=self.translator.translate("theme_select"), command=self.theme_manager.show_theme_dialog)
        menubar.add_cascade(label=self.translator.translate("theme"), menu=theme_menu)

        # Dil Menüsü
        lang_menu = tk.Menu(menubar, tearoff=0)
        for lang_code in LANGUAGES.keys():
            lang_name = LANGUAGES[lang_code].get(lang_code, lang_code)
            lang_menu.add_command(label=lang_name, command=lambda c=lang_code: self._set_language(c))
        menubar.add_cascade(label=self.translator.translate("language_select"), menu=lang_menu)

        # Ayarlar Menüsü
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label=self.translator.translate("settings"), command=self._show_settings_dialog)
        menubar.add_cascade(label=self.translator.translate("settings_menu"), menu=settings_menu)

        # Yardım Menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.translator.translate("about"), command=lambda: show_about(self.root))
        menubar.add_cascade(label=self.translator.translate("help"), menu=help_menu)

        self.root.config(menu=menubar)

    def _setup_status_bar(self) -> None:
        self.status_bar = ttk.Label(self.root, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        update_status(self.status_bar, self.translator.translate("ready"))

    # ---- Parça Ekleme-Düzenleme-Silme ----

    def _add_part(self) -> None:
        name = self.part_name_var.get().strip()
        if not name:
            messagebox.showerror("Hata", "Parça adı boş olamaz.")
            return
        if not validate_positive_number(self.part_length_var.get()):
            messagebox.showerror("Hata", self.translator.translate("error_invalid_input"))
            return
        if not validate_positive_number(self.part_quantity_var.get()):
            messagebox.showerror("Hata", self.translator.translate("error_invalid_input"))
            return

        try:
            length = float(self.part_length_var.get())
            quantity = int(self.part_quantity_var.get())
            new_part = {"name": name, "length": length, "quantity": quantity}
            self.parts_data.append(new_part)
            self.parts_tree.insert("", "end", values=(name, length, quantity))
            self.part_name_var.set("")
            self.part_length_var.set("")
            self.part_quantity_var.set("")
            update_status(self.status_bar, f"Parça eklendi: {name}, Uzunluk={length} mm, Adet={quantity}", duration_ms=3000)
        except Exception as e:
            messagebox.showerror("Hata", f"Parça eklenirken hata oluştu:\n{e}")

    def _edit_selected_part(self) -> None:
        selected_items = self.parts_tree.selection()
        if not selected_items:
            messagebox.showwarning("Uyarı", self.translator.translate("warning_select_part"))
            return
        item = selected_items[0]
        values = self.parts_tree.item(item, "values")
        name, length, quantity = values
        self.part_name_var.set(name)
        self.part_length_var.set(length)
        self.part_quantity_var.set(quantity)
        self.parts_tree.delete(item)
        for i, part in enumerate(self.parts_data):
            if (part["name"] == name and
                    float(part["length"]) == float(length) and
                    int(part["quantity"]) == int(quantity)):
                del self.parts_data[i]
                break
        update_status(self.status_bar, "Parça düzenlemesi için form dolduruldu.", duration_ms=3000)

    def _delete_selected_part(self) -> None:
        selected_items = self.parts_tree.selection()
        if not selected_items:
            messagebox.showwarning("Uyarı", self.translator.translate("warning_select_part"))
            return
        for item in selected_items:
            values = self.parts_tree.item(item, "values")
            name, length_str, quantity_str = values
            length = float(length_str)
            quantity = int(quantity_str)
            for i, part in enumerate(self.parts_data):
                if (part["name"] == name and
                        float(part["length"]) == length and
                        int(part["quantity"]) == quantity):
                    del self.parts_data[i]
                    break
            self.parts_tree.delete(item)
        update_status(self.status_bar, "Seçili parça(lar) silindi.", duration_ms=3000)

    def _delete_all_parts(self) -> None:
        if not self.parts_data:
            messagebox.showinfo("Bilgi", "Listede silinecek parça yok.")
            return
        if messagebox.askyesno("Onay", self.translator.translate("confirm_delete_all")):
            self.parts_data.clear()
            for item in self.parts_tree.get_children():
                self.parts_tree.delete(item)
            update_status(self.status_bar, "Tüm parçalar silindi.", duration_ms=3000)

    # ---- Optimizasyon ve Grafik ----

    def _optimize(self) -> None:
        if not self.parts_data:
            messagebox.showwarning("Uyarı", "Lütfen önce parça verilerini ekleyin.")
            update_status(self.status_bar, "Parça verisi yok")
            return
        try:
            optimize_result = optimize_parts(
                self.parts_data,
                self.stock_length,
                self.kerf,
                trials=self.trials,
                algorithm=self.algorithm,
            )
            self.optimization_result_data = optimize_result
            self._draw_cutting_plan()
            update_status(self.status_bar, self.translator.translate("optimization_complete"))
        except Exception as e:
            messagebox.showerror("Hata", f"{self.translator.translate('optimization_error')}\n{e}")
            update_status(self.status_bar, self.translator.translate("optimization_error"))

    def _draw_cutting_plan(self) -> None:
        if self.optimization_result_data is None:
            update_status(self.status_bar, "Görselleştirilecek veri yok")
            return
        try:
            kerf_val = (
                self.optimization_result_data.get("kerf", self.kerf)
                if isinstance(self.optimization_result_data, dict)
                else self.kerf
            )
            draw_cutting_plan(self.ax, self.canvas, self.optimization_result_data,
                              stock_length=self.stock_length, kerf=kerf_val)
            update_status(self.status_bar, "Kesim planı çizildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Kesim planı çizilirken hata oluştu:\n{e}")
            update_status(self.status_bar, "Çizim hatası")

    # ---- Dosya İşlemleri ----

    def _save_project(self) -> None:
        try:
            save_project(self.parts_data, self.stock_length, self.kerf)
            update_status(self.status_bar, "Proje kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi:\n{e}")
            update_status(self.status_bar, "Kaydetme hatası")

    def _load_project(self) -> None:
        try:
            result = load_project()
            if result:
                parts, stock_length, kerf = result
                self.parts_data = parts
                self.stock_length = stock_length
                self.kerf = kerf
                self.parts_tree.delete(*self.parts_tree.get_children())
                for part in self.parts_data:
                    self.parts_tree.insert("", "end", values=(
                        safe_get_part_attr(part, "name", ""),
                        safe_get_part_attr(part, "length", 0),
                        safe_get_part_attr(part, "quantity", 0)
                    ))
                update_status(self.status_bar, "Proje yüklendi.")
            else:
                update_status(self.status_bar, "Proje yükleme iptal edildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yüklenemedi:\n{e}")
            update_status(self.status_bar, "Yükleme hatası")

    # ---- CSV İşlemleri ----

    def _import_csv(self) -> None:
        try:
            imported = import_from_csv()
            if imported:
                self.parts_data = imported
                self.parts_tree.delete(*self.parts_tree.get_children())
                for part in self.parts_data:
                    self.parts_tree.insert("", "end", values=(
                        safe_get_part_attr(part, "name", ""),
                        safe_get_part_attr(part, "length", 0),
                        safe_get_part_attr(part, "quantity", 0)
                    ))
                update_status(self.status_bar, "CSV dosyası içe aktarıldı.", 3000)
        except Exception as e:
            messagebox.showerror("Hata", f"CSV içe aktarılırken hata oluştu:\n{e}")

    def _export_csv(self) -> None:
        if not self.parts_data:
            messagebox.showinfo("Bilgi", "Dışa aktarılacak veri bulunmamaktadır.")
            return
        try:
            export_to_csv(self.parts_data)
        except Exception as e:
            messagebox.showerror("Hata", f"CSV dışa aktarılırken hata oluştu:\n{e}")

    # ---- Excel & PDF Dışa Aktarma ----

    def _export_excel(self) -> None:
        if not self.optimization_result_data:
            messagebox.showinfo("Bilgi", "Önce optimizasyon yapılmalı.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dosyaları", "*.xlsx")])
        if file_path:
            try:
                export_to_excel(self.optimization_result_data, file_path, self.stock_unit_price)
            except Exception as e:
                messagebox.showerror("Hata", f"Excel dışa aktarılırken hata oluştu:\n{e}")

    def _export_pdf(self) -> None:
        if not self.optimization_result_data:
            messagebox.showinfo("Bilgi", "Önce optimizasyon yapılmalı.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyaları", "*.pdf")])
        if file_path:
            try:
                export_to_pdf(self.optimization_result_data, file_path, self.stock_unit_price)
            except Exception as e:
                messagebox.showerror("Hata", f"PDF dışa aktarılırken hata oluştu:\n{e}")

    # ---- Tema ve Dil Yönetimi ----

    def _set_language(self, lang_code: str) -> None:
        self.translator.set_language(lang_code)
        self._refresh_ui_texts()

    def _refresh_ui_texts(self) -> None:
        # Menü ve buton yazıları dahil tüm metinleri güncelle

        # Menü yeniden oluştur
        self._setup_menu()

        # Butonlar
        self.optimize_button.config(text=self.translator.translate("optimize"))
        self.export_excel_button.config(text=self.translator.translate("export_excel"))
        self.export_pdf_button.config(text=self.translator.translate("export_pdf"))

        # Diğer statik metin alanlarını da güncellemek isterseniz buraya ekleyin, örn. Treeview başlığı vs.

    def _show_settings_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title(self.translator.translate("settings"))
        dialog.resizable(False, False)

        ttk.Label(dialog, text=self.translator.translate("stock_length")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        stock_length_var = tk.StringVar(value=str(self.stock_length))
        ttk.Entry(dialog, textvariable=stock_length_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text=self.translator.translate("kerf_label")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        kerf_var = tk.StringVar(value=str(self.kerf))
        ttk.Entry(dialog, textvariable=kerf_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text=self.translator.translate("trials_label")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        trials_var = tk.StringVar(value=str(self.trials))
        ttk.Entry(dialog, textvariable=trials_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(dialog, text=self.translator.translate("algorithm_label")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        alg_var = tk.StringVar(value=self.algorithm)
        ttk.Combobox(dialog, textvariable=alg_var, values=["first_fit", "genetic"], state="readonly").grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(dialog, text=self.translator.translate("stock_unit_price_label")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        price_var = tk.StringVar(value=str(self.stock_unit_price))
        ttk.Entry(dialog, textvariable=price_var).grid(row=4, column=1, padx=5, pady=5)

        def on_save():
            try:
                sl = int(stock_length_var.get())
                kf = int(kerf_var.get())
                tr = int(trials_var.get())
                alg = alg_var.get()
                price = float(price_var.get())
                if sl <= 0 or kf <= 0 or tr <= 0 or price < 0:
                    raise ValueError()
                self.stock_length = sl
                self.kerf = kf
                self.trials = tr
                self.algorithm = alg
                self.stock_unit_price = price
                dialog.destroy()
                update_status(self.status_bar,
                              f"Ayarlar güncellendi: Stok={sl}, Kerf={kf}, Deneme={tr}, Alg={alg}, Fiyat={price} TL/mm", 5000)
            except ValueError:
                messagebox.showerror("Hata", "Geçerli pozitif sayılar giriniz.")

        ttk.Button(dialog, text=self.translator.translate("save_button"), command=on_save).grid(row=5, column=0, columnspan=2, pady=10)
        dialog.grab_set()
