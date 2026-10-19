import unittest

from atm_model import Account, Bank


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.acc = Account(100)

    def test_initial_balance(self):
        self.assertEqual(Account().get_balance(), 0)
        self.assertEqual(self.acc.get_balance(), 100)

    def test_negative_initial_balance(self):
        with self.assertRaises(ValueError):
            Account(-1)

    def test_deposit(self):
        self.acc.deposit(50)
        self.assertEqual(self.acc.get_balance(), 150)

    def test_deposit_zero_rejected(self):
        with self.assertRaises(ValueError):
            self.acc.deposit(0)
        self.assertEqual(self.acc.get_balance(), 100)

    def test_deposit_negative_rejected(self):
        with self.assertRaises(ValueError):
            self.acc.deposit(-10)
        self.assertEqual(self.acc.get_balance(), 100)

    def test_deposit_non_number_rejected(self):
        with self.assertRaises(TypeError):
            self.acc.deposit("abc")

    def test_withdraw(self):
        self.acc.withdraw(40)
        self.assertEqual(self.acc.get_balance(), 60)

    def test_withdraw_entire_balance(self):
        self.acc.withdraw(100)
        self.assertEqual(self.acc.get_balance(), 0)

    def test_withdraw_more_than_balance_rejected(self):
        with self.assertRaises(ValueError):
            self.acc.withdraw(100.01)
        self.assertEqual(self.acc.get_balance(), 100)

    def test_withdraw_zero_and_negative_rejected(self):
        for amount in (0, -5):
            with self.assertRaises(ValueError):
                self.acc.withdraw(amount)
        self.assertEqual(self.acc.get_balance(), 100)

    def test_balance_after_several_operations(self):
        self.acc.deposit(100)
        self.acc.withdraw(30)
        self.acc.deposit(5)
        self.assertEqual(self.acc.get_balance(), 175)


class TestBank(unittest.TestCase):
    def setUp(self):
        self.bank = Bank()

    def test_find_customer_ok(self):
        c = self.bank.find_customer(1001, 1234)
        self.assertIsNotNone(c)
        self.assertEqual(c.number, 1001)

    def test_wrong_pin(self):
        self.assertIsNone(self.bank.find_customer(1001, 0))

    def test_unknown_number(self):
        self.assertIsNone(self.bank.find_customer(5555, 1234))

    def test_customer_has_two_accounts(self):
        c = self.bank.find_customer(1002, 4321)
        self.assertEqual(c.current_account.get_balance(), 250)
        self.assertEqual(c.savings_account.get_balance(), 3000)

    def test_numbers_are_generated_in_order(self):
        numbers = [c.number for c in self.bank.customers]
        self.assertEqual(numbers, [1001, 1002, 1003, 1004])

    def test_add_customer_gets_next_number(self):
        c = self.bank.add_customer(5555, 10, 20)
        self.assertEqual(c.number, 1005)
        self.assertIs(self.bank.find_customer(1005, 5555), c)

    def test_generated_numbers_are_unique(self):
        a = self.bank.add_customer(1)
        b = self.bank.add_customer(2)
        self.assertNotEqual(a.number, b.number)


if __name__ == "__main__":
    unittest.main()