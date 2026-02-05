import tkinter as tk
from tkinter import ttk
import threading

from core.addon_manager import AddonManager
from core.config import ConfigManager
from core.logger import Logger
from core.cleaner_engine import CleanerEngine


class WinCleanerProGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WinCleanerPro")
        self.root.geometry("920x640")
        self.root.resizable(False, False)

        self.config = ConfigManager()
        self.addon_manager = AddonManager()

        self._build_ui()
        self._load_addons()

    # ==================================================
    # UI
    # ==================================================
    def _build_ui(self):
        self.main = ttk.Frame(self.root)
        self.main.pack(fill="both", expand=True)

        # ---------------- Sidebar ----------------
        self.sidebar = ttk.Frame(self.main, width=210)
        self.sidebar.pack(side="left", fill="y")

        ttk.Label(
            self.sidebar,
            text="Categorías",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(12, 6))

        self.category_list = tk.Listbox(
            self.sidebar,
            height=12,
            activestyle="dotbox"
        )
        self.category_list.pack(fill="y", expand=True, padx=10)
        self.category_list.bind("<<ListboxSelect>>", self._on_category_select)

        # ---------------- Content ----------------
        self.content = ttk.Frame(self.main, padding=14)
        self.content.pack(side="left", fill="both", expand=True)

        self.check_frame = ttk.Frame(self.content)
        self.check_frame.pack(fill="both", expand=True)

        # ---------------- Bottom ----------------
        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")

        self.progress = ttk.Progressbar(
            bottom,
            mode="determinate"
        )
        self.progress.pack(fill="x", pady=(0, 6))

        self.total_label = ttk.Label(
            bottom,
            text="📊 Espacio potencial: 0.00 MB",
            font=("Segoe UI", 10, "bold")
        )
        self.total_label.pack(anchor="w", pady=(0, 6))

        btns = ttk.Frame(bottom)
        btns.pack(fill="x")

        self.btn_analyze = ttk.Button(
            btns,
            text="ANALIZAR",
            command=self.start_analyze
        )
        self.btn_analyze.pack(side="right", padx=5)

        self.btn_clean = ttk.Button(
            btns,
            text="LIMPIAR",
            command=self.start_clean
        )
        self.btn_clean.pack(side="right", padx=5)

        self.btn_stop = ttk.Button(
            btns,
            text="DETENER",
            command=self.stop_action
        )
        self.btn_stop.pack(side="right")

        # ---------------- Log ----------------
        ttk.Label(
            self.root,
            text="Registro de actividad",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12)

        self.log_box = tk.Text(
            self.root,
            height=9,
            bg="#f7f7f7",
            font=("Consolas", 9),
            state="normal"
        )
        self.log_box.pack(fill="x", padx=12, pady=(0, 12))

        self.logger = Logger(self._log_ui)
        self.engine = CleanerEngine(self.logger)

    # ==================================================
    # LOG
    # ==================================================
    def _log_ui(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    # ==================================================
    # ADDONS
    # ==================================================
    def _load_addons(self):
        self.addons = self.addon_manager.load_addons()

        self.categories = sorted(
            set(addon["category"] for addon in self.addons)
        )

        self.category_list.delete(0, "end")
        for category in self.categories:
            self.category_list.insert("end", category.capitalize())

        if self.categories:
            self.category_list.selection_set(0)
            self._render_category(self.categories[0])

    def _on_category_select(self, event):
        sel = self.category_list.curselection()
        if not sel:
            return
        category = self.categories[sel[0]]
        self._render_category(category)

    def _render_category(self, category):
        for w in self.check_frame.winfo_children():
            w.destroy()

        self.vars = {}

        ttk.Label(
            self.check_frame,
            text=f"Limpieza de {category.capitalize()}",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        for addon in self.addons:
            if addon["category"] != category:
                continue

            var = tk.BooleanVar(
                value=self.config.is_addon_enabled(
                    addon["id"],
                    addon.get("default", True)
                )
            )

            chk = ttk.Checkbutton(
                self.check_frame,
                text=addon["name"],
                variable=var,
                command=lambda a=addon, v=var:
                    self.config.set_addon_state(a["id"], v.get())
            )
            chk.pack(anchor="w", pady=2)

            self.vars[addon["id"]] = (addon, var)

    # ==================================================
    # ACTIONS
    # ==================================================
    def start_analyze(self):
        self._start_action(mode="analyze")

    def start_clean(self):
        self._start_action(mode="clean")

    def stop_action(self):
        self.engine.stop()

    def _start_action(self, mode):
        selected = [a for a, v in self.vars.values() if v.get()]
        if not selected:
            self.logger.log("⚠️ No hay opciones seleccionadas")
            return

        self.progress["value"] = 0

        if mode == "analyze":
            self.total_label.config(text="📊 Espacio potencial: 0.00 MB")
            self.logger.log("🔍 Iniciando análisis global...")
        else:
            self.total_label.config(text="💾 Espacio liberado: 0.00 MB")
            self.logger.log("🧹 Iniciando limpieza...")

        threading.Thread(
            target=self.engine.run,
            args=(selected, self._update_progress, self._action_done, mode),
            daemon=True
        ).start()

    def _update_progress(self, index, total, percent):
        base = ((index - 1) / total) * 100
        self.progress["value"] = base + (percent / total)
        self.root.update_idletasks()

    def _action_done(self, total_bytes, mode):
        mb = total_bytes / (1024 * 1024)

        if mode == "analyze":
            self.total_label.config(
                text=f"📊 Espacio potencial: {mb:.2f} MB"
            )
            self.logger.log(
                f"📊 Análisis completado: {mb:.2f} MB se podrían liberar"
            )
        else:
            self.total_label.config(
                text=f"💾 Espacio liberado: {mb:.2f} MB"
            )
            self.logger.log(
                f"💾 Limpieza completada: {mb:.2f} MB liberados"
            )

    # ==================================================
    # RUN
    # ==================================================
    def run(self):
        self.root.mainloop()
