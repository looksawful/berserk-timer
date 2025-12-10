import threading
import time
from typing import Optional
from .events import EventBus, Event, EventType, get_event_bus


class TimerCore:
    def __init__(
        self,
        duration: float,
        event_bus: Optional[EventBus] = None,
        goal: Optional[str] = None,
        sound_file: str = "alert1.wav",
        volume: int = 5,
        silent: bool = False,
    ):
        self._event_bus = event_bus or get_event_bus()
        self._duration = duration
        self._remaining = duration
        self._goal = goal
        self._sound_file = sound_file
        self._volume = volume
        self._silent = silent
        self._paused = False
        self._running = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._subscribe_to_commands()

    def _subscribe_to_commands(self):
        self._event_bus.subscribe(
            EventType.USER_PAUSE_REQUESTED, self._handle_pause_request
        )
        self._event_bus.subscribe(
            EventType.USER_RESUME_REQUESTED, self._handle_resume_request
        )
        self._event_bus.subscribe(
            EventType.USER_STOP_REQUESTED, self._handle_stop_request
        )
        self._event_bus.subscribe(
            EventType.USER_ZERO_REQUESTED, self._handle_zero_request
        )
        self._event_bus.subscribe(
            EventType.USER_RESTART_REQUESTED, self._handle_restart_request
        )
        self._event_bus.subscribe(
            EventType.USER_UPDATE_DURATION_REQUESTED, self._handle_update_duration
        )
        self._event_bus.subscribe(
            EventType.USER_SET_GOAL_REQUESTED, self._handle_set_goal
        )
        self._event_bus.subscribe(
            EventType.USER_TOGGLE_MUTE_REQUESTED, self._handle_toggle_mute
        )

    def _handle_pause_request(self, event: Event):
        if not self._paused:
            self.pause()

    def _handle_resume_request(self, event: Event):
        if self._paused:
            self.resume()

    def _handle_stop_request(self, event: Event):
        self.stop()

    def _handle_zero_request(self, event: Event):
        self.zero()

    def _handle_restart_request(self, event: Event):
        self.restart()

    def _handle_update_duration(self, event: Event):
        new_duration = event.data.get("duration")
        if new_duration:
            self.update_duration(new_duration)

    def _handle_set_goal(self, event: Event):
        goal = event.data.get("goal")
        if goal:
            self.set_goal(goal)

    def _handle_toggle_mute(self, event: Event):
        self.toggle_silent()

    def start(self):
        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._countdown, daemon=True)
        self._thread.start()

        self._event_bus.publish(
            Event(
                EventType.TIMER_STARTED,
                {"duration": self._duration, "goal": self._goal},
            )
        )

    def pause(self):
        with self._lock:
            if not self._paused:
                self._paused = True
                self._event_bus.publish(Event(EventType.TIMER_PAUSED))

    def resume(self):
        with self._lock:
            if self._paused:
                self._paused = False
                self._event_bus.publish(Event(EventType.TIMER_RESUMED))

    def stop(self):
        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        self._event_bus.publish(Event(EventType.TIMER_STOPPED))

    def zero(self):
        with self._lock:
            self._remaining = 0
        self.stop()
        self._event_bus.publish(Event(EventType.TIMER_ZEROED))

    def restart(self):
        self.stop()
        time.sleep(0.1)
        with self._lock:
            self._remaining = self._duration
            self._paused = False
        self.start()
        self._event_bus.publish(Event(EventType.TIMER_RESTARTED))

    def update_duration(self, new_duration: float):
        with self._lock:
            self._duration = new_duration
            self._remaining = new_duration

        self._event_bus.publish(
            Event(EventType.TIMER_DURATION_UPDATED, {"duration": new_duration})
        )

    def set_goal(self, goal: str):
        with self._lock:
            self._goal = goal

    def toggle_silent(self):
        with self._lock:
            self._silent = not self._silent
            return self._silent

    def is_paused(self) -> bool:
        return self._paused

    def is_running(self) -> bool:
        return self._running

    def is_silent(self) -> bool:
        return self._silent

    def get_remaining_time(self) -> float:
        with self._lock:
            return self._remaining

    def get_remaining_time_str(self) -> str:
        remaining = self.get_remaining_time()
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def get_goal(self) -> Optional[str]:
        return self._goal

    def get_volume(self) -> int:
        return self._volume

    def set_volume(self, volume: int):
        with self._lock:
            self._volume = max(0, min(10, volume))

    def get_sound_file(self) -> str:
        return self._sound_file

    def set_sound_file(self, sound_file: str):
        with self._lock:
            self._sound_file = sound_file

    def _countdown(self):
        while self._running and self._remaining > 0:
            if self._stop_event.is_set():
                break

            if not self._paused:
                with self._lock:
                    self._remaining -= 0.1
                    if self._remaining < 0:
                        self._remaining = 0

                    remaining_str = self.get_remaining_time_str()

                self._event_bus.publish(
                    Event(
                        EventType.TIMER_TICK,
                        {
                            "remaining": self._remaining,
                            "remaining_str": remaining_str,
                            "is_paused": self._paused,
                            "is_silent": self._silent,
                        },
                    )
                )

            time.sleep(0.1)

        if self._remaining <= 0 and self._running:
            self._running = False
            self._event_bus.publish(
                Event(
                    EventType.TIMER_FINISHED,
                    {
                        "goal": self._goal,
                        "sound_file": self._sound_file,
                        "volume": self._volume,
                        "silent": self._silent,
                    },
                )
            )
