import os
import shutil
import getpass
import psutil
import tkinter.messagebox as msg

ADDON_INFO = {
    "id": "opera_cache",
    "name": "Opera Browser (cache e imágenes)",
    "default": True
}

USER = getpass.getuser()
OPERA_BASE = rf"C:\Users\{USER}\AppData\Roaming\Opera Software\Opera Stable"

CACHE_DIRS = [
    "Cache",
    "Code Cache",
    "GPUCache",
    "Media Cache",
]

# -------------------------------------------------

def is_opera_running():
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and "opera.exe" in p.info["name"].lower():
                return True
        except Exception:
            pass
    return False

def close_opera(logger):
    closed = False
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and "opera.exe" in p.info["name"].lower():
                p.terminate()
                closed = True
        except Exception:
            pass
    if closed:
        logger("🛑 Opera fue cerrado para limpiar correctamente")

def clean_dir(path, logger, stop_event, analyze_only):
    freed = 0
    if not os.path.exists(path):
        return 0

    for root, dirs, files in os.walk(path, topdown=False):
        if stop_event.is_set():
            return freed

        for f in files:
            fp = os.path.join(root, f)
            try:
                size = os.path.getsize(fp)
                freed += size
                if not analyze_only:
                    os.remove(fp)
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
    logger("🎭 Opera Browser: análisis y limpieza de cache")

    analyze_only = False

    if is_opera_running():
        res = msg.askyesnocancel(
            "Opera está abierto",
            "Opera Browser está en ejecución.\n\n"
            "¿Deseas CERRARLO para limpiar completamente?\n\n"
            "✔ Sí = cerrar Opera y limpiar\n"
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
            close_opera(logger)

    total = len(CACHE_DIRS)
    total_freed = 0

    for i, rel in enumerate(CACHE_DIRS, start=1):
        if stop_event.is_set():
            logger("⛔ Operación cancelada")
            return total_freed

        full_path = os.path.join(OPERA_BASE, rel)
        logger(f"➡️ {'Analizando' if analyze_only else 'Limpiando'}: {full_path}")

        freed = clean_dir(full_path, logger, stop_event, analyze_only)
        total_freed += freed

        progress(int((i / total) * 100))

    mb = total_freed / (1024 * 1024)

    if analyze_only:
        logger(f"📊 Opera puede liberar: {mb:.2f} MB")
    else:
        logger(f"✅ Cache de Opera limpiada: {mb:.2f} MB liberados")

    return total_freed
