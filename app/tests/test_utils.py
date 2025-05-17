import unittest
from ..utils import LogHelper


class TestUtils(unittest.TestCase):
    def test_foo(self):
        self.assertTrue(True)

    def test_log_helper_debug_env_flag_is_default_false(self):
        expected = False
        actual = LogHelper.get_debug_env_flag()
        self.assertEqual(actual, expected)
        self.assertIsInstance(actual, bool)
        self.assertFalse(actual)


if __name__ == '__main__':
    unittest.main()
