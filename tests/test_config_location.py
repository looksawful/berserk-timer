from pathlib import Path

import src.config_manager as config_manager


def test_default_config_path_is_user_scoped_not_current_working_directory(monkeypatch, tmp_path):
    home = tmp_path / "home"
    cwd = tmp_path / "workspace"
    home.mkdir()
    cwd.mkdir()

    monkeypatch.setattr(config_manager.Path, "home", classmethod(lambda cls: home))
    monkeypatch.chdir(cwd)
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(config_manager.sys, "platform", "linux")

    path = config_manager.get_default_config_path()

    assert path == home / ".config" / "berserk-timer" / "config.json"
    assert path.parent != cwd


def test_load_config_creates_parent_directory_for_default_location(monkeypatch, tmp_path):
    target = tmp_path / "nested" / "berserk-timer" / "config.json"
    monkeypatch.setattr(config_manager, "get_default_config_path", lambda: target)

    config = config_manager.load_config()

    assert target.exists()
    assert config["volume"] == config_manager.DEFAULT_CONFIG["volume"]
