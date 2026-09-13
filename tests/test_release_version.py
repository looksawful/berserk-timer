from pathlib import Path

from src.version import __version__


PUBLIC_VERSION = "0.3.0-beta"
PACKAGE_VERSION = "0.3.0b0"


def test_release_version_is_consistent_across_runtime_package_and_readme() -> None:
    root = Path(__file__).resolve().parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert __version__ == PUBLIC_VERSION
    assert f'version = "{PACKAGE_VERSION}"' in pyproject
    assert readme.startswith(f"# Berserk Timer {PUBLIC_VERSION}\n")
