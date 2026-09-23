import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIMER_MODULE = ROOT / "src" / "timer.py"


def test_timer_domain_does_not_import_persistence_or_logging_adapters():
    tree = ast.parse(TIMER_MODULE.read_text(encoding="utf-8"))

    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert "logging" not in imported_modules
    assert "logging" not in imported_names
    assert "logger" not in imported_modules
    assert "src.logger" not in imported_modules
    assert "src.logger" not in imported_names
