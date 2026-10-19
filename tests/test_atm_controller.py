import unittest

from atm_controller import ATMController
from atm_types import Shortcut, State


def type_keys(atm, keys):
    for key in keys:
        atm.handle_digit(key)


def enter(atm, keys):
    type_keys(atm, keys)
    atm.handle_enter()


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.atm = ATMController()
        self.atm.handle_enter()

    def test_starts_on_start_screen(self):
        atm = ATMController()
        self.assertEqual(atm.state, State.START)
        self.assertIn("Welcome", atm.get_display_text())

    def test_correct_login(self):
        enter(self.atm, "1001")
        self.assertEqual(self.atm.state, State.ENTER_PIN)
        enter(self.atm, "1234")
        self.assertEqual(self.atm.state, State.SELECT_ACCOUNT)
        self.assertEqual(self.atm.session.customer.number, 1001)

    def test_unknown_number(self):
        enter(self.atm, "5555")
        self.assertEqual(self.atm.state, State.ENTER_NUMBER)
        self.assertIn("Unknown customer number", self.atm.get_display_text())

    def test_pin_is_hidden(self):
        enter(self.atm, "1001")
        type_keys(self.atm, "1234")
        self.assertIn("****", self.atm.get_display_text())
        self.assertNotIn("1234", self.atm.get_display_text())

    def test_wrong_pin_shows_error(self):
        enter(self.atm, "1001")
        enter(self.atm, "0000")
        self.assertEqual(self.atm.state, State.ENTER_PIN)
        self.assertIn("Wrong PIN. Attempts left: 2", self.atm.get_display_text())

    def test_locked_after_three_wrong_pins(self):
        enter(self.atm, "1001")
        enter(self.atm, "0000")
        enter(self.atm, "0000")
        enter(self.atm, "0000")
        self.assertEqual(self.atm.state, State.START)
        self.assertIn("Card locked", self.atm.get_display_text())

        # The correct PIN no longer helps
        self.atm.handle_enter()
        enter(self.atm, "1001")
        self.assertEqual(self.atm.state, State.ENTER_NUMBER)
        self.assertIn("Card locked", self.atm.get_display_text())

    def test_correct_pin_resets_failed_attempts(self):
        enter(self.atm, "1001")
        enter(self.atm, "0000")
        enter(self.atm, "0000")
        enter(self.atm, "1234")
        self.atm.handle_shortcut(Shortcut.C)

        self.atm.handle_enter()
        enter(self.atm, "1001")
        enter(self.atm, "0000")
        self.assertEqual(self.atm.state, State.ENTER_PIN)

    def test_cancel_on_pin_screen(self):
        enter(self.atm, "1001")
        self.atm.handle_shortcut(Shortcut.C)
        self.assertEqual(self.atm.state, State.START)

    def test_clear(self):
        type_keys(self.atm, "123")
        self.atm.handle_clear()
        self.assertTrue(self.atm.keypad.is_empty())


class TestTransactions(unittest.TestCase):
    def setUp(self):
        self.atm = ATMController()
        self.atm.handle_enter()
        enter(self.atm, "1001")
        enter(self.atm, "1234")
        self.atm.handle_shortcut(Shortcut.A)

    def test_shows_balance(self):
        self.assertEqual(self.atm.state, State.TRANSACTION)
        self.assertIn("Balance: €500.00", self.atm.get_display_text())

    def test_deposit(self):
        self.atm.handle_shortcut(Shortcut.B)
        enter(self.atm, "50")
        self.assertEqual(self.atm.state, State.TRANSACTION)
        self.assertEqual(self.atm.session.account.get_balance(), 550)
        self.assertIn("Deposited €50.00", self.atm.get_display_text())

    def test_withdraw_with_cents(self):
        self.atm.handle_shortcut(Shortcut.A)
        enter(self.atm, "120.50")
        self.assertEqual(self.atm.session.account.get_balance(), 379.50)

    def test_overdraw_rejected(self):
        self.atm.handle_shortcut(Shortcut.A)
        enter(self.atm, "600")
        self.assertEqual(self.atm.state, State.ENTER_AMOUNT)
        self.assertEqual(self.atm.session.account.get_balance(), 500)
        self.assertIn("Insufficient funds", self.atm.get_display_text())

    def test_zero_amount_rejected(self):
        self.atm.handle_shortcut(Shortcut.B)
        enter(self.atm, "0")
        self.assertEqual(self.atm.session.account.get_balance(), 500)
        self.assertIn("greater than zero", self.atm.get_display_text())

    def test_empty_amount_rejected(self):
        self.atm.handle_shortcut(Shortcut.B)
        self.atm.handle_enter()
        self.assertEqual(self.atm.state, State.ENTER_AMOUNT)
        self.assertIn("Please enter an amount", self.atm.get_display_text())

    def test_amount_input_rules(self):
        self.atm.handle_shortcut(Shortcut.B)
        type_keys(self.atm, "1.2.345")
        self.assertEqual(self.atm.keypad.value, "1.23")

    def test_no_decimal_point_in_customer_number(self):
        atm = ATMController()
        type_keys(atm, "10.01")
        self.assertEqual(atm.keypad.value, "1001")

    def test_cancel_amount(self):
        self.atm.handle_shortcut(Shortcut.A)
        self.atm.handle_shortcut(Shortcut.C)
        self.assertEqual(self.atm.state, State.TRANSACTION)

    def test_switch_account(self):
        self.atm.handle_shortcut(Shortcut.C)
        self.assertEqual(self.atm.state, State.SELECT_ACCOUNT)
        self.atm.handle_shortcut(Shortcut.B)
        self.assertIn("Savings account", self.atm.get_display_text())
        self.assertIn("Balance: €1500.00", self.atm.get_display_text())

    def test_exit_resets_session(self):
        self.atm.handle_shortcut(Shortcut.C)
        self.atm.handle_shortcut(Shortcut.C)
        self.assertEqual(self.atm.state, State.START)
        self.assertIsNone(self.atm.session.customer)
        self.assertIsNone(self.atm.session.account)
        self.assertIn("Goodbye", self.atm.get_display_text())


class TestShortcutLabels(unittest.TestCase):
    def test_labels_change_with_state(self):
        atm = ATMController()
        atm.handle_enter()
        enter(atm, "1001")
        enter(atm, "1234")
        self.assertEqual(atm.get_shortcut_labels(),
                         {Shortcut.A: "Current", Shortcut.B: "Savings", Shortcut.C: "Exit"})
        atm.handle_shortcut(Shortcut.A)
        self.assertEqual(atm.get_shortcut_labels(),
                         {Shortcut.A: "Withdraw", Shortcut.B: "Deposit", Shortcut.C: "Back"})


class TestFullSession(unittest.TestCase):
    def test_login_balance_deposit_withdraw_exit(self):
        atm = ATMController()
        atm.handle_enter()
        enter(atm, "1002")
        enter(atm, "4321")
        atm.handle_shortcut(Shortcut.A)
        self.assertIn("Balance: €250.00", atm.get_display_text())

        atm.handle_shortcut(Shortcut.B)
        enter(atm, "100")
        self.assertIn("Balance: €350.00", atm.get_display_text())

        atm.handle_shortcut(Shortcut.A)
        enter(atm, "50")
        self.assertIn("Balance: €300.00", atm.get_display_text())

        atm.handle_shortcut(Shortcut.C)
        atm.handle_shortcut(Shortcut.C)
        self.assertEqual(atm.state, State.START)


if __name__ == "__main__":
    unittest.main()