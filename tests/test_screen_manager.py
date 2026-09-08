import io

import src.screen_manager as screen_manager


def test_screen_manager_enters_and_exits_alternate_buffer(monkeypatch):
    stream = io.StringIO()
    monkeypatch.setattr(screen_manager.sys, "stdout", stream)
    manager = screen_manager.ScreenManager(use_alternate_buffer=True)

    manager.enter_alternate_screen()
    assert manager.is_in_alternate is True
    assert manager.ENTER_ALTERNATE_SCREEN in stream.getvalue()

    manager.exit_alternate_screen()
    assert manager.is_in_alternate is False
    assert manager.EXIT_ALTERNATE_SCREEN in stream.getvalue()


def test_get_screen_manager_reuses_singleton_until_cleanup(monkeypatch):
    monkeypatch.setattr(screen_manager, "_screen_manager", None)
    monkeypatch.setattr(
        screen_manager.ScreenManager, "exit_alternate_screen", lambda self: None
    )

    first = screen_manager.get_screen_manager(False, False)
    second = screen_manager.get_screen_manager(True, True)
    assert second is first

    screen_manager.cleanup_screen()
    third = screen_manager.get_screen_manager(False, False)
    assert third is not first

    screen_manager.cleanup_screen()
