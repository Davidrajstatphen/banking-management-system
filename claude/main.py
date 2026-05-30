# main.py
# Main entry point
# Covers: All topics together

from database import initialize_database
from customer import Customer
from utils import format_currency
from reports import (export_transactions_to_csv,
                      generate_account_statement,
                      export_to_json)

def display_menu():
    """Display main menu"""
    print("""
╔══════════════════════════════════════╗
║     STEPHEN'S DIGITAL BANK          ║
║     Banking Management System       ║
╚══════════════════════════════════════╝

1.  Register New Customer
2.  Open Bank Account
3.  Deposit Money
4.  Withdraw Money
5.  Check Balance
6.  Transaction History
7.  Transfer Money
8.  Account Statement (CSV)
9.  Portfolio Summary
10. Exit

Enter choice (1-10): """)

def main():
    """Main function — entry point"""
    print("\n🏦 Welcome to Stephen's Digital Bank!")
    print("Initializing system...")

    # Initialize database
    initialize_database()

    # Store active customers in memory
    # Dictionary — covers Dictionary topic
    active_customers = {}
    active_accounts  = {}

    print("System ready!\n")

    while True:
        try:
            display_menu()
            choice = input().strip()

            # ── OPTION 1: Register Customer ──
            if choice == '1':
                print("\n=== REGISTER NEW CUSTOMER ===")
                name    = input("Full Name: ").strip()
                email   = input("Email: ").strip()
                phone   = input("Phone (10 digits): ").strip()
                pan     = input("PAN (optional, press Enter to skip): ").strip()
                address = input("Address: ").strip()

                try:
                    customer = Customer(
                        name=name,
                        email=email,
                        phone=phone,
                        pan=pan if pan else None,
                        address=address
                    )
                    customer_id = customer.register()
                    active_customers[customer_id] = customer
                    print(f"\n✅ Welcome to Stephen's Bank, {name}!")

                except ValueError as e:
                    print(f"\n❌ Registration failed: {e}")

            # ── OPTION 2: Open Account ──
            elif choice == '2':
                print("\n=== OPEN BANK ACCOUNT ===")
                customer_id  = input("Customer ID: ").strip().upper()

                if customer_id not in active_customers:
                    print("❌ Customer not found. Please register first.")
                    continue

                print("Account Types:")
                print("1. Savings Account (4.5% interest)")
                print("2. Current Account (0% interest, overdraft facility)")
                acc_choice = input("Choose (1/2): ").strip()

                acc_type = 'SAVINGS' if acc_choice == '1' else 'CURRENT'

                try:
                    customer = active_customers[customer_id]
                    account  = customer.open_account(acc_type)

                    # Initial deposit
                    initial_amount = float(input("\nInitial deposit amount: Rs "))
                    account.deposit(initial_amount)

                    active_accounts[account.account_number] = account

                except Exception as e:
                    print(f"\n❌ Error: {e}")

            # ── OPTION 3: Deposit ──
            elif choice == '3':
                print("\n=== DEPOSIT MONEY ===")
                acc_num = input("Account Number: ").strip()

                if acc_num not in active_accounts:
                    print("❌ Account not found in this session.")
                    continue

                amount = float(input("Amount to deposit: Rs "))

                try:
                    active_accounts[acc_num].deposit(amount)
                except Exception as e:
                    print(f"❌ Error: {e}")

            # ── OPTION 4: Withdraw ──
            elif choice == '4':
                print("\n=== WITHDRAW MONEY ===")
                acc_num = input("Account Number: ").strip()

                if acc_num not in active_accounts:
                    print("❌ Account not found in this session.")
                    continue

                amount = float(input("Amount to withdraw: Rs "))

                try:
                    active_accounts[acc_num].withdraw(amount)
                except Exception as e:
                    print(f"❌ Error: {e}")

            # ── OPTION 5: Check Balance ──
            elif choice == '5':
                print("\n=== CHECK BALANCE ===")
                acc_num = input("Account Number: ").strip()

                if acc_num not in active_accounts:
                    print("❌ Account not found.")
                    continue

                account = active_accounts[acc_num]
                print(f"\nAccount: {acc_num}")
                print(f"Type:    {account.account_type}")
                print(f"Balance: {format_currency(account.get_balance())}")

            # ── OPTION 6: Transaction History ──
            elif choice == '6':
                print("\n=== TRANSACTION HISTORY ===")
                acc_num = input("Account Number: ").strip()

                if acc_num not in active_accounts:
                    print("❌ Account not found.")
                    continue

                transactions = active_accounts[acc_num].get_transaction_history(10)

                if not transactions:
                    print("No transactions yet.")
                else:
                    print(f"\nLast {len(transactions)} transactions:")
                    print("-" * 65)

                    # Generator usage — covers Generators topic
                    from utils import transaction_generator
                    for batch in transaction_generator(transactions, 5):
                        for t in batch:
                            print(
                                f"{t['timestamp'][:19]} | "
                                f"{t['transaction_type']:<12} | "
                                f"{format_currency(t['amount']):>12} | "
                                f"Bal: {format_currency(t['balance_after'])}"
                            )

            # ── OPTION 7: Transfer Money ──
            elif choice == '7':
                print("\n=== TRANSFER MONEY ===")
                from_acc = input("From Account: ").strip()
                to_acc   = input("To Account: ").strip()

                if from_acc not in active_accounts:
                    print("❌ Source account not found.")
                    continue
                if to_acc not in active_accounts:
                    print("❌ Destination account not found.")
                    continue

                amount = float(input("Amount to transfer: Rs "))

                try:
                    # Withdraw from source
                    active_accounts[from_acc].withdraw(amount)
                    # Deposit to destination
                    active_accounts[to_acc].deposit(amount)
                    print(f"\n✅ Transfer of {format_currency(amount)} successful!")

                except Exception as e:
                    print(f"❌ Transfer failed: {e}")

            # ── OPTION 8: Account Statement ──
            elif choice == '8':
                print("\n=== ACCOUNT STATEMENT ===")
                acc_num     = input("Account Number: ").strip()
                cust_name   = input("Customer Name: ").strip()

                try:
                    # Generate text statement
                    generate_account_statement(acc_num, cust_name)

                    # Export to CSV
                    csv_file = export_transactions_to_csv(acc_num)
                    print(f"CSV exported: {csv_file}")

                except Exception as e:
                    print(f"❌ Error: {e}")

            # ── OPTION 9: Portfolio Summary ──
            elif choice == '9':
                print("\n=== PORTFOLIO SUMMARY ===")
                customer_id = input("Customer ID: ").strip().upper()

                if customer_id not in active_customers:
                    print("❌ Customer not found.")
                    continue

                try:
                    summary = active_customers[customer_id].get_portfolio_summary()

                    print(f"\n{'='*45}")
                    print(f"PORTFOLIO SUMMARY — {summary['name']}")
                    print(f"{'='*45}")
                    print(f"Customer ID:    {summary['customer_id']}")
                    print(f"Total Accounts: {summary['total_accounts']}")
                    print(f"Account Types:  {summary['account_types']}")
                    print(f"Total Balance:  {format_currency(summary['total_balance'])}")
                    print(f"{'='*45}")

                    # Export to JSON
                    json_file = f"portfolio_{customer_id}.json"
                    export_to_json(summary, json_file)

                except Exception as e:
                    print(f"❌ Error: {e}")

            # ── OPTION 10: Exit ──
            elif choice == '10':
                print("\n🏦 Thank you for using Stephen's Digital Bank!")
                print("Goodbye!\n")
                break

            else:
                print("❌ Invalid choice. Please enter 1-10.")

        # Exception Handling — covers Exception Handling topic
        except ValueError as e:
            print(f"\n❌ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n\nExiting... Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()