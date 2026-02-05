import os
import winreg
import tkinter.filedialog as fd

def detect_steam_path():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Valve\Steam"
        ) as key:
            path, _ = winreg.QueryValueEx(key, "SteamPath")
            if os.path.exists(path):
                return path
    except Exception:
        pass
    return None

def ask_steam_path():
    return fd.askdirectory(
        title="Selecciona la carpeta donde está instalado Steam"
    )
