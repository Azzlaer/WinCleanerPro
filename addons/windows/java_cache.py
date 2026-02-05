import os
import shutil
import getpass

ADDON_INFO = {
    "id": "java_cache",
    "name": "Java (cache y temporales)",
    "default": True
}

USER = getpass.getuser()

JAVA_CACHE_PATHS = [
    rf"C:\Users\{USER}\AppData\LocalLow\Sun\Java\Deployment\cache",
    rf"C:\Users\{USER}\AppData\Local\Temp\javaws",
]

def clean_dir(path, logger, stop_event, analyze_only=False):
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

def run(logger, progress, stop_event, mode="clean"):
    analyze_only = (mode == "analyze")

    logger("☕ Java: análisis y limpieza de cache")

    total_paths = len(JAVA_CACHE_PATHS)
    total_freed = 0

    for i, path in enumerate(JAVA_CACHE_PATHS, start=1):
        if stop_event.is_set():
            logger("⛔ Operación cancelada")
            return total_freed

        if analyze_only:
            logger(f"➡️ Analizando: {path}")
        else:
            logger(f"➡️ Limpiando: {path}")

        freed = clean_dir(path, logger, stop_event, analyze_only)
        total_freed += freed

        progress(int((i / total_paths) * 100))

    mb = total_freed / (1024 * 1024)

    if analyze_only:
        logger(f"📊 Java puede liberar: {mb:.2f} MB")
    else:
        logger(f"✅ Cache de Java limpiada: {mb:.2f} MB liberados")

    return total_freed
