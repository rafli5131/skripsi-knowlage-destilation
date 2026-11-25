"""Preview bersama yang menunggu SIGUSR1 sebelum mulai merekam."""

import signal
import threading

from op3_fullscreen_preview import preview
from op3_fullscreen_preview.recorder import PreviewRecorder


class DeferredRecorder(PreviewRecorder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trigger = threading.Event()

    def start(self):
        signal.signal(signal.SIGUSR1, lambda *_: self.trigger.set())
        super().start()
        print("PEREKAM SIAGA: menunggu sinyal mulai setelah konfirmasi operator", flush=True)

    def run(self):
        while self.state.running.is_set():
            if self.trigger.wait(0.1):
                super().run()
                return
        self.finished.set()


if __name__ == "__main__":
    preview.PreviewRecorder = DeferredRecorder
    raise SystemExit(preview.main())
