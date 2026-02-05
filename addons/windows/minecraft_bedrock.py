import os
import shutil
import getpass

ADDON_INFO = {
    "id": "minecraft_bedrock",
    "name": "Minecraft Bedrock (cache y logs)",
    "default": True
}

USER = getpass.getuser()
BEDROCK_BASE = (
    rf"C:\Users\{USER}\AppData\Local\Packages"
    r"\Microsoft.MinecraftUWP_8wekyb3d8bbwe"
)

SAFE_DIRS = [
    "LocalCache",
    "TempState",
    "AC\\Temp",
    "logs",
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
    logger("🎮 Minecraft Bedrock: cache y logs")

    if not os.path.exists(BEDROCK_BASE):
        logger("ℹ️ Minecraft Bedrock no está instalado")
        progress(100)
        return 0

    total = len(SAFE_DIRS)
    total_freed = 0

    for i, d in enumerate(SAFE_DIRS, start=1):
        if stop_event.is_set():
            return total_freed

        full = os.path.join(BEDROCK_BASE, d)
        logger(f"➡️ {'Analizando' if analyze_only else 'Limpiando'}: {full}")

        total_freed += clean_dir(full, stop_event, analyze_only)
        progress(int((i / total) * 100))

    mb = total_freed / (1024 * 1024)
    logger(
        f"{'📊 Puede liberar' if analyze_only else '✅ Liberados'} "
        f"{mb:.2f} MB (Minecraft Bedrock)"
    )

    return total_freed
