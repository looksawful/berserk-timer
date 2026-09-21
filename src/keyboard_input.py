import select
import sys
from collections.abc import Callable


class KeyboardInputAdapter:
    def __init__(
        self,
        available: Callable[[], bool],
        read: Callable[[], str],
    ) -> None:
        self._available = available
        self._read = read

    def poll_key(self) -> str | None:
        if not self._available():
            return None

        try:
            key = self._read()
        except (UnicodeDecodeError, OSError):
            return None

        if not key:
            return None

        code = ord(key[0])

        if code == 27:
            while self._available():
                try:
                    self._read()
                except (UnicodeDecodeError, OSError):
                    break
            return None

        if code == 224:
            if self._available():
                try:
                    self._read()
                except (UnicodeDecodeError, OSError):
                    pass
            return None

        if code < 32:
            return None

        return key


def create_platform_keyboard_input() -> KeyboardInputAdapter:
    if sys.platform.startswith("win"):
        import msvcrt

        def available() -> bool:
            return msvcrt.kbhit()

        def read() -> str:
            return msvcrt.getch().decode("utf-8", errors="ignore")

        return KeyboardInputAdapter(available, read)

    import termios
    import tty

    def available() -> bool:
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(ready)

    def read() -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return KeyboardInputAdapter(available, read)
