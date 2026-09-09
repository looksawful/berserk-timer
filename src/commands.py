from collections.abc import Callable, Mapping

CommandHandler = Callable[[], None]


def dispatch_command(key: str, handlers: Mapping[str, CommandHandler]) -> bool:
    if len(key) != 1:
        return False
    if ord(key) < 32 or ord(key) == 127:
        return False

    handler = handlers.get(key.lower())
    if handler is None:
        return False

    handler()
    return True
