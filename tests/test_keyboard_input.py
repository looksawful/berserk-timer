import pytest

from src.keyboard_input import KeyboardInputAdapter


def _adapter(values: list[str]) -> tuple[KeyboardInputAdapter, list[str]]:
    queue = list(values)

    def available() -> bool:
        return bool(queue)

    def read() -> str:
        return queue.pop(0)

    return KeyboardInputAdapter(available, read), queue


def test_poll_key_returns_printable_key() -> None:
    adapter, queue = _adapter(["P"])

    assert adapter.poll_key() == "P"
    assert queue == []


def test_poll_key_returns_none_when_no_key_is_available() -> None:
    reads = 0

    def read() -> str:
        nonlocal reads
        reads += 1
        return "p"

    adapter = KeyboardInputAdapter(lambda: False, read)

    assert adapter.poll_key() is None
    assert reads == 0


@pytest.mark.parametrize("raw_key", ["", "\x03"])
def test_poll_key_ignores_empty_and_control_input(raw_key: str) -> None:
    adapter, _queue = _adapter([raw_key])

    assert adapter.poll_key() is None


def test_poll_key_drains_escape_sequence() -> None:
    adapter, queue = _adapter(["\x1b", "[", "A"])

    assert adapter.poll_key() is None
    assert queue == []


def test_poll_key_preserves_printable_key_queued_after_escape() -> None:
    adapter, queue = _adapter(["\x1b", "k"])

    assert adapter.poll_key() is None
    assert adapter.poll_key() == "k"
    assert queue == []


def test_poll_key_discards_alt_prefixed_printable_key_by_default() -> None:
    adapter, queue = _adapter(["\x1b", "x"])

    assert adapter.poll_key() is None
    assert adapter.poll_key() is None
    assert queue == []


def test_poll_key_drains_windows_extended_key_suffix() -> None:
    adapter, queue = _adapter(["\xe0", "K"])

    assert adapter.poll_key() is None
    assert queue == []


@pytest.mark.parametrize(
    "error",
    [
        OSError("read failed"),
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid"),
    ],
)
def test_poll_key_ignores_raw_read_errors(error: Exception) -> None:
    def read() -> str:
        raise error

    adapter = KeyboardInputAdapter(lambda: True, read)

    assert adapter.poll_key() is None
