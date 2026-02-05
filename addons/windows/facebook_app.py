import os
import shutil
import getpass

ADDON_INFO = {
    "id": "facebook_app",
    "name": "Facebook (aplicación de Windows)",
    "default": False
}

USER = getpass.getuser()
PACKAGES_DIR = rf"C:\Users\{USER}\AppData\Local\Packages"

# Prefijo típico del paquete Facebook
FACEBOOK_PREFIX = "Facebook.Facebook"

# Subcarpetas SEGURAS para limpiar
SAFE_DIRS = [
    "LocalCache",
    "TempState",
    "AC\\Temp",
]

def clean_dir(path, logger, stop_event):
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
                os.remove(fp)
                freed += size
            except Exception:
                pass

        for d in dirs:
            try:
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
            except Exception:
                pass

    return freed

def run(logger, progress, stop_event):
    logger("📘 Facebook (Windows): limpieza de cache y temporales")

    if not os.path.exists(PACKAGES_DIR):
        logger("ℹ️ No se encontró carpeta Packages")
        progress(100)
        return 0

    fb_packages = [
        d for d in os.listdir(PACKAGES_DIR)
        if d.startswith(FACEBOOK_PREFIX)
    ]

    if not fb_packages:
        logger("ℹ️ Facebook no está instalado como app de Windows")
        progress(100)
        return 0

    total_freed = 0
    total_tasks = len(fb_packages) * len(SAFE_DIRS)
    done = 0

    for pkg in fb_packages:
        base_path = os.path.join(PACKAGES_DIR, pkg)

        for rel in SAFE_DIRS:
            if stop_event.is_set():
                logger("⛔ Operación cancelada")
                return total_freed

            full_path = os.path.join(base_path, rel)
            logger(f"➡️ Limpiando: {full_path}")

            freed = clean_dir(full_path, logger, stop_event)
            total_freed += freed

            done += 1
            progress(int((done / total_tasks) * 100))

    mb = total_freed / (1024 * 1024)
    logger(f"✅ Facebook cache limpiada: {mb:.2f} MB liberados")

    return total_freed
