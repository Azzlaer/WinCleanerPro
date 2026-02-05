import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "clean.log")

class Logger:

    def __init__(self, ui_callback=None):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.ui_callback = ui_callback

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"

        if self.ui_callback:
            self.ui_callback(line)

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
