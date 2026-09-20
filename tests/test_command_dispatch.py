import importlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _commands_module():
    spec = importlib.util.find_spec("src.commands")
    assert spec is not None, "src.commands must provide raw-key-independent dispatch"
    return importlib.import_module("src.commands")


def test_dispatch_command_executes_matching_handler_case_insensitively() -> None:
    commands = _commands_module()
    calls: list[str] = []
    handlers = {"p": lambda: calls.append("pause")}

    handled = commands.dispatch_command("P", handlers)

    assert handled is True
    assert calls == ["pause"]


def test_dispatch_command_rejects_unknown_or_invalid_keys_without_side_effects() -> None:
    commands = _commands_module()
    calls: list[str] = []
    handlers = {"p": lambda: calls.append("pause")}

    assert commands.dispatch_command("z", handlers) is False
    assert commands.dispatch_command("", handlers) is False
    assert commands.dispatch_command("pp", handlers) is False
    assert commands.dispatch_command("\x1b", handlers) is False
    assert calls == []


def test_cli_keyboard_loop_delegates_routing_to_dispatcher() -> None:
    source = (ROOT / "src" / "cli.py").read_text(encoding="utf-8")

    assert "from .commands import dispatch_command" in source
    assert "dispatch_command(key, commands)" in source
    assert "if key in commands:" not in source


def test_cli_exposes_command_handler_factory_without_starting_keyboard_listener() -> None:
    cli = importlib.import_module("src.cli")

    assert hasattr(cli, "build_timer_command_handlers")


def test_command_handler_factory_preserves_command_surface_and_simple_actions() -> None:
    cli = importlib.import_module("src.cli")
    calls: list[str] = []

    class FakeTimer:
        def is_paused(self) -> bool:
            return False

        def pause(self) -> None:
            calls.append("pause")

        def resume(self) -> None:
            calls.append("resume")

        def zero(self) -> None:
            calls.append("zero")

        def restart(self) -> None:
            calls.append("restart")

    handlers = cli.build_timer_command_handlers(FakeTimer())

    assert set(handlers) == set("pqxrvdugmskh")
    handlers["p"]()
    handlers["x"]()
    handlers["r"]()
    assert calls == ["pause", "zero", "restart"]
