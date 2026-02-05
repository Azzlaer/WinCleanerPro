import ctypes

ADDON_INFO = {
    "id": "recycle_bin",
    "name": "Papelera de reciclaje",
    "default": True
}

# Flags de SHEmptyRecycleBinW
SHERB_NOCONFIRMATION = 0x00000001
SHERB_NOPROGRESSUI = 0x00000002
SHERB_NOSOUND = 0x00000004

def run(logger, progress, stop_event):
    logger("♻️ Vaciando papelera de reciclaje...")

    if stop_event.is_set():
        logger("⛔ Operación cancelada")
        return

    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(
            None,
            None,
            SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
        )
        progress(100)
        logger("✅ Papelera vaciada correctamente")
    except Exception as e:
        logger(f"❌ Error al vaciar la papelera: {e}")
