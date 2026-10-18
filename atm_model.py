class Account:
    """Bank account with balance, deposit and withdrawal."""

    def __init__(self, balance=0.0):
        if balance < 0:
            raise ValueError("Initial balance cannot be negative.")
        self._balance = float(balance)

    def get_balance(self):
        """Return the current balance (read-only access)."""
        return self._balance

    def check_amount(self, amount):
        """Raise an error if the amount is not a positive number."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

    def deposit(self, amount):
        self.check_amount(amount)
        self._balance += amount

    def withdraw(self, amount):
        self.check_amount(amount)
        if amount > self._balance:
            raise ValueError("Insufficient funds.")
        self._balance -= amount


class Customer:
    """Bank customer: number, PIN, current and savings accounts."""

    def __init__(self, number, pin, current_balance=0.0, savings_balance=0.0):
        self.number = number
        self.pin = pin
        self.current_account = Account(current_balance)
        self.savings_account = Account(savings_balance)


class Bank:
    """Stores customers, generates customer numbers, finds customers."""

    def __init__(self):
        self.customers = []
        self.next_number = 1001
        # test customers
        self.add_customer(1234, 500.0, 1500.0)
        self.add_customer(4321, 250.0, 3000.0)
        self.add_customer(1111, 0.0, 100.0)
        self.add_customer(9999, 1200.0, 8000.0)

    def add_customer(self, pin, current_balance=0.0, savings_balance=0.0):
        """Create a customer with the next free number and return it."""
        customer = Customer(self.next_number, pin, current_balance, savings_balance)
        self.next_number += 1
        self.customers.append(customer)
        return customer

    def findCustomer(self, number, pin):
        """Return the Customer if number and PIN match, otherwise None."""
        for customer in self.customers:
            if customer.number == number and customer.pin == pin:
                return customer
        return None