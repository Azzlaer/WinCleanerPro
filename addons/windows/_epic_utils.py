import os
import winreg
import tkinter.filedialog as fd

def detect_epic_path():
    keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\EpicGames\EpicGamesLauncher"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\EpicGames\EpicGamesLauncher"),
    ]

    for root, path in keys:
        try:
            with winreg.OpenKey(root, path) as key:
                val, _ = winreg.QueryValueEx(key, "InstallLocation")
                if os.path.exists(val):
                    return val
        except Exception:
            pass

    return None

def ask_epic_path():
    return fd.askdirectory(
        title="Selecciona la carpeta donde está instalado Epic Games Launcher"
    )
