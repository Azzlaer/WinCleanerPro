import os
import configparser


class ConfigManager:
    """
    Maneja toda la configuración persistente de WinCleanerPro.
    - Estado de addons
    - Rutas configurables (Steam, Epic, etc.)
    """

    def __init__(self, file="config.ini"):
        self.file = file
        self.cfg = configparser.ConfigParser()

        # Crear config.ini si no existe
        if not os.path.exists(self.file):
            self._create_default()

        self.cfg.read(self.file, encoding="utf-8")

        # Asegurar secciones mínimas
        if "ADDONS" not in self.cfg:
            self.cfg["ADDONS"] = {}

        if "PATHS" not in self.cfg:
            self.cfg["PATHS"] = {}

        self._save()

    # ==================================================
    # ADDONS
    # ==================================================

    def is_addon_enabled(self, addon_id, default=True):
        """
        Devuelve True/False si el addon está activado.
        """
        try:
            return self.cfg["ADDONS"].getboolean(addon_id)
        except Exception:
            return default

    def set_addon_state(self, addon_id, enabled: bool):
        """
        Guarda el estado del addon (on/off).
        """
        self.cfg["ADDONS"][addon_id] = str(enabled)
        self._save()

    # ==================================================
    # PATHS (Steam, Epic, etc.)
    # ==================================================

    def get_path(self, key: str):
        """
        Obtiene una ruta guardada (ej: steam_path).
        """
        return self.cfg["PATHS"].get(key)

    def set_path(self, key: str, value: str):
        """
        Guarda una ruta en la configuración.
        """
        self.cfg["PATHS"][key] = value
        self._save()

    def has_path(self, key: str) -> bool:
        """
        Verifica si una ruta ya está configurada.
        """
        return key in self.cfg["PATHS"]

    # ==================================================
    # INTERNOS
    # ==================================================

    def _create_default(self):
        """
        Crea el archivo config.ini base.
        """
        self.cfg["ADDONS"] = {}
        self.cfg["PATHS"] = {}

        with open(self.file, "w", encoding="utf-8") as f:
            self.cfg.write(f)

    def _save(self):
        """
        Guarda config.ini en disco.
        """
        with open(self.file, "w", encoding="utf-8") as f:
            self.cfg.write(f)
