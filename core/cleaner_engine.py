import threading

class CleanerEngine:

    def __init__(self, logger):
        self.logger = logger
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self, addons, progress_callback, done_callback, mode="clean"):
        self.stop_event.clear()
        total = len(addons)
        total_freed = 0

        for index, addon in enumerate(addons, start=1):
            if self.stop_event.is_set():
                self.logger.log("⛔ Operación detenida por el usuario")
                break

            self.logger.log(
                f"➡️ {addon['name']} ({'ANALIZAR' if mode == 'analyze' else 'LIMPIAR'})"
            )

            try:
                freed = addon["module"].run(
                    logger=self.logger.log,
                    progress=lambda p: progress_callback(index, total, p),
                    stop_event=self.stop_event,
                    mode=mode  # 👈 NUEVO
                )

                if isinstance(freed, int):
                    total_freed += freed

            except TypeError:
                # Compatibilidad con addons antiguos
                freed = addon["module"].run(
                    logger=self.logger.log,
                    progress=lambda p: progress_callback(index, total, p),
                    stop_event=self.stop_event
                )
                if isinstance(freed, int):
                    total_freed += freed

            except Exception as e:
                self.logger.log(f"❌ Error en {addon['name']}: {e}")

        done_callback(total_freed, mode)
