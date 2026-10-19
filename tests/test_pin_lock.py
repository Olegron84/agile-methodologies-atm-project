import unittest

from pin_lock import PinLock


class TestPinLock(unittest.TestCase):
    def setUp(self):
        self.lock = PinLock(max_attempts=3)

    def test_not_locked_at_first(self):
        self.assertFalse(self.lock.is_locked(1001))

    def test_attempts_count_down(self):
        self.assertEqual(self.lock.record_failure(1001), 2)
        self.assertEqual(self.lock.record_failure(1001), 1)
        self.assertFalse(self.lock.is_locked(1001))

    def test_locked_after_max_attempts(self):
        for _ in range(3):
            attempts_left = self.lock.record_failure(1001)
        self.assertEqual(attempts_left, 0)
        self.assertTrue(self.lock.is_locked(1001))

    def test_reset_restores_attempts(self):
        self.lock.record_failure(1001)
        self.lock.record_failure(1001)
        self.lock.reset(1001)
        self.assertEqual(self.lock.record_failure(1001), 2)

    def test_numbers_are_tracked_separately(self):
        for _ in range(3):
            self.lock.record_failure(1001)
        self.assertTrue(self.lock.is_locked(1001))
        self.assertFalse(self.lock.is_locked(1002))
        self.assertEqual(self.lock.record_failure(1002), 2)


if __name__ == "__main__":
    unittest.main()