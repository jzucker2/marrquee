from ..utils import LogHelper


def test_log_helper_debug_env_flag_is_default_false():
    expected = False
    actual = LogHelper.get_debug_env_flag()
    assert actual == expected
    assert isinstance(actual, bool)
    assert actual == False
