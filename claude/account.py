# account.py
# Account classes — covers full OOP syllabus

import uuid
from datetime import datetime
from utils import (log_transaction, validate_input,
                   format_currency, get_timestamp,
                   write_to_log)
from database import (get_account, update_balance,
                       insert_transaction, get_transactions)

# ── BASE CLASS — Abstraction and Encapsulation ──
class Account:
    """
    Base Account class
    Covers: Class, Object, Abstraction, Encapsulation
    """

    # Class variable — shared across all accounts
    total_accounts_created = 0
    MINIMUM_BALANCE        = 1000

    def __init__(self, account_number, customer_id, account_type):
        # Private attributes — Encapsulation
        self.__account_number = account_number
        self.__customer_id    = customer_id
        self.__account_type   = account_type
        self.__balance        = 0.0
        self.__created_at     = get_timestamp()
        self.__is_active      = True

        Account.total_accounts_created += 1

    # ── Properties — Encapsulation ──
    @property
    def account_number(self):
        return self.__account_number

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, amount):
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        self.__balance = amount

    @property
    def account_type(self):
        return self.__account_type

    @property
    def is_active(self):
        return self.__is_active

    # ── Abstract methods — Abstraction ──
    def get_interest_rate(self):
        """Override in subclass"""
        raise NotImplementedError("Subclass must implement this")

    def calculate_interest(self):
        """Override in subclass"""
        raise NotImplementedError("Subclass must implement this")

    # ── Common methods ──
    @log_transaction
    @validate_input
    def deposit(self, amount):
        """Deposit money into account"""
        amount = float(amount)

        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        old_balance    = self.__balance
        self.__balance += amount

        # Update database
        update_balance(self.__account_number, self.__balance)

        # Record transaction
        trans_id = str(uuid.uuid4())[:8].upper()
        insert_transaction({
            'transaction_id':   trans_id,
            'account_number':   self.__account_number,
            'transaction_type': 'DEPOSIT',
            'amount':           amount,
            'balance_after':    self.__balance,
            'description':      f'Deposit of {format_currency(amount)}'
        })

        # Write to log file
        write_to_log(
            f"DEPOSIT | Acc: {self.__account_number} | "
            f"Amount: {format_currency(amount)} | "
            f"Balance: {format_currency(self.__balance)}"
        )

        print(f"✅ Deposit successful!")
        print(f"   Amount:      {format_currency(amount)}")
        print(f"   New Balance: {format_currency(self.__balance)}")

        return {
            'success':     True,
            'amount':      amount,
            'old_balance': old_balance,
            'new_balance': self.__balance
        }

    @log_transaction
    def withdraw(self, amount):
        """Withdraw money from account"""
        amount = float(amount)

        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self.__balance - self.MINIMUM_BALANCE:
            raise ValueError(
                f"Insufficient funds. "
                f"Minimum balance of {format_currency(self.MINIMUM_BALANCE)} required."
            )

        old_balance    = self.__balance
        self.__balance -= amount

        # Update database
        update_balance(self.__account_number, self.__balance)

        # Record transaction
        trans_id = str(uuid.uuid4())[:8].upper()
        insert_transaction({
            'transaction_id':   trans_id,
            'account_number':   self.__account_number,
            'transaction_type': 'WITHDRAWAL',
            'amount':           amount,
            'balance_after':    self.__balance,
            'description':      f'Withdrawal of {format_currency(amount)}'
        })

        write_to_log(
            f"WITHDRAWAL | Acc: {self.__account_number} | "
            f"Amount: {format_currency(amount)} | "
            f"Balance: {format_currency(self.__balance)}"
        )

        print(f"✅ Withdrawal successful!")
        print(f"   Amount:      {format_currency(amount)}")
        print(f"   New Balance: {format_currency(self.__balance)}")

        return {
            'success':     True,
            'amount':      amount,
            'old_balance': old_balance,
            'new_balance': self.__balance
        }

    def get_transaction_history(self, limit=10):
        """Get recent transactions"""
        return get_transactions(self.__account_number, limit)

    def get_balance(self):
        """Get current balance"""
        return self.__balance

    def __str__(self):
        """String representation — String methods"""
        return (
            f"Account: {self.__account_number} | "
            f"Type: {self.__account_type} | "
            f"Balance: {format_currency(self.__balance)}"
        )

    def __repr__(self):
        return f"Account('{self.__account_number}', '{self.__account_type}')"


# ── INHERITANCE — SavingsAccount ──
class SavingsAccount(Account):
    """
    Savings Account
    Covers: Inheritance, Polymorphism
    """

    INTEREST_RATE    = 4.5
    MINIMUM_BALANCE  = 1000
    MAX_WITHDRAWALS  = 6  # per month

    def __init__(self, account_number, customer_id):
        # Call parent constructor
        super().__init__(account_number, customer_id, 'SAVINGS')
        self.__monthly_withdrawals = 0

    def get_interest_rate(self):
        """POLYMORPHISM — overrides base class method"""
        return self.INTEREST_RATE

    def calculate_interest(self):
        """Calculate monthly interest"""
        monthly_rate = self.INTEREST_RATE / 12 / 100
        interest     = self.balance * monthly_rate
        return round(interest, 2)

    def add_interest(self):
        """Add monthly interest to balance"""
        interest = self.calculate_interest()
        if interest > 0:
            self.deposit(interest)
            print(f"Interest added: {format_currency(interest)}")
        return interest

    def withdraw(self, amount):
        """Override withdraw — add withdrawal limit check"""
        if self.__monthly_withdrawals >= self.MAX_WITHDRAWALS:
            raise ValueError(
                f"Monthly withdrawal limit of {self.MAX_WITHDRAWALS} reached."
            )

        result = super().withdraw(amount)
        self.__monthly_withdrawals += 1
        return result

    def reset_monthly_withdrawals(self):
        """Reset counter at start of new month"""
        self.__monthly_withdrawals = 0


# ── INHERITANCE — CurrentAccount ──
class CurrentAccount(Account):
    """
    Current Account for businesses
    Covers: Inheritance, Polymorphism
    """

    INTEREST_RATE    = 0.0
    MINIMUM_BALANCE  = 5000
    OVERDRAFT_LIMIT  = 10000

    def __init__(self, account_number, customer_id):
        super().__init__(account_number, customer_id, 'CURRENT')
        self.__overdraft_used = 0

    def get_interest_rate(self):
        """POLYMORPHISM — overrides base class method"""
        return self.INTEREST_RATE

    def calculate_interest(self):
        """No interest on current account"""
        return 0

    def withdraw(self, amount):
        """Override withdraw — allows overdraft"""
        amount = float(amount)

        available = self.balance + self.OVERDRAFT_LIMIT
        if amount > available:
            raise ValueError(
                f"Exceeds overdraft limit. "
                f"Available: {format_currency(available)}"
            )

        return super().withdraw(amount)


# ── POLYMORPHISM DEMONSTRATION ──
def process_interest_for_all(accounts):
    """
    Polymorphism in action
    Same method call, different behavior
    based on account type
    """
    results = {}

    for account in accounts:
        # Same method call for all account types
        # But each behaves differently
        interest          = account.calculate_interest()
        results[account.account_number] = {
            'type':     account.account_type,
            'interest': interest
        }
        print(
            f"{account.account_type}: "
            f"Interest = {format_currency(interest)}"
        )

    return results

print("Account classes loaded!")