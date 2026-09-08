import src.main as main
import src.session as session


def test_cleanup_screen_exists_on_composition_root():
    assert hasattr(main, "cleanup_screen")


def test_session_owns_sound_shutdown_dependency():
    assert hasattr(session, "stop_sound")
    assert not hasattr(main, "stop_sound")
