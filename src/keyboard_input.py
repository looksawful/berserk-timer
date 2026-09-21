import select
import sys
from collections.abc import Callable


class KeyboardInputAdapter:
    def __init__(
        self,
        available: Callable[[], bool],
        read: Callable[[], str],
        *,
        preserve_printable_after_escape: bool = False,
    ) -> None:
        self._available = available
        self._read = read
        self._preserve_printable_after_escape = preserve_printable_after_escape
        self._pending_key: str | None = None

    def reset(self) -> None:
        self._pending_key = None

    def poll_key(self) -> str | None:
        if self._pending_key is not None:
            key = self._pending_key
            self._pending_key = None
        else:
            if not self._available():
                return None

            try:
                key = self._read()
            except (UnicodeDecodeError, OSError):
                return None

        try:
            code = ord(key[0]) if key else -1
        except (IndexError, TypeError):
            return None

        if code < 0:
            return None

        if code == 27:
            if self._available():
                try:
                    suffix = self._read()
                except (UnicodeDecodeError, OSError):
                    return None

                if suffix in ("[", "O"):
                    while self._available():
                        try:
                            sequence_key = self._read()
                        except (UnicodeDecodeError, OSError):
                            break
                        if sequence_key and 0x40 <= ord(sequence_key[0]) <= 0x7E:
                            break
                elif suffix and self._preserve_printable_after_escape:
                    self._pending_key = suffix
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

        return KeyboardInputAdapter(
            available,
            read,
            preserve_printable_after_escape=True,
        )

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
