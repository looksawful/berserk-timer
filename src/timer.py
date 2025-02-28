"""Module timer.py: Implements a Timer class for the Berserk Timer application."""
import time
import threading
from typing import Optional
from .logger import log_event


class Timer:
    def __init__(self, duration: float, log_without_timer: bool = False, goal: Optional[str] = None) -> None:
        """Initializes the Timer instance.
        Args:
            duration (float): Duration in seconds.
            log_without_timer (bool): Flag to log data without running timer.
            goal (Optional[str]): Optional goal associated with the timer.
        Returns:
            None
        """
        self.duration = duration
        self.duration = duration
        self.remaining = duration
        self._paused = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run)
        self.log_without_timer = log_without_timer
        self.goal = goal
        self._silent = False

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self) -> None:
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

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join()

    def is_running(self) -> bool:
        return self._thread.is_alive()

    def get_remaining_time(self) -> float:
        with self._lock:
            return self.remaining

    def get_remaining_time_str(self) -> str:
        remaining = int(self.get_remaining_time())
        minutes, seconds = divmod(remaining, 60)
        if self.goal:
            return f"{minutes:02d}:{seconds:02d} [Goal: {self.goal}]"
        return f"{minutes:02d}:{seconds:02d}"

    def zero(self) -> None:
        with self._lock:
            self.remaining = 0
        self.stop()

    def restart(self) -> None:
        self.stop()
        with self._lock:
            self.remaining = self.duration
        self._paused = False
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def update_duration(self, new_duration: float) -> None:
        with self._lock:
            self.duration = new_duration
            self.remaining = new_duration

    def set_goal(self, goal: str) -> None:
        self.goal = goal

    def log_data(self, message: str) -> None:
        if self.log_without_timer:
            log_event(message)
        else:
            logging.error("Timer must be running to log data.")

    def toggle_silent(self) -> None:
        self._silent = not self._silent

    def is_silent(self) -> bool:
        return self._silent
