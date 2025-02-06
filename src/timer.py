import time
import threading
from .logger import log_event


class Timer:
    def __init__(self, duration, log_without_timer=False):
        """
        :param duration: Duration in seconds.
        :param log_without_timer: Flag to allow logging without running the timer.
        """
        self.duration = duration
        self.remaining = duration
        self._paused = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run)
        self.log_without_timer = log_without_timer

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        last_time = time.time()
        while self.get_remaining_time() > 0 and not self._stop_event.is_set():
            time.sleep(0.1)
            if self._paused:
                last_time = time.time()
                continue
            now = time.time()
            elapsed = now - last_time
            with self._lock:
                self.remaining -= elapsed
                if self.remaining < 0:
                    self.remaining = 0
            last_time = now

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join()

    def is_running(self):
        return self._thread.is_alive()

    def get_remaining_time(self):
        with self._lock:
            return self.remaining

    def get_remaining_time_str(self):
        remaining = int(self.get_remaining_time())
        minutes, seconds = divmod(remaining, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def zero(self):
        with self._lock:
            self.remaining = 0
        self.stop()

    def restart(self):
        self.stop()
        with self._lock:
            self.remaining = self.duration
        self._paused = False
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def update_duration(self, new_duration):
        """Update the timer's duration and remaining time."""
        with self._lock:
            self.duration = new_duration
            self.remaining = new_duration

    def log_data(self, message):
        if self.log_without_timer:
            log_event(message)
        else:
            print("Timer must be running to log data.")
