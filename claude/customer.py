# customer.py
# Customer class — covers OOP, data structures

import uuid
from utils import (validate_pan, validate_phone,
                   validate_email, generate_account_number,
                   format_currency)
from database import (insert_customer, get_customer,
                       get_customer_with_accounts, insert_account)
from account import SavingsAccount, CurrentAccount
from email_otp import send_otp_email, verify_otp

class Customer:
    """
    Customer class
    Covers: Class, Object, Encapsulation
    """

    def __init__(self, name, email, phone,
                 pan=None, address=None, dob=None):
        # Validate inputs using regex functions
        if not validate_email(email):
            raise ValueError(f"Invalid email: {email}")

        if not validate_phone(phone):
            raise ValueError(f"Invalid phone: {phone}")

        if pan and not validate_pan(pan):
            raise ValueError(f"Invalid PAN: {pan}")

        # Private attributes
        self.__customer_id = str(uuid.uuid4())[:8].upper()
        self.__name        = name.strip().title()
        self.__email       = email.lower()
        self.__phone       = str(phone)
        self.__pan         = pan.upper() if pan else None
        self.__address     = address
        self.__dob         = dob
        self.__accounts    = {}  # Dictionary of accounts
        self.__is_verified = False

    # ── Properties ──
    @property
    def customer_id(self):
        return self.__customer_id

    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    @property
    def is_verified(self):
        return self.__is_verified

    def register(self):
        """
        Register customer with OTP verification
        Covers: OOP, Email, Exception Handling
        """
        print(f"\n{'='*50}")
        print(f"Registering: {self.__name}")
        print(f"{'='*50}")

        # Step 1 — Send OTP
        print(f"\nSending OTP to {self.__email}...")
        otp = send_otp_email(self.__email, self.__name)

        # Step 2 — Verify OTP
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                entered_otp = input(
                    f"\nEnter the OTP sent to {self.__email}: "
                ).strip()

                if verify_otp(self.__email, entered_otp):
                    self.__is_verified = True
                    break

            except ValueError as e:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    print(f"{e}. {remaining} attempts remaining.")
                else:
                    raise ValueError(
                        "Too many failed attempts. Registration failed."
                    )

        if not self.__is_verified:
            raise ValueError("OTP verification failed.")

        # Step 3 — Save to database
        insert_customer({
            'customer_id':   self.__customer_id,
            'name':          self.__name,
            'email':         self.__email,
            'phone':         self.__phone,
            'pan':           self.__pan,
            'address':       self.__address,
            'date_of_birth': self.__dob
        })

        print(f"\n✅ Registration successful!")
        print(f"   Customer ID: {self.__customer_id}")
        print(f"   Name:        {self.__name}")

        return self.__customer_id

    def open_account(self, account_type='SAVINGS'):
        """
        Open a new bank account
        Covers: OOP, Dictionary operations
        """
        if not self.__is_verified:
            raise ValueError("Customer not verified. Register first.")

        account_number = generate_account_number()

        # Create appropriate account type
        # Polymorphism — different objects, same interface
        if account_type.upper() == 'SAVINGS':
            account = SavingsAccount(
                account_number, self.__customer_id
            )
        elif account_type.upper() == 'CURRENT':
            account = CurrentAccount(
                account_number, self.__customer_id
            )
        else:
            raise ValueError(f"Unknown account type: {account_type}")

        # Store in dictionary — Dictionary topic
        self.__accounts[account_number] = account

        # Save to database
        insert_account({
            'account_number': account_number,
            'customer_id':    self.__customer_id,
            'account_type':   account_type.upper(),
            'balance':        0
        })

        print(f"\n✅ Account opened successfully!")
        print(f"   Account Number: {account_number}")
        print(f"   Account Type:   {account_type.upper()}")
        print(f"   Minimum Balance: {format_currency(1000)}")

        return account

    def get_all_accounts(self):
        """
        Get all accounts summary
        Covers: Dictionary, List comprehension
        """
        accounts_data = get_customer_with_accounts(self.__customer_id)

        # List comprehension — covers Comprehensions topic
        active_accounts = [
            acc for acc in accounts_data
            if acc['account_number'] is not None
        ]

        return active_accounts

    def get_portfolio_summary(self):
        """
        Complete portfolio summary
        Covers: Dictionary, String formatting, List comprehension
        """
        accounts = self.get_all_accounts()

        # Dictionary comprehension — covers Dict Comprehension
        balances = {
            acc['account_type']: acc['balance']
            for acc in accounts
        }

        # Set comprehension — covers Set Comprehension
        account_types = {acc['account_type'] for acc in accounts}

        total_balance = sum(balances.values())

        summary = {
            'customer_id':    self.__customer_id,
            'name':           self.__name,
            'email':          self.__email,
            'total_accounts': len(accounts),
            'account_types':  account_types,
            'total_balance':  total_balance,
            'balances':       balances
        }

        return summary

    def __str__(self):
        return (
            f"Customer: {self.__name} "
            f"(ID: {self.__customer_id}) | "
            f"Verified: {self.__is_verified}"
        )

print("Customer class loaded!")