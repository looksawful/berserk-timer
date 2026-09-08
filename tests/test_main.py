import argparse

import pytest

import src.main as main


def _args(**overrides):
    values = {
        "duration": None,
        "seconds": False,
        "x": False,
        "s": False,
        "m": False,
        "l": False,
        "X": False,
        "t": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_calculate_duration_converts_minutes_to_seconds():
    duration = main.calculate_duration(_args(duration=1.5), {"presets": {}})
    assert duration == 90


def test_calculate_duration_preserves_seconds_mode():
    duration = main.calculate_duration(
        _args(duration=90, seconds=True), {"presets": {}}
    )
    assert duration == 90


def test_calculate_duration_uses_configured_preset():
    duration = main.calculate_duration(_args(s=True), {"presets": {"s": 12}})
    assert duration == 12 * 60


def test_calculate_duration_rejects_out_of_range_value(capsys):
    with pytest.raises(SystemExit):
        main.calculate_duration(_args(duration=0), {"presets": {}})
    assert "Duration must be positive" in capsys.readouterr().out


def test_windows_stdout_configuration_reconfigures_without_detaching(monkeypatch):
    calls = []

    class HostStream:
        def reconfigure(self, **kwargs):
            calls.append(kwargs)

        def detach(self):
            raise AssertionError("host stdout must never be detached")

    monkeypatch.setattr(main.sys, "platform", "win32")
    monkeypatch.setattr(main.sys, "stdout", HostStream())

    main.configure_stdout_encoding()

    assert calls == [{"encoding": "utf-8"}]
