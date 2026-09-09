import src.cli as cli


COMMAND_KEYS = ("p", "q", "x", "r", "v", "d", "u", "g", "m", "s", "k", "h")


def test_dispatcher_executes_every_existing_timer_shortcut():
    dispatcher_type = getattr(cli, "CommandDispatcher", None)
    assert dispatcher_type is not None

    calls = []
    handlers = {
        key: (lambda current=key: calls.append(current)) for key in COMMAND_KEYS
    }
    dispatcher = dispatcher_type(handlers)

    for key in COMMAND_KEYS:
        assert dispatcher.dispatch(key) is True

    assert calls == list(COMMAND_KEYS)


def test_dispatcher_ignores_unknown_key_without_side_effects():
    dispatcher_type = getattr(cli, "CommandDispatcher", None)
    assert dispatcher_type is not None

    calls = []
    dispatcher = dispatcher_type({"p": lambda: calls.append("p")})

    assert dispatcher.dispatch("?") is False
    assert dispatcher.dispatch("") is False
    assert calls == []


def test_dispatcher_normalizes_command_case():
    dispatcher_type = getattr(cli, "CommandDispatcher", None)
    assert dispatcher_type is not None

    calls = []
    dispatcher = dispatcher_type({"p": lambda: calls.append("p")})

    assert dispatcher.dispatch("P") is True
    assert calls == ["p"]
