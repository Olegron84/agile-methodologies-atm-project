from config import Settings


class PinLock:
    """Count wrong PINs per customer number and lock after too many."""

    def __init__(self, max_attempts: int = Settings.MAX_PIN_ATTEMPTS):
        self.max_attempts = max_attempts
        self.failed_attempts: dict[int, int] = {}
        self.locked_numbers: set[int] = set()

    def is_locked(self, number: int) -> bool:
        return number in self.locked_numbers

    def record_failure(self, number: int) -> int:
        """Count a wrong PIN and return the attempts left."""
        attempts = self.failed_attempts.get(number, 0) + 1
        self.failed_attempts[number] = attempts

        attempts_left = self.max_attempts - attempts
        if attempts_left <= 0:
            self.locked_numbers.add(number)
            return 0
        return attempts_left

    def reset(self, number: int) -> None:
        """Forget wrong PINs after a correct one."""
        self.failed_attempts[number] = 0