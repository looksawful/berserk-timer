import json

import src.config_manager as config_manager


def test_default_config_path_is_user_scoped_not_current_working_directory(monkeypatch, tmp_path):
    config_home = tmp_path / "config-home"
    cwd = tmp_path / "workspace"
    config_home.mkdir()
    cwd.mkdir()

    monkeypatch.chdir(cwd)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(config_manager.sys, "platform", "linux")

    path = config_manager.get_default_config_path()

    assert path == config_home / "berserk-timer" / "config.json"
    assert cwd not in path.parents


def test_load_config_creates_parent_directory_for_default_location(monkeypatch, tmp_path):
    target = tmp_path / "nested" / "berserk-timer" / "config.json"
    monkeypatch.setattr(config_manager, "get_default_config_path", lambda: target)
    monkeypatch.setattr(
        config_manager, "get_legacy_source_config_path", lambda: tmp_path / "missing.json"
    )

    config = config_manager.load_config()

    assert target.exists()
    assert config["volume"] == config_manager.DEFAULT_CONFIG["volume"]


def test_first_run_migrates_legacy_source_config(monkeypatch, tmp_path):
    target = tmp_path / "user" / "config.json"
    legacy = tmp_path / "repo" / "config.json"
    legacy.parent.mkdir()
    legacy.write_text(json.dumps({"safe_word": "q", "volume": 8}), encoding="utf-8")

    monkeypatch.setattr(config_manager, "get_default_config_path", lambda: target)
    monkeypatch.setattr(config_manager, "get_legacy_source_config_path", lambda: legacy)

    config = config_manager.load_config()

    assert target.exists()
    assert config["safe_word"] == "q"
    assert config["volume"] == 8


def test_repository_config_is_canonical_default_config():
    source_config = config_manager.get_legacy_source_config_path()

    loaded = json.loads(source_config.read_text(encoding="utf-8"))

    assert loaded == config_manager.DEFAULT_CONFIG
