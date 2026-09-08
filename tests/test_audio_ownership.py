import subprocess

import src.logger as logger


def test_stop_sound_never_uses_system_wide_killall(monkeypatch):
    calls = []

    def fake_run(command, *args, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(logger.subprocess, "run", fake_run)
    monkeypatch.setattr(logger.sys, "platform", "linux")

    logger.stop_sound()

    assert not any(command and command[0] == "killall" for command in calls)
