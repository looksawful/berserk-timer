import sys
import os
import shutil
from typing import Optional, Callable
from rich.console import Console


class ScreenManager:
    ENTER_ALTERNATE_SCREEN = "\033[?1049h"
    EXIT_ALTERNATE_SCREEN = "\033[?1049l"
    CLEAR_SCREEN = "\033[2J"
    MOVE_CURSOR_HOME = "\033[H"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"
    SAVE_CURSOR = "\033[s"
    RESTORE_CURSOR = "\033[u"

    def __init__(self, use_alternate_buffer: bool = True, debug_mode: bool = False):
        self.use_alternate_buffer = use_alternate_buffer and not debug_mode
        self.debug_mode = debug_mode
        self.is_in_alternate = False
        self.console = Console()

    def enter_alternate_screen(self):
        if not self.use_alternate_buffer or self.is_in_alternate:
            return

        sys.stdout.write(self.ENTER_ALTERNATE_SCREEN)
        sys.stdout.write(self.CLEAR_SCREEN)
        sys.stdout.write(self.MOVE_CURSOR_HOME)
        sys.stdout.write(self.HIDE_CURSOR)
        sys.stdout.flush()

        self.is_in_alternate = True

    def exit_alternate_screen(self):
        if not self.use_alternate_buffer or not self.is_in_alternate:
            return

        sys.stdout.write(self.SHOW_CURSOR)
        sys.stdout.write(self.EXIT_ALTERNATE_SCREEN)
        sys.stdout.flush()

        self.is_in_alternate = False

    def clear_screen(self):
        if self.debug_mode:
            print("\n" + "=" * 80 + "\n")
            return

        if self.use_alternate_buffer:
            sys.stdout.write(self.CLEAR_SCREEN)
            sys.stdout.write(self.MOVE_CURSOR_HOME)
            sys.stdout.flush()
        else:
            try:
                self.console.clear()
            except Exception:
                os.system("cls" if os.name == "nt" else "clear")

    def get_terminal_size(self) -> tuple[int, int]:
        try:
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except Exception:
            return 80, 24

    def move_cursor(self, row: int, col: int):
        sys.stdout.write(f"\033[{row};{col}H")
        sys.stdout.flush()

    def clear_line(self):
        sys.stdout.write("\033[2K")
        sys.stdout.flush()

    def clear_from_cursor_down(self):
        sys.stdout.write("\033[J")
        sys.stdout.flush()

    def save_cursor_position(self):
        sys.stdout.write(self.SAVE_CURSOR)
        sys.stdout.flush()

    def restore_cursor_position(self):
        sys.stdout.write(self.RESTORE_CURSOR)
        sys.stdout.flush()

    def hide_cursor(self):
        sys.stdout.write(self.HIDE_CURSOR)
        sys.stdout.flush()

    def show_cursor(self):
        sys.stdout.write(self.SHOW_CURSOR)
        sys.stdout.flush()

    def render_block(self, render_func: Callable, *args, **kwargs):
        self.clear_screen()
        render_func(*args, **kwargs)
        sys.stdout.flush()

    def __enter__(self):
        self.enter_alternate_screen()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_alternate_screen()
        return False


class ScreenContext:
    def __init__(self, screen_manager: ScreenManager):
        self.screen_manager = screen_manager

    def __enter__(self):
        self.screen_manager.clear_screen()
        return self.screen_manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.flush()
        return False


_screen_manager: Optional[ScreenManager] = None


def get_screen_manager(
    use_alternate_buffer: bool = True, debug_mode: bool = False
) -> ScreenManager:
    global _screen_manager
    if _screen_manager is None:
        _screen_manager = ScreenManager(use_alternate_buffer, debug_mode)
    return _screen_manager


def init_screen(use_alternate_buffer: bool = True, debug_mode: bool = False):
    screen = get_screen_manager(use_alternate_buffer, debug_mode)
    screen.enter_alternate_screen()
    return screen


def cleanup_screen():
    global _screen_manager
    if _screen_manager:
        _screen_manager.exit_alternate_screen()
