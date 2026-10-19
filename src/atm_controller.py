from atm_model import Account, Bank
from atm_types import SHORTCUT_LABELS, Session, Shortcut, State, Transaction
from keypad_input import KeypadInput
from pin_lock import PinLock

TYPING_STATES = (State.ENTER_NUMBER, State.ENTER_PIN, State.ENTER_AMOUNT)


def format_money(amount: float) -> str:
    return f"€{amount:.2f}"


class ATMController:
    """Run ATM sessions: Start -> Enter customer number -> Enter PIN ->
    Select account -> Transaction -> back to Select account, or Exit.
    """

    def __init__(self, bank: Bank | None = None):
        if bank is None:
            bank = Bank()
        self.bank = bank
        # Lives outside the session so a lock survives logout
        self.pin_lock = PinLock()

        self.state = State.START
        self.keypad = KeypadInput()
        self.message = ""
        self.session = Session()

    def reset(self, message: str = "") -> None:
        """End the session and return to the Start screen."""
        self.session = Session()
        self.go_to(State.START, message)

    def go_to(self, state: State, message: str = "") -> None:
        """Move to a state with empty input."""
        self.state = state
        self.keypad.clear()
        self.message = message

    def handle_digit(self, digit: str) -> None:
        """Add a keypad key (0-9 or '.') to the input."""
        # Typing on the Start screen begins customer number entry
        if self.state == State.START:
            self.go_to(State.ENTER_NUMBER)

        if self.state not in TYPING_STATES:
            return
        self.keypad.add(digit, allow_decimal=self.state == State.ENTER_AMOUNT)
        self.message = ""

    def handle_clear(self) -> None:
        """Clear the input and the message."""
        self.keypad.clear()
        self.message = ""

    def handle_enter(self) -> None:
        """Confirm the input."""
        if self.state == State.START:
            self.go_to(State.ENTER_NUMBER)
        elif self.state == State.ENTER_NUMBER:
            self.check_customer_number()
        elif self.state == State.ENTER_PIN:
            self.check_pin()
        elif self.state == State.ENTER_AMOUNT:
            self.do_transaction()

    def handle_shortcut(self, key: Shortcut) -> None:
        """Handle a side button press."""
        if self.state == State.ENTER_PIN:
            if key == Shortcut.C:
                self.reset("Cancelled.")

        elif self.state == State.SELECT_ACCOUNT:
            if key == Shortcut.A:
                self.choose_account(self.session.customer.current_account, "Current")
            elif key == Shortcut.B:
                self.choose_account(self.session.customer.savings_account, "Savings")
            elif key == Shortcut.C:
                self.reset("Thank you. Goodbye!")

        elif self.state == State.TRANSACTION:
            if key == Shortcut.A:
                self.session.transaction = Transaction.WITHDRAW
                self.go_to(State.ENTER_AMOUNT)
            elif key == Shortcut.B:
                self.session.transaction = Transaction.DEPOSIT
                self.go_to(State.ENTER_AMOUNT)
            elif key == Shortcut.C:
                self.session.account = None
                self.session.account_name = ""
                self.go_to(State.SELECT_ACCOUNT)

        elif self.state == State.ENTER_AMOUNT:
            if key == Shortcut.C:
                self.go_to(State.TRANSACTION, "Cancelled.")

    def get_display_text(self) -> str:
        """Return the text for the ATM screen."""
        if self.state == State.START:
            lines = ["Welcome to the ATM", "Press Enter to begin"]
        elif self.state == State.ENTER_NUMBER:
            lines = ["Enter customer number", self.keypad.value]
        elif self.state == State.ENTER_PIN:
            lines = ["Enter PIN", self.keypad.masked()]
        elif self.state == State.SELECT_ACCOUNT:
            lines = ["Select account"]
        elif self.state == State.TRANSACTION:
            balance = format_money(self.session.account.get_balance())
            lines = [f"{self.session.account_name} account", f"Balance: {balance}"]
        else:
            lines = [f"{self.session.transaction} - {self.session.account_name} account",
                     f"Enter amount: €{self.keypad.value}"]

        if self.message:
            lines.append(self.message)
        return "\n".join(lines)

    def get_shortcut_labels(self) -> dict[Shortcut, str]:
        """Return the label of each side button."""
        return dict(SHORTCUT_LABELS[self.state])

    def check_customer_number(self) -> None:
        if self.keypad.is_empty():
            self.message = "Please enter your customer number."
            return

        number = self.keypad.as_int()
        known_numbers = [customer.number for customer in self.bank.customers]

        if self.pin_lock.is_locked(number):
            self.go_to(State.ENTER_NUMBER, "Card locked. Please contact your bank.")
        elif number not in known_numbers:
            self.go_to(State.ENTER_NUMBER, "Unknown customer number.")
        else:
            self.session.customer_number = number
            self.go_to(State.ENTER_PIN)

    def check_pin(self) -> None:
        if self.keypad.is_empty():
            self.message = "Please enter your PIN."
            return

        number = self.session.customer_number
        customer = self.bank.find_customer(number, self.keypad.as_int())
        if customer is not None:
            self.pin_lock.reset(number)
            self.session.customer = customer
            self.go_to(State.SELECT_ACCOUNT)
            return

        attempts_left = self.pin_lock.record_failure(number)
        if attempts_left == 0:
            self.reset("Too many wrong PINs. Card locked.")
        else:
            self.go_to(State.ENTER_PIN, f"Wrong PIN. Attempts left: {attempts_left}")

    def choose_account(self, account: Account, name: str) -> None:
        self.session.account = account
        self.session.account_name = name
        self.go_to(State.TRANSACTION)

    def do_transaction(self) -> None:
        amount = self.keypad.as_amount()
        if amount is None:
            self.message = "Please enter an amount."
            return

        account = self.session.account
        try:
            if self.session.transaction == Transaction.WITHDRAW:
                account.withdraw(amount)
                done = f"Withdrew {format_money(amount)}."
            else:
                account.deposit(amount)
                done = f"Deposited {format_money(amount)}."
        except ValueError as error:
            # Account validates the amount; show its reason to the user
            self.go_to(State.ENTER_AMOUNT, str(error))
            return

        self.go_to(State.TRANSACTION, done)