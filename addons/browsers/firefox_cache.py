import os
import shutil
import getpass
import psutil
import tkinter.messagebox as msg
import configparser

ADDON_INFO = {
    "id": "firefox_cache",
    "name": "Mozilla Firefox (cache e imágenes)",
    "default": True
}

USER = getpass.getuser()
FIREFOX_BASE = rf"C:\Users\{USER}\AppData\Local\Mozilla\Firefox\Profiles"

# -------------------------------------------------

def is_firefox_running():
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and "firefox.exe" in p.info["name"].lower():
                return True
        except Exception:
            pass
    return False

def close_firefox(logger):
    closed = False
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and "firefox.exe" in p.info["name"].lower():
                p.terminate()
                closed = True
        except Exception:
            pass
    if closed:
        logger("🛑 Mozilla Firefox fue cerrado para limpiar correctamente")

def get_profiles():
    """Detecta perfiles de Firefox leyendo profiles.ini"""
    ini_path = rf"C:\Users\{USER}\AppData\Roaming\Mozilla\Firefox\profiles.ini"
    profiles = []

    if not os.path.exists(ini_path):
        return profiles

    cfg = configparser.ConfigParser()
    cfg.read(ini_path, encoding="utf-8")

    for section in cfg.sections():
        if section.startswith("Profile"):
            path = cfg.get(section, "Path", fallback=None)
            if path:
                profiles.append(path)

    return profiles

def clean_dir(path, logger, stop_event, analyze_only):
    freed = 0

    if not os.path.exists(path):
        return 0

    for root, dirs, files in os.walk(path, topdown=False):
        if stop_event.is_set():
            return freed

        for f in files:
            file_path = os.path.join(root, f)
            try:
                size = os.path.getsize(file_path)
                freed += size
                if not analyze_only:
                    os.remove(file_path)
            except Exception:
                pass

        for d in dirs:
            try:
                if not analyze_only:
                    shutil.rmtree(os.path.join(root, d), ignore_errors=True)
            except Exception:
                pass

    return freed

# -------------------------------------------------

def run(logger, progress, stop_event):
    logger("🦊 Mozilla Firefox: análisis y limpieza de cache")

    analyze_only = False

    if is_firefox_running():
        res = msg.askyesnocancel(
            "Mozilla Firefox está abierto",
            "Mozilla Firefox está en ejecución.\n\n"
            "¿Deseas CERRARLO para limpiar completamente?\n\n"
            "✔ Sí = cerrar Firefox y limpiar\n"
            "❌ No = solo analizar (no borrar)\n"
            "Cancelar = no hacer nada"
        )

        if res is None:
            logger("⛔ Operación cancelada por el usuario")
            return 0

        if res is False:
            analyze_only = True
            logger("ℹ️ Modo ANALIZAR: no se borrarán archivos")
        else:
            close_firefox(logger)

    profiles = get_profiles()
    if not profiles:
        logger("ℹ️ No se encontraron perfiles de Firefox")
        progress(100)
        return 0

    total = len(profiles)
    total_freed = 0

    for i, profile in enumerate(profiles, start=1):
        if stop_event.is_set():
            logger("⛔ Operación cancelada")
            return total_freed

        # Cache principal del perfil
        cache_path = os.path.join(FIREFOX_BASE, profile, "cache2")

        logger(f"➡️ {'Analizando' if analyze_only else 'Limpiando'} perfil: {profile}")
        freed = clean_dir(cache_path, logger, stop_event, analyze_only)
        total_freed += freed

        progress(int((i / total) * 100))

    mb = total_freed / (1024 * 1024)

    if analyze_only:
        logger(f"📊 Firefox puede liberar: {mb:.2f} MB")
    else:
        logger(f"✅ Cache de Firefox limpiada: {mb:.2f} MB liberados")

    return total_freed
