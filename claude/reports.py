# reports.py
# PDF and CSV report generation
# Covers: CSV data, PDF data, File I/O

import csv
import json
from datetime import datetime
from database import get_transactions, get_customer_with_accounts
from utils import format_currency

def export_transactions_to_csv(account_number, filename=None):
    """
    Export transactions to CSV
    Covers: CSV data, File I/O
    """
    if not filename:
        filename = f"statement_{account_number}_{datetime.now().strftime('%Y%m%d')}.csv"

    transactions = get_transactions(account_number, limit=100)

    if not transactions:
        print("No transactions found.")
        return None

    # Write CSV file
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            'Transaction ID', 'Date', 'Type',
            'Amount', 'Balance After', 'Description'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write rows — list comprehension
        rows = [
            {
                'Transaction ID': t['transaction_id'],
                'Date':           t['timestamp'],
                'Type':           t['transaction_type'],
                'Amount':         format_currency(t['amount']),
                'Balance After':  format_currency(t['balance_after']),
                'Description':    t['description']
            }
            for t in transactions
        ]

        writer.writerows(rows)

    print(f"✅ CSV statement saved: {filename}")
    return filename

def read_transactions_from_csv(filename):
    """
    Read transactions from CSV
    Covers: CSV reading, File I/O
    """
    transactions = []

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transactions.append(dict(row))

    return transactions

def export_to_json(data, filename):
    """
    Export data to JSON
    Covers: JSON data, File I/O
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, default=str)

    print(f"✅ JSON report saved: {filename}")

def read_from_json(filename):
    """
    Read data from JSON file
    Covers: JSON data, File I/O
    """
    with open(filename, 'r') as f:
        return json.load(f)

def generate_account_statement(account_number, customer_name):
    """
    Generate complete account statement as text
    Covers: String methods, File I/O, List comprehension
    """
    transactions = get_transactions(account_number, limit=50)

    # Build statement string
    separator = "=" * 60

    statement = f"""
{separator}
         ACCOUNT STATEMENT
         Stephen's Digital Bank
{separator}
Account Number : {account_number}
Customer Name  : {customer_name}
Generated On   : {datetime.now().strftime("%d %B %Y %H:%M:%S")}
{separator}

DATE                 TYPE           AMOUNT        BALANCE
{'-'*60}
"""
    if transactions:
        for t in transactions:
            line = (
                f"{t['timestamp'][:19]:<20} "
                f"{t['transaction_type']:<14} "
                f"{format_currency(t['amount']):>12} "
                f"{format_currency(t['balance_after']):>12}\n"
            )
            statement += line
    else:
        statement += "No transactions found.\n"

    statement += f"\n{separator}\n"
    statement += "Note: This is a computer-generated statement.\n"
    statement += f"{separator}\n"

    # Save statement to file — File I/O
    filename = f"statement_{account_number}.txt"
    with open(filename, 'w') as f:
        f.write(statement)

    print(f"✅ Statement saved: {filename}")
    print(statement)

    return statement

print("Reports module loaded!")