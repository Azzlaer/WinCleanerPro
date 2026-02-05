import os
import shutil

ADDON_INFO = {
    "id": "windows_cache",
    "name": "Cache de Windows",
    "default": True
}

# Rutas SEGURAS de cache de Windows
CACHE_PATHS = [
    r"C:\Windows\SoftwareDistribution\Download",   # Cache de Windows Update
    r"C:\Windows\Logs",                              # Logs antiguos
]

def _get_size(path):
    total = 0
    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass
    return total

def _clean_path(path, logger, stop_event):
    freed = 0

    if not os.path.exists(path):
        return 0

    for root, dirs, files in os.walk(path, topdown=False):
        if stop_event.is_set():
            return freed

        # Archivos
        for name in files:
            file_path = os.path.join(root, name)
            try:
                size = os.path.getsize(file_path)
                os.remove(file_path)
                freed += size
            except Exception:
                pass

        # Carpetas vacías
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
            except Exception:
                pass

    return freed

def run(logger, progress, stop_event):
    logger("🪟 Iniciando limpieza de cache de Windows...")

    total_paths = len(CACHE_PATHS)
    total_freed = 0

    for index, path in enumerate(CACHE_PATHS, start=1):
        if stop_event.is_set():
            logger("⛔ Limpieza de cache de Windows cancelada")
            return

        logger(f"➡️ Limpiando: {path}")
        freed = _clean_path(path, logger, stop_event)
        total_freed += freed

        percent = int((index / total_paths) * 100)
        progress(percent)

    freed_mb = total_freed / (1024 * 1024)
    logger(f"✅ Cache de Windows limpiada: {freed_mb:.2f} MB liberados")
