import os

ADDON_INFO = {
    "id": "prefetch",
    "name": "Prefetch (avanzado)",
    "default": False
}

PREFETCH_PATH = r"C:\Windows\Prefetch"

def run(logger, progress, stop_event):
    logger("⚠️ PREFETCH: limpieza avanzada")
    logger("ℹ️ Esta opción puede ralentizar el primer inicio de aplicaciones")
    logger("ℹ️ Windows regenerará estos archivos automáticamente")

    if not os.path.exists(PREFETCH_PATH):
        logger("❌ Carpeta Prefetch no encontrada")
        progress(100)
        return

    files = []
    try:
        files = os.listdir(PREFETCH_PATH)
    except Exception as e:
        logger(f"❌ Error accediendo a Prefetch: {e}")
        progress(100)
        return

    total = len(files)
    if total == 0:
        logger("ℹ️ Prefetch ya está vacío")
        progress(100)
        return

    deleted = 0

    for index, name in enumerate(files, start=1):
        if stop_event.is_set():
            logger("⛔ Limpieza de Prefetch cancelada")
            return

        file_path = os.path.join(PREFETCH_PATH, name)

        # SOLO archivos .pf
        if not name.lower().endswith(".pf"):
            continue

        try:
            os.remove(file_path)
            deleted += 1
        except Exception:
            pass

        percent = int((index / total) * 100)
        progress(percent)

    logger(f"✅ Prefetch limpiado: {deleted} archivos eliminados")
