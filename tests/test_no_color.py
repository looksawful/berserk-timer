import importlib
import os


def test_no_color_environment():
    os.environ["NO_COLOR"] = "1"
    if "src.cli" in list(importlib.sys.modules):
        importlib.reload(importlib.import_module("src.cli"))
    import src.cli as cli
    assert cli.console.no_color is True
