# database.py
# SQLite database operations
# Covers: SQL Database, CRUD, Joins

import sqlite3
import json
from datetime import datetime

DATABASE = 'banking_system.db'

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """
    Create all tables
    Covers: SQLite, CREATE TABLE
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id   TEXT PRIMARY KEY,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            phone         TEXT NOT NULL,
            pan           TEXT UNIQUE,
            address       TEXT,
            date_of_birth TEXT,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active     INTEGER DEFAULT 1
        )
    ''')

    # Accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_number TEXT PRIMARY KEY,
            customer_id    TEXT NOT NULL,
            account_type   TEXT NOT NULL,
            balance        REAL DEFAULT 0,
            created_at     TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active      INTEGER DEFAULT 1,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
    ''')

    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id   TEXT PRIMARY KEY,
            account_number   TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount           REAL NOT NULL,
            balance_after    REAL NOT NULL,
            description      TEXT,
            timestamp        TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_number)
                REFERENCES accounts(account_number)
        )
    ''')

    # Loans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            loan_id        TEXT PRIMARY KEY,
            customer_id    TEXT NOT NULL,
            amount         REAL NOT NULL,
            interest_rate  REAL NOT NULL,
            tenure_months  INTEGER NOT NULL,
            status         TEXT DEFAULT 'pending',
            applied_at     TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized!")

# ── CUSTOMER CRUD OPERATIONS ──
def insert_customer(customer_data):
    """INSERT — Create new customer"""
    conn   = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO customers
            (customer_id, name, email, phone, pan, address, date_of_birth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_data['customer_id'],
            customer_data['name'],
            customer_data['email'],
            customer_data['phone'],
            customer_data.get('pan'),
            customer_data.get('address'),
            customer_data.get('date_of_birth')
        ))
        conn.commit()
        print(f"Customer {customer_data['name']} added!")
        return True

    except sqlite3.IntegrityError as e:
        raise ValueError(f"Customer already exists: {e}")
    finally:
        conn.close()

def get_customer(customer_id):
    """SELECT — Get customer by ID"""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM customers WHERE customer_id = ?',
        (customer_id,)
    )
    customer = cursor.fetchone()
    conn.close()

    return dict(customer) if customer else None

def get_customer_by_email(email):
    """SELECT — Get customer by email"""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM customers WHERE email = ?',
        (email,)
    )
    customer = cursor.fetchone()
    conn.close()

    return dict(customer) if customer else None

def update_customer(customer_id, updates):
    """UPDATE — Update customer details"""
    conn   = get_connection()
    cursor = conn.cursor()

    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values     = list(updates.values()) + [customer_id]

    cursor.execute(
        f'UPDATE customers SET {set_clause} WHERE customer_id = ?',
        values
    )
    conn.commit()
    conn.close()
    print("Customer updated!")

def delete_customer(customer_id):
    """DELETE — Deactivate customer (soft delete)"""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'UPDATE customers SET is_active = 0 WHERE customer_id = ?',
        (customer_id,)
    )
    conn.commit()
    conn.close()

# ── ACCOUNT OPERATIONS ──
def insert_account(account_data):
    """INSERT — Create new account"""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO accounts
        (account_number, customer_id, account_type, balance)
        VALUES (?, ?, ?, ?)
    ''', (
        account_data['account_number'],
        account_data['customer_id'],
        account_data['account_type'],
        account_data.get('balance', 0)
    ))
    conn.commit()
    conn.close()

def get_account(account_number):
    """SELECT — Get account details"""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM accounts WHERE account_number = ?',
        (account_number,)
    )
    account = cursor.fetchone()
    conn.close()

    return dict(account) if account else None

def update_balance(account_number, new_balance):
    """UPDATE — Update account balance"""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'UPDATE accounts SET balance = ? WHERE account_number = ?',
        (new_balance, account_number)
    )
    conn.commit()
    conn.close()

# ── TRANSACTION OPERATIONS ──
def insert_transaction(trans_data):
    """INSERT — Record a transaction"""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transactions
        (transaction_id, account_number, transaction_type,
         amount, balance_after, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        trans_data['transaction_id'],
        trans_data['account_number'],
        trans_data['transaction_type'],
        trans_data['amount'],
        trans_data['balance_after'],
        trans_data.get('description', '')
    ))
    conn.commit()
    conn.close()

def get_transactions(account_number, limit=50):
    """SELECT — Get transaction history"""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM transactions
        WHERE account_number = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (account_number, limit))

    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return transactions

# ── JOINS — Customer with Account details ──
def get_customer_with_accounts(customer_id):
    """
    JOIN query — customer + accounts
    Covers: SQL Joins topic
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            c.customer_id,
            c.name,
            c.email,
            c.phone,
            a.account_number,
            a.account_type,
            a.balance,
            a.created_at as account_created
        FROM customers c
        INNER JOIN accounts a
            ON c.customer_id = a.customer_id
        WHERE c.customer_id = ?
            AND c.is_active = 1
            AND a.is_active = 1
    ''', (customer_id,))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results

def get_all_customers_summary():
    """
    Complex JOIN — all customers with account summary
    Covers: SQL Joins, GROUP BY
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            c.customer_id,
            c.name,
            c.email,
            COUNT(a.account_number) as total_accounts,
            SUM(a.balance) as total_balance,
            MAX(a.created_at) as last_account_date
        FROM customers c
        LEFT JOIN accounts a
            ON c.customer_id = a.customer_id
            AND a.is_active = 1
        WHERE c.is_active = 1
        GROUP BY c.customer_id
        ORDER BY total_balance DESC
    ''')

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results

print("Database module loaded!")