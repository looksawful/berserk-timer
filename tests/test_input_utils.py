import importlib
import importlib.util


def _input_utils_module():
    spec = importlib.util.find_spec("src.input_utils")
    assert spec is not None, "src.input_utils must normalize EOF/Ctrl+C input"
    return importlib.import_module("src.input_utils")


def test_read_input_returns_user_text(monkeypatch) -> None:
    input_utils = _input_utils_module()
    monkeypatch.setattr("builtins.input", lambda _prompt="": "hello")

    assert input_utils.read_input("prompt") == "hello"


def test_read_input_returns_none_on_eof(monkeypatch) -> None:
    input_utils = _input_utils_module()

    def raise_eof(_prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)

    assert input_utils.read_input("prompt") is None


def test_read_input_returns_none_on_keyboard_interrupt(monkeypatch) -> None:
    input_utils = _input_utils_module()

    def raise_interrupt(_prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_interrupt)

    assert input_utils.read_input("prompt") is None
