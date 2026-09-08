from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_windows_launcher_forwards_arguments_without_injected_modes() -> None:
    launcher = (ROOT / "brsrk.bat").read_text(encoding="utf-8")

    assert "C:\\Program Files\\Python312\\python.exe" not in launcher
    assert "-m src.main -w %*" not in launcher
    assert "-m src.main %*" in launcher


def test_posix_launcher_forwards_arguments_without_injected_duration_or_mode() -> None:
    launcher = (ROOT / "brsrk.sh").read_text(encoding="utf-8")

    assert '-m src.main 5 -w "$@"' not in launcher
    assert '-m src.main "$@"' in launcher


def test_readme_references_existing_windows_launcher() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "brsrk-cli.bat" not in readme
    assert "brsrk.bat" in readme
