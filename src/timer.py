import time
import threading
import logging
from typing import Optional
from .logger import log_event
from .constants import MAX_TIMER_SECONDS


class TimerDurationError(ValueError):
    pass


class Timer:
    MIN_DURATION = 1
    MAX_DURATION = MAX_TIMER_SECONDS

    def __init__(
        self,
        duration: float,
        log_without_timer: bool = False,
        goal: Optional[str] = None,
        sound_file: str = "alert1.wav",
        volume: int = 5,
    ) -> None:
        self._validate_duration(duration)
        self.duration = duration
        self.remaining = duration
        self._paused = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run)
        self.log_without_timer = log_without_timer
        self.goal = goal
        self.sound_file = sound_file
        self.volume = max(0, min(10, volume))
        self._silent = self.volume == 0
        self._previous_volume = self.volume or 5
        self._zeroed = False

    @classmethod
    def _validate_duration(cls, duration: float) -> None:
        if duration <= 0:
            raise TimerDurationError("Duration must be positive")
        if duration < cls.MIN_DURATION:
            raise TimerDurationError(
                f"Duration must be at least {cls.MIN_DURATION} second(s)"
            )
        if duration > cls.MAX_DURATION:
            hours = cls.MAX_DURATION // 3600
            raise TimerDurationError(f"Duration cannot exceed {hours} hours")

    def start(self) -> None:
        if self.is_running():
            return
        with self._lock:
            self.remaining = self.duration
            self._paused = False
            self._zeroed = False
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

    def is_paused(self) -> bool:
        return self._paused

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
        hours, remainder = divmod(remaining, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"

        if self.goal:
            return f"{time_str} [Goal: {self.goal}]"
        return time_str

    def zero(self) -> None:
        with self._lock:
            self.remaining = 0
            self._zeroed = True
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
        self._validate_duration(new_duration)
        with self._lock:
            self.duration = new_duration
            self.remaining = new_duration

    def set_goal(self, goal: Optional[str]) -> None:
        self.goal = goal

    def get_goal(self) -> Optional[str]:
        return self.goal

    def log_data(self, message: str) -> None:
        if self.log_without_timer:
            log_event(message)
        else:
            logging.error("Timer must be running to log data.")

    def toggle_silent(self) -> None:
        if not self._silent:
            if self.volume > 0:
                self._previous_volume = self.volume
            self.volume = 0
            self._silent = True
        else:
            restore = self._previous_volume if self._previous_volume > 0 else 5
            self.volume = max(0, min(10, restore))
            self._silent = self.volume == 0

    def is_silent(self) -> bool:
        return self._silent

    def set_sound_file(self, sound_file: str) -> None:
        self.sound_file = sound_file

    def get_sound_file(self) -> str:
        return self.sound_file

    def set_volume(self, volume: int) -> None:
        volume = max(0, min(10, volume))

        if volume == 0:
            if self.volume > 0:
                self._previous_volume = self.volume
            self._silent = True
        else:
            self._silent = False
            self._previous_volume = volume

        self.volume = volume

    def get_volume(self) -> int:
        return self.volume

    def was_zeroed(self) -> bool:
        return self._zeroed
