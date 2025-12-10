from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from enum import Enum, auto
import threading
import queue


class EventType(Enum):
    TIMER_STARTED = auto()
    TIMER_PAUSED = auto()
    TIMER_RESUMED = auto()
    TIMER_STOPPED = auto()
    TIMER_ZEROED = auto()
    TIMER_RESTARTED = auto()
    TIMER_TICK = auto()
    TIMER_FINISHED = auto()
    TIMER_DURATION_UPDATED = auto()

    USER_PAUSE_REQUESTED = auto()
    USER_RESUME_REQUESTED = auto()
    USER_STOP_REQUESTED = auto()
    USER_ZERO_REQUESTED = auto()
    USER_RESTART_REQUESTED = auto()
    USER_UPDATE_DURATION_REQUESTED = auto()
    USER_SET_GOAL_REQUESTED = auto()
    USER_TOGGLE_MUTE_REQUESTED = auto()
    USER_VIEW_LOG_REQUESTED = auto()
    USER_DELETE_LOG_REQUESTED = auto()
    USER_CHANGE_SOUND_REQUESTED = auto()
    USER_STOP_SOUND_REQUESTED = auto()
    USER_HELP_REQUESTED = auto()

    SYSTEM_SHUTDOWN = auto()
    SYSTEM_ERROR = auto()


@dataclass
class Event:
    type: EventType
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._lock = threading.Lock()
        self._queue: "queue.Queue[Event]" = queue.Queue()
        self._stop_event = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def subscribe(
        self, event_type: EventType, handler: Callable[[Event], None]
    ) -> None:
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    def unsubscribe(
        self, event_type: EventType, handler: Callable[[Event], None]
    ) -> None:
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                except ValueError:
                    pass

    def publish(self, event: Event) -> None:
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            print(f"Dropping event {event.type}: queue is full")

    def clear(self) -> None:
        with self._lock:
            self._subscribers.clear()
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def stop(self) -> None:
        self._stop_event.set()
        self._queue.put(Event(EventType.SYSTEM_SHUTDOWN))
        if self._worker.is_alive():
            self._worker.join(timeout=1.0)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                event = self._queue.get()
            except Exception:
                continue

            if event.type == EventType.SYSTEM_SHUTDOWN and self._stop_event.is_set():
                break

            with self._lock:
                handlers = self._subscribers.get(event.type, []).copy()

            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler for {event.type}: {e}")

            self._queue.task_done()


_event_bus = EventBus()


def get_event_bus() -> EventBus:
    return _event_bus
