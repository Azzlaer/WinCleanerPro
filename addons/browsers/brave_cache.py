import os
import shutil
import getpass
import psutil
import tkinter.messagebox as msg

ADDON_INFO = {
    "id": "brave_cache",
    "name": "Brave Browser (cache e imágenes)",
    "default": True
}

USER = getpass.getuser()
BRAVE_BASE = rf"C:\Users\{USER}\AppData\Local\BraveSoftware\Brave-Browser\User Data"

CACHE_DIRS = [
    "Default\\Cache",
    "Default\\Code Cache",
    "Default\\GPUCache",
    "Default\\Media Cache",
]

# -------------------------------------------------

def is_brave_running():
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and "brave.exe" in p.info["name"].lower():
                return True
        except Exception:
            pass
    return False

def close_brave(logger):
    closed = False
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and "brave.exe" in p.info["name"].lower():
                p.terminate()
                closed = True
        except Exception:
            pass
    if closed:
        logger("🛑 Brave Browser fue cerrado para limpiar correctamente")

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
    logger("🦁 Brave Browser: análisis y limpieza de cache")

    analyze_only = False

    if is_brave_running():
        res = msg.askyesnocancel(
            "Brave Browser está abierto",
            "Brave Browser está en ejecución.\n\n"
            "¿Deseas CERRARLO para limpiar completamente?\n\n"
            "✔ Sí = cerrar Brave y limpiar\n"
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
            close_brave(logger)

    total = len(CACHE_DIRS)
    total_freed = 0

    for i, rel in enumerate(CACHE_DIRS, start=1):
        if stop_event.is_set():
            logger("⛔ Operación cancelada")
            return total_freed

        full_path = os.path.join(BRAVE_BASE, rel)
        logger(f"➡️ {'Analizando' if analyze_only else 'Limpiando'}: {full_path}")

        freed = clean_dir(full_path, logger, stop_event, analyze_only)
        total_freed += freed

        progress(int((i / total) * 100))

    mb = total_freed / (1024 * 1024)

    if analyze_only:
        logger(f"📊 Brave puede liberar: {mb:.2f} MB")
    else:
        logger(f"✅ Cache de Brave limpiada: {mb:.2f} MB liberados")

    return total_freed
