import os
import importlib.util

ADDONS_DIR = "addons"

class AddonManager:

    def __init__(self):
        self.addons = []

    def load_addons(self):
        self.addons.clear()

        for category in os.listdir(ADDONS_DIR):
            cat_path = os.path.join(ADDONS_DIR, category)
            if not os.path.isdir(cat_path):
                continue

            for file in os.listdir(cat_path):
                if not file.endswith(".py"):
                    continue

                addon_path = os.path.join(cat_path, file)
                addon = self._load_addon(addon_path, category)
                if addon:
                    self.addons.append(addon)

        return self.addons

    def _load_addon(self, path, category):
        spec = importlib.util.spec_from_file_location(path, path)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
        except Exception:
            return None

        if not hasattr(module, "ADDON_INFO") or not hasattr(module, "run"):
            return None

        info = module.ADDON_INFO.copy()
        info["category"] = category
        info["module"] = module
        return info
