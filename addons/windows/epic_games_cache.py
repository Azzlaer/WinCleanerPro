import os
import shutil
from core.config import ConfigManager
from addons.windows._epic_utils import detect_epic_path, ask_epic_path

ADDON_INFO = {
    "id": "epic_games_cache",
    "name": "Epic Games Launcher (cache y logs)",
    "default": True
}

config = ConfigManager()

SAFE_DIRS = [
    os.path.join("EpicGamesLauncher", "Saved", "webcache"),
    os.path.join("EpicGamesLauncher", "Saved", "webcache_4147"),
    os.path.join("EpicGamesLauncher", "Saved", "Logs"),
]

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
    logger("🎮 Epic Games Launcher: cache y logs")

    epic_path = config.get_path("epic_path")

    if not epic_path:
        epic_path = detect_epic_path()
        if epic_path:
            config.set_path("epic_path", epic_path)
            logger(f"✔ Epic detectado automáticamente: {epic_path}")
        else:
            logger("⚠️ No se pudo detectar Epic automáticamente")
            epic_path = ask_epic_path()
            if not epic_path:
                logger("⛔ Operación cancelada: Epic no configurado")
                return 0
            config.set_path("epic_path", epic_path)
            logger(f"✔ Epic configurado manualmente: {epic_path}")

    total = len(SAFE_DIRS)
    total_freed = 0

    for i, rel in enumerate(SAFE_DIRS, start=1):
        if stop_event.is_set():
            return total_freed

        full = os.path.join(epic_path, rel)
        logger(f"➡️ {'Analizando' if analyze_only else 'Limpiando'}: {full}")

        total_freed += clean_dir(full, stop_event, analyze_only)
        progress(int((i / total) * 100))

    logger(
        f"{'📊 Puede liberar' if analyze_only else '✅ Liberados'} "
        f"{total_freed / (1024 * 1024):.2f} MB (Epic Games Launcher)"
    )

    return total_freed
