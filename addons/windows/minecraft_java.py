import os
import shutil
import getpass

ADDON_INFO = {
    "id": "minecraft_java",
    "name": "Minecraft Java (cache y logs)",
    "default": True
}

USER = getpass.getuser()
MC_BASE = rf"C:\Users\{USER}\AppData\Roaming\.minecraft"

SAFE_DIRS = [
    "logs",
    "crash-reports",
    "webcache2",
    "cache",
]

SAFE_FILES = [
    "launcher_log.txt",
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
            try:
                if not analyze_only:
                    shutil.rmtree(os.path.join(root, d), ignore_errors=True)
            except Exception:
                pass

    return freed

def run(logger, progress, stop_event, mode="clean"):
    analyze_only = (mode == "analyze")
    logger("🎮 Minecraft Java: cache y logs")

    total_items = len(SAFE_DIRS) + len(SAFE_FILES)
    done = 0
    total_freed = 0

    for d in SAFE_DIRS:
        if stop_event.is_set():
            return total_freed

        full = os.path.join(MC_BASE, d)
        logger(f"➡️ {'Analizando' if analyze_only else 'Limpiando'}: {full}")
        total_freed += clean_dir(full, stop_event, analyze_only)

        done += 1
        progress(int((done / total_items) * 100))

    for f in SAFE_FILES:
        if stop_event.is_set():
            return total_freed

        full = os.path.join(MC_BASE, f)
        if os.path.exists(full):
            try:
                size = os.path.getsize(full)
                total_freed += size
                if not analyze_only:
                    os.remove(full)
            except Exception:
                pass

        done += 1
        progress(int((done / total_items) * 100))

    mb = total_freed / (1024 * 1024)
    logger(
        f"{'📊 Puede liberar' if analyze_only else '✅ Liberados'} "
        f"{mb:.2f} MB (Minecraft Java)"
    )

    return total_freed
