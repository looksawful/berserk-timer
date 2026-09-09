from collections.abc import Callable, Mapping

CommandHandler = Callable[[], None]


class CommandDispatcher:
    def __init__(self, handlers: Mapping[str, CommandHandler]) -> None:
        self._handlers = {key.lower(): handler for key, handler in handlers.items()}

    def dispatch(self, key: str) -> bool:
        if not key:
            return False
        handler = self._handlers.get(key.lower())
        if handler is None:
            return False
        handler()
        return True
