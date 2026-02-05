import os
import shutil
from addons.windows._steam_utils import detect_steam_path, ask_steam_path
from core.config import ConfigManager

ADDON_INFO = {
    "id": "steam_cache",
    "name": "Steam (cache y logs)",
    "default": True
}

config = ConfigManager()

SAFE_DIRS = ["appcache", "logs", "dump"]

def clean_dir(path, stop_event, analyze_only):
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
            if not analyze_only:
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)

    return freed

def run(logger, progress, stop_event, mode="clean"):
    analyze_only = (mode == "analyze")

    steam_path = config.get_path("steam_path")

    if not steam_path:
        steam_path = detect_steam_path()
        if steam_path:
            config.set_path("steam_path", steam_path)
            logger(f"✔ Steam detectado automáticamente: {steam_path}")
        else:
            logger("⚠️ No se pudo detectar Steam automáticamente")
            steam_path = ask_steam_path()
            if not steam_path:
                logger("⛔ Operación cancelada: Steam no configurado")
                return 0
            config.set_path("steam_path", steam_path)
            logger(f"✔ Steam configurado manualmente: {steam_path}")

    total = len(SAFE_DIRS)
    total_freed = 0

    for i, d in enumerate(SAFE_DIRS, start=1):
        if stop_event.is_set():
            return total_freed

        full = os.path.join(steam_path, d)
        logger(f"➡️ {'Analizando' if analyze_only else 'Limpiando'}: {full}")
        total_freed += clean_dir(full, stop_event, analyze_only)
        progress(int((i / total) * 100))

    logger(
        f"{'📊 Puede liberar' if analyze_only else '✅ Liberados'} "
        f"{total_freed / (1024 * 1024):.2f} MB (Steam cache)"
    )

    return total_freed
