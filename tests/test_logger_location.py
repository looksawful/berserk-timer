from pathlib import Path

import src.logger as logger


def test_default_log_dir_is_user_scoped_on_linux(monkeypatch, tmp_path):
    state_home = tmp_path / "state-home"
    cwd = tmp_path / "workspace"
    state_home.mkdir()
    cwd.mkdir()

    monkeypatch.chdir(cwd)
    monkeypatch.setenv("XDG_STATE_HOME", str(state_home))
    monkeypatch.setattr(logger.sys, "platform", "linux")

    path = logger.get_default_log_dir()

    assert path == state_home / "berserk-timer" / "logs"
    assert cwd not in path.parents


def test_default_log_dir_is_user_scoped_on_windows(monkeypatch, tmp_path):
    local_app_data = tmp_path / "LocalAppData"
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))
    monkeypatch.setattr(logger.sys, "platform", "win32")

    path = logger.get_default_log_dir()

    assert path == local_app_data / "Berserk Timer" / "logs"


def test_log_dir_can_be_overridden_for_tests_and_embedders(monkeypatch, tmp_path):
    target = tmp_path / "custom-logs"

    monkeypatch.setenv("BERSERK_LOG_DIR", str(target))

    assert logger.get_default_log_dir() == Path(target)
