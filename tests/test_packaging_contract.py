from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_project_defines_installable_console_entrypoint() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "[project]" in pyproject
    assert 'name = "berserk-timer"' in pyproject
    assert '[project.scripts]' in pyproject
    assert 'berserk = "src.main:main"' in pyproject


def test_runtime_requirements_do_not_include_test_tools() -> None:
    runtime = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    dev = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")

    assert "pytest" not in runtime
    assert "pytest" in dev


def test_setup_py_is_not_a_shell_activation_bootstrap() -> None:
    setup_py = ROOT / "setup.py"
    if setup_py.exists():
        source = setup_py.read_text(encoding="utf-8")
        assert "activate_venv" not in source
        assert "subprocess.call([activate_script])" not in source
