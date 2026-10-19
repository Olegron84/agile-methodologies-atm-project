import unittest

from config import Settings
from keypad_input import KeypadInput


def type_keys(keypad, keys, allow_decimal=False):
    for key in keys:
        keypad.add(key, allow_decimal)


class TestKeypadInput(unittest.TestCase):
    def setUp(self):
        self.keypad = KeypadInput()

    def test_starts_empty(self):
        self.assertTrue(self.keypad.is_empty())

    def test_digits_are_added(self):
        type_keys(self.keypad, "123")
        self.assertEqual(self.keypad.value, "123")

    def test_max_length(self):
        type_keys(self.keypad, "1" * (Settings.MAX_INPUT_LENGTH + 3))
        self.assertEqual(len(self.keypad.value), Settings.MAX_INPUT_LENGTH)

    def test_decimal_point_rejected_when_not_allowed(self):
        type_keys(self.keypad, "1.5")
        self.assertEqual(self.keypad.value, "15")

    def test_only_one_decimal_point(self):
        type_keys(self.keypad, "1..5.", allow_decimal=True)
        self.assertEqual(self.keypad.value, "1.5")

    def test_max_two_decimals(self):
        type_keys(self.keypad, "9.999", allow_decimal=True)
        self.assertEqual(self.keypad.value, "9.99")

    def test_clear(self):
        type_keys(self.keypad, "42")
        self.keypad.clear()
        self.assertTrue(self.keypad.is_empty())

    def test_masked(self):
        type_keys(self.keypad, "1234")
        self.assertEqual(self.keypad.masked(), "****")

    def test_as_int(self):
        type_keys(self.keypad, "1001")
        self.assertEqual(self.keypad.as_int(), 1001)

    def test_as_amount_empty(self):
        self.assertIsNone(self.keypad.as_amount())
        type_keys(self.keypad, ".", allow_decimal=True)
        self.assertIsNone(self.keypad.as_amount())

    def test_as_amount_with_cents(self):
        type_keys(self.keypad, "12.5", allow_decimal=True)
        self.assertEqual(self.keypad.as_amount(), 12.5)


if __name__ == "__main__":
    unittest.main()