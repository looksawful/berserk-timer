"""Privacy contract: an opt-out session must not persist its goal (Issue #39)."""

import argparse

import pytest

import src.logger as logger
import src.session as session


def test_witness_disabled_does_not_persist_goal_or_create_witness_log(
    monkeypatch, tmp_path
):
    private_goal = "PRIVATE-GOAL-ISSUE-39"
    messages = []
    monkeypatch.setattr(logger, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logger, "LOG_READY", True)
    monkeypatch.setattr(session, "log_event", messages.append)

    def stop_timer(timer):
        timer.stop()
        return True

    monkeypatch.setattr(session, "run_cli_timer", stop_timer)

    with pytest.raises(SystemExit) as exit_info:
        session.run_timer_loop(
            argparse.Namespace(seconds=False, sound=None, mute=False),
            {"volume": 5, "sound_file": "alert1.wav"},
            60,
            False,
            None,
            private_goal,
            False,
        )

    assert exit_info.value.code == 0
    assert not list(tmp_path.glob("witness_log_*.txt"))
    assert all(private_goal not in message for message in messages)


def test_witness_disabled_completion_does_not_create_witness_log(monkeypatch, tmp_path):
    from src.timer import Timer

    monkeypatch.setattr(logger, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logger, "LOG_READY", True)

    timer = Timer(60, volume=0)
    session.on_timer_end(timer, False, {"messages": []}, None)

    assert not list(tmp_path.glob("witness_log_*.txt"))


def test_fresh_config_witness_is_opt_in(tmp_path):
    import json

    from src.config_manager import load_config

    path = tmp_path / "new-config.json"
    loaded = load_config(path)

    assert loaded["witness_mode"] is False
    assert json.loads(path.read_text(encoding="utf-8"))["witness_mode"] is False


def test_existing_witness_preference_survives_new_default(tmp_path):
    import json

    from src.config_manager import load_config

    path = tmp_path / "existing-config.json"
    path.write_text(json.dumps({"witness_mode": True, "volume": 7}), encoding="utf-8")

    loaded = load_config(path)

    assert loaded["witness_mode"] is True
    assert loaded["volume"] == 7
    assert json.loads(path.read_text(encoding="utf-8"))["witness_mode"] is True


@pytest.mark.parametrize(
    ("argv", "saved_witness", "expected"),
    [
        (["berserk", "1", "--no-witness"], True, False),
        (["berserk", "1", "-w"], False, True),
        (["berserk", "1", "--witness"], False, True),
        (["berserk", "1"], True, True),
        (["berserk", "1"], False, False),
    ],
)
def test_explicit_cli_witness_preference_overrides_saved_config(
    monkeypatch, argv, saved_witness, expected
):
    import sys

    import src.main as main

    recorded = []
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(main, "configure_stdout_encoding", lambda: None)
    monkeypatch.setattr(main, "render_startup_screen", lambda *a, **k: None)
    monkeypatch.setattr(
        main,
        "load_config",
        lambda: {"witness_mode": saved_witness, "presets": {}},
    )
    monkeypatch.setattr(main, "prompt_input", lambda *a, **k: "")
    monkeypatch.setattr(main, "init_screen", lambda **k: None)
    monkeypatch.setattr(main.atexit, "register", lambda callback: None)
    monkeypatch.setattr(main, "log_event", lambda message: None)
    monkeypatch.setattr(
        main,
        "run_timer_loop",
        lambda args, config, duration, witness_mode, *rest: recorded.append(
            witness_mode
        ),
    )

    main.main()

    assert recorded == [expected]


def test_witness_disabled_does_not_log_private_custom_advice(monkeypatch, caplog):
    import logging

    from src.timer import Timer

    timer = Timer(60, volume=0)
    with caplog.at_level(logging.INFO):
        session.on_timer_end(
            timer,
            False,
            {"messages": ["Default"]},
            "PRIVATE-ADVICE-ISSUE-39",
        )

    assert "PRIVATE-ADVICE-ISSUE-39" not in caplog.text


@pytest.mark.parametrize(
    ("response", "expect_answer"),
    [
        ("Completed the task", True),
        ("Witness skipped.", False),
    ],
)
def test_opted_in_witness_preserves_existing_log_and_appends_response(
    monkeypatch, tmp_path, response, expect_answer
):
    import re
    import time

    from src.timer import Timer

    monkeypatch.setattr(logger, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logger, "LOG_READY", True)
    monkeypatch.setattr(session, "stop_sound", lambda: None)
    monkeypatch.setattr(
        session,
        "cli_witness_form",
        lambda *args, **kwargs: (response, time.time()),
    )
    goal = "User-approved goal"
    session.log_timer_start(1, goal)
    path = next(tmp_path.glob("witness_log_*.txt"))
    initial_text = path.read_text(encoding="utf-8")

    session.on_timer_end(
        Timer(60, volume=0),
        True,
        {"safe_word": "skip"},
        None,
        goal,
    )

    text = path.read_text(encoding="utf-8")
    assert text.startswith(initial_text)
    assert goal in text
    assert "Timer completed" in text
    assert bool("Completed the task" in text) is expect_answer
    assert re.search(r"\[\d{2}:\d{2}:\d{2}\]", text)


def test_help_documents_witness_opt_out(monkeypatch, capsys):
    import src.main as main

    monkeypatch.setattr(main, "render_help_screen", lambda *a, **k: None)

    with pytest.raises(SystemExit) as exit_info:
        main.show_help()

    assert exit_info.value.code == 0
    text = capsys.readouterr().out
    assert "-w, --witness" in text
    assert "--no-witness" in text
    assert "off by default" in text
