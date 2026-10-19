from dataclasses import dataclass
from enum import StrEnum

from atm_model import Account, Customer


class State(StrEnum):
    START = "Start"
    ENTER_NUMBER = "Enter customer number"
    ENTER_PIN = "Enter PIN"
    SELECT_ACCOUNT = "Select account"
    TRANSACTION = "Transaction"
    ENTER_AMOUNT = "Enter amount"


class Transaction(StrEnum):
    WITHDRAW = "Withdraw"
    DEPOSIT = "Deposit"


class Shortcut(StrEnum):
    """Side buttons next to the ATM screen."""

    A = "A"
    B = "B"
    C = "C"


# "" means the button is not used in that state
SHORTCUT_LABELS = {
    State.START: {Shortcut.A: "", Shortcut.B: "", Shortcut.C: ""},
    State.ENTER_NUMBER: {Shortcut.A: "", Shortcut.B: "", Shortcut.C: ""},
    State.ENTER_PIN: {Shortcut.A: "", Shortcut.B: "", Shortcut.C: "Cancel"},
    State.SELECT_ACCOUNT: {Shortcut.A: "Current", Shortcut.B: "Savings", Shortcut.C: "Exit"},
    State.TRANSACTION: {Shortcut.A: "Withdraw", Shortcut.B: "Deposit", Shortcut.C: "Back"},
    State.ENTER_AMOUNT: {Shortcut.A: "", Shortcut.B: "", Shortcut.C: "Cancel"},
}


@dataclass
class Session:
    """Data of one customer visit, from login until exit."""

    customer_number: int | None = None
    customer: Customer | None = None
    account: Account | None = None
    account_name: str = ""
    transaction: Transaction | None = None