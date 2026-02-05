import os
import shutil
import tempfile

ADDON_INFO = {
    "id": "temp_files",
    "name": "Archivos temporales",
    "default": True
}

# Carpetas de temporales a limpiar
TEMP_PATHS = [
    tempfile.gettempdir(),                 # %TEMP%
    r"C:\Windows\Temp",                    # Windows Temp
]

def _get_size(path):
    """Calcula tamaño total en bytes"""
    total = 0
    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass
    return total

def _clean_path(path, logger, stop_event):
    """Limpia una carpeta de temporales"""
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

        # Carpetas
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
            except Exception:
                pass

    return freed

def run(logger, progress, stop_event):
    logger("🧹 Iniciando limpieza de archivos temporales...")

    total_paths = len(TEMP_PATHS)
    total_freed = 0

    for index, path in enumerate(TEMP_PATHS, start=1):
        if stop_event.is_set():
            logger("⛔ Limpieza de temporales cancelada")
            return

        logger(f"➡️ Limpiando: {path}")
        freed = _clean_path(path, logger, stop_event)
        total_freed += freed

        percent = int((index / total_paths) * 100)
        progress(percent)

    freed_mb = total_freed / (1024 * 1024)
    logger(f"✅ Temporales limpiados: {freed_mb:.2f} MB liberados")
