import importlib
import importlib.util


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
