from config import Settings


class KeypadInput:
    """What the user has typed on the keypad."""

    def __init__(self):
        self.value = ""

    def add(self, key: str, allow_decimal: bool = False) -> None:
        """Add a key (0-9 or '.') if the input rules allow it."""
        if len(self.value) >= Settings.MAX_INPUT_LENGTH:
            return
        if key == "." and (not allow_decimal or "." in self.value):
            return
        if self.has_cents():
            return
        self.value += key

    def clear(self) -> None:
        self.value = ""

    def is_empty(self) -> bool:
        return self.value == ""

    def masked(self) -> str:
        """Return the input hidden with '*', for PINs."""
        return "*" * len(self.value)

    def as_int(self) -> int:
        return int(self.value)

    def as_amount(self) -> float | None:
        """Return the input as money, or None if nothing was typed."""
        if self.value in ("", "."):
            return None
        return float(self.value)

    def has_cents(self) -> bool:
        """Return True if there are already 2 digits after the point."""
        if "." not in self.value:
            return False
        cents = self.value.split(".")[1]
        return len(cents) >= 2