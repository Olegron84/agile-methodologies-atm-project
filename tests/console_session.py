from atm_controller import ATMController
from atm_types import Shortcut


def show(atm: ATMController, action: str) -> None:
    buttons = [f"{key} = {label}" for key, label in atm.get_shortcut_labels().items() if label]
    print(f"> {action}")
    print(atm.get_display_text())
    print(f"  Buttons: {', '.join(buttons)}")
    print()


def type_keys(atm: ATMController, keys: str) -> None:
    for key in keys:
        atm.handle_digit(key)


def main() -> None:
    atm = ATMController()
    show(atm, "Start")

    atm.handle_enter()
    type_keys(atm, "1001")
    show(atm, "Type customer number 1001")

    atm.handle_enter()
    type_keys(atm, "1234")
    show(atm, "Type PIN")

    atm.handle_enter()
    show(atm, "Enter -> logged in")

    atm.handle_shortcut(Shortcut.A)
    show(atm, "A = Current account (balance)")

    atm.handle_shortcut(Shortcut.B)
    type_keys(atm, "50")
    atm.handle_enter()
    show(atm, "Deposit 50")

    atm.handle_shortcut(Shortcut.A)
    type_keys(atm, "120.50")
    atm.handle_enter()
    show(atm, "Withdraw 120.50")

    atm.handle_shortcut(Shortcut.C)
    show(atm, "C = Back to account selection")

    atm.handle_shortcut(Shortcut.C)
    show(atm, "C = Exit")


if __name__ == "__main__":
    main()