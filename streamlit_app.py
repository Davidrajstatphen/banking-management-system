# streamlit_app.py
import streamlit as st
import sqlite3
import uuid
from datetime import datetime
from database import (initialize_database, insert_customer,
                      get_customer, insert_account,
                      update_balance, insert_transaction,
                      get_transactions, get_customer_with_accounts)
from utils import (validate_pan, validate_phone, validate_email,
                   generate_account_number, format_currency,
                   generate_otp, get_timestamp)

# Page config
st.set_page_config(
    page_title="Stephen's Digital Bank",
    page_icon="🏦",
    layout="wide"
)

# Initialize database
initialize_database()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page         = 'home'
if 'customer_id' not in st.session_state:
    st.session_state.customer_id  = None
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = None
if 'account_number' not in st.session_state:
    st.session_state.account_number = None
if 'otp' not in st.session_state:
    st.session_state.otp          = None
if 'temp_customer' not in st.session_state:
    st.session_state.temp_customer = None

# Custom CSS
st.markdown("""
<style>
.bank-header {
    background: linear-gradient(135deg, #1F4E79, #2E75B6);
    padding: 25px 30px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
}
.metric-box {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    border: 1px solid #e0e0e0;
}
.success-box {
    background: #d4edda;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #c3e6cb;
    color: #155724;
}
.error-box {
    background: #f8d7da;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #f5c6cb;
    color: #721c24;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="bank-header">
    <h1>🏦 Stephen's Digital Bank</h1>
    <p>Complete Banking Management System</p>
    <p style="font-size:12px; opacity:0.8">
        Built with Python | OOP | SQLite | Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation
if st.session_state.customer_id:
    # Logged in navigation
    col1,col2,col3,col4,col5,col6 = st.columns(6)
    if col1.button("🏠 Home",        use_container_width=True): st.session_state.page = 'dashboard'
    if col2.button("💰 Deposit",     use_container_width=True): st.session_state.page = 'deposit'
    if col3.button("💸 Withdraw",    use_container_width=True): st.session_state.page = 'withdraw'
    if col4.button("🔄 Transfer",    use_container_width=True): st.session_state.page = 'transfer'
    if col5.button("📋 History",     use_container_width=True): st.session_state.page = 'history'
    if col6.button("🚪 Logout",      use_container_width=True):
        st.session_state.customer_id   = None
        st.session_state.customer_name = None
        st.session_state.account_number = None
        st.session_state.page = 'home'
        st.rerun()
    st.divider()
else:
    col1, col2, col3 = st.columns(3)
    if col1.button("🏠 Home",     use_container_width=True): st.session_state.page = 'home'
    if col2.button("📝 Register", use_container_width=True): st.session_state.page = 'register'
    if col3.button("🔑 Login",    use_container_width=True): st.session_state.page = 'login'
    st.divider()

# ── HOME PAGE ──
if st.session_state.page == 'home':
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**🔐 Secure Banking**\n\nOTP verified registration with PAN and phone validation")
    with col2:
        st.info("**💳 Multiple Accounts**\n\nSavings and Current accounts with different interest rates")
    with col3:
        st.info("**📊 Full Reports**\n\nTransaction history, CSV export and portfolio summary")

    st.divider()
    st.subheader("What this project covers:")
    col1, col2 = st.columns(2)
    with col1:
        st.write("✅ Python OOP — Class, Inheritance, Polymorphism")
        st.write("✅ SQLite Database — CRUD + Joins")
        st.write("✅ Regex — PAN, Phone, Email validation")
        st.write("✅ File I/O — Logs and CSV export")
        st.write("✅ Exception Handling — throughout")
    with col2:
        st.write("✅ Decorators — logging and validation")
        st.write("✅ Generators — transaction streaming")
        st.write("✅ JSON — config management")
        st.write("✅ Comprehensions — data filtering")
        st.write("✅ OTP Email — SMTP verification")

# ── REGISTER PAGE ──
elif st.session_state.page == 'register':
    st.subheader("📝 Register New Customer")

    if st.session_state.otp is None:
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                name  = st.text_input("Full Name")
                email = st.text_input("Email Address")
                phone = st.text_input("Phone Number (10 digits)")
            with col2:
                pan     = st.text_input("PAN Number (optional)")
                address = st.text_input("Address")
                acc_type = st.selectbox("Account Type",
                                        ["Savings (4.5% interest)",
                                         "Current (0% interest)"])

            submitted = st.form_submit_button(
                "📧 Send OTP", use_container_width=True
            )

            if submitted:
                errors = []
                if not name:
                    errors.append("Name is required")
                if not validate_email(email):
                    errors.append("Invalid email format")
                if not validate_phone(phone):
                    errors.append("Invalid phone — must be 10 digits")
                if pan and not validate_pan(pan):
                    errors.append("Invalid PAN format (e.g. ABCDE1234F)")

                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    otp = generate_otp()
                    st.session_state.otp = otp
                    st.session_state.temp_customer = {
                        'name':     name,
                        'email':    email,
                        'phone':    phone,
                        'pan':      pan if pan else None,
                        'address':  address,
                        'acc_type': acc_type
                    }
                    st.success(f"OTP sent to {email}")
                    st.info(f"**Demo OTP: {otp}**")
                    st.rerun()

    else:
        # OTP verification
        temp = st.session_state.temp_customer
        st.success(f"OTP sent to {temp['email']}")
        st.info(f"**Demo OTP: {st.session_state.otp}**")

        entered_otp = st.text_input(
            "Enter 6-digit OTP",
            max_chars=6,
            placeholder="Enter OTP here"
        )

        col1, col2 = st.columns(2)

        if col1.button("✅ Verify OTP", use_container_width=True):
            if entered_otp == st.session_state.otp:
                try:
                    customer_id    = str(uuid.uuid4())[:8].upper()
                    account_number = generate_account_number()
                    acc_type_clean = 'SAVINGS' if 'Savings' in temp['acc_type'] else 'CURRENT'

                    # Save customer
                    insert_customer({
                        'customer_id':   customer_id,
                        'name':          temp['name'].title(),
                        'email':         temp['email'],
                        'phone':         temp['phone'],
                        'pan':           temp['pan'],
                        'address':       temp['address'],
                        'date_of_birth': None
                    })

                    # Create account
                    insert_account({
                        'account_number': account_number,
                        'customer_id':    customer_id,
                        'account_type':   acc_type_clean,
                        'balance':        0
                    })

                    st.session_state.customer_id    = customer_id
                    st.session_state.customer_name  = temp['name'].title()
                    st.session_state.account_number = account_number
                    st.session_state.otp            = None
                    st.session_state.temp_customer  = None
                    st.session_state.page           = 'dashboard'

                    st.success(f"✅ Welcome {temp['name'].title()}!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Registration failed: {e}")
            else:
                st.error("❌ Wrong OTP! Try again.")

        if col2.button("🔄 Resend OTP", use_container_width=True):
            new_otp = generate_otp()
            st.session_state.otp = new_otp
            st.info(f"New Demo OTP: {new_otp}")
            st.rerun()

# ── LOGIN PAGE ──
elif st.session_state.page == 'login':
    st.subheader("🔑 Customer Login")

    with st.form("login_form"):
        customer_id = st.text_input("Customer ID")
        submitted   = st.form_submit_button(
            "Login", use_container_width=True
        )

        if submitted:
            customer = get_customer(customer_id.upper())
            if customer:
                accounts = get_customer_with_accounts(customer_id.upper())
                if accounts:
                    st.session_state.customer_id    = customer['customer_id']
                    st.session_state.customer_name  = customer['name']
                    st.session_state.account_number = accounts[0]['account_number']
                    st.session_state.page           = 'dashboard'
                    st.success(f"Welcome back {customer['name']}!")
                    st.rerun()
                else:
                    st.error("No accounts found for this customer.")
            else:
                st.error("Customer ID not found.")

# ── DASHBOARD ──
elif st.session_state.page == 'dashboard':
    st.subheader(f"👋 Welcome, {st.session_state.customer_name}!")

    # Get current balance
    from database import get_account
    account = get_account(st.session_state.account_number)
    balance = account['balance'] if account else 0

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Balance",     format_currency(balance))
    col2.metric("🏦 Account",     st.session_state.account_number)
    col3.metric("👤 Customer ID", st.session_state.customer_id)
    col4.metric("📅 Date",        datetime.now().strftime("%d %b %Y"))

    st.divider()

    # Recent transactions
    st.subheader("Recent Transactions")
    transactions = get_transactions(
        st.session_state.account_number, limit=5
    )

    if transactions:
        import pandas as pd
        df = pd.DataFrame(transactions)
        df = df[['timestamp','transaction_type','amount',
                 'balance_after','description']]
        df.columns = ['Date','Type','Amount','Balance After','Description']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Make your first deposit!")

# ── DEPOSIT ──
elif st.session_state.page == 'deposit':
    st.subheader("💰 Deposit Money")

    from database import get_account
    account = get_account(st.session_state.account_number)
    balance = account['balance'] if account else 0

    st.metric("Current Balance", format_currency(balance))

    with st.form("deposit_form"):
        amount      = st.number_input("Deposit Amount (Rs)",
                                       min_value=1.0, value=1000.0)
        description = st.text_input("Description",
                                     value="Cash Deposit")
        submitted   = st.form_submit_button(
            "💰 Deposit", use_container_width=True
        )

        if submitted:
            try:
                new_balance = balance + amount
                update_balance(st.session_state.account_number,
                               new_balance)

                trans_id = str(uuid.uuid4())[:8].upper()
                insert_transaction({
                    'transaction_id':   trans_id,
                    'account_number':   st.session_state.account_number,
                    'transaction_type': 'DEPOSIT',
                    'amount':           amount,
                    'balance_after':    new_balance,
                    'description':      description
                })

                st.success(f"✅ Rs {amount:,.0f} deposited successfully!")
                st.metric("New Balance", format_currency(new_balance))

            except Exception as e:
                st.error(f"❌ Deposit failed: {e}")

# ── WITHDRAW ──
elif st.session_state.page == 'withdraw':
    st.subheader("💸 Withdraw Money")

    from database import get_account
    account = get_account(st.session_state.account_number)
    balance = account['balance'] if account else 0

    st.metric("Current Balance", format_currency(balance))

    with st.form("withdraw_form"):
        amount      = st.number_input("Withdrawal Amount (Rs)",
                                       min_value=1.0, value=500.0)
        description = st.text_input("Description", value="Cash Withdrawal")
        submitted   = st.form_submit_button(
            "💸 Withdraw", use_container_width=True
        )

        if submitted:
            if balance - amount < 1000:
                st.error("❌ Cannot go below minimum balance of Rs 1,000")
            else:
                try:
                    new_balance = balance - amount
                    update_balance(st.session_state.account_number,
                                   new_balance)

                    trans_id = str(uuid.uuid4())[:8].upper()
                    insert_transaction({
                        'transaction_id':   trans_id,
                        'account_number':   st.session_state.account_number,
                        'transaction_type': 'WITHDRAWAL',
                        'amount':           amount,
                        'balance_after':    new_balance,
                        'description':      description
                    })

                    st.success(f"✅ Rs {amount:,.0f} withdrawn successfully!")
                    st.metric("New Balance", format_currency(new_balance))

                except Exception as e:
                    st.error(f"❌ Withdrawal failed: {e}")

# ── TRANSFER ──
elif st.session_state.page == 'transfer':
    st.subheader("🔄 Transfer Money")

    from database import get_account
    account = get_account(st.session_state.account_number)
    balance = account['balance'] if account else 0

    st.metric("Available Balance", format_currency(balance))

    with st.form("transfer_form"):
        col1, col2 = st.columns(2)
        with col1:
            to_account = st.text_input("To Account Number")
            ben_name   = st.text_input("Beneficiary Name")
        with col2:
            amount  = st.number_input("Amount (Rs)",
                                       min_value=1.0, value=1000.0)
            remarks = st.text_input("Remarks", value="Transfer")

        submitted = st.form_submit_button(
            "🔄 Transfer Now", use_container_width=True
        )

        if submitted:
            if not to_account or len(to_account) < 10:
                st.error("❌ Enter valid account number")
            elif balance - amount < 1000:
                st.error("❌ Insufficient balance")
            else:
                try:
                    new_balance = balance - amount
                    update_balance(st.session_state.account_number,
                                   new_balance)

                    trans_id = str(uuid.uuid4())[:8].upper()
                    insert_transaction({
                        'transaction_id':   trans_id,
                        'account_number':   st.session_state.account_number,
                        'transaction_type': 'TRANSFER',
                        'amount':           amount,
                        'balance_after':    new_balance,
                        'description':      f'Transfer to {ben_name}'
                    })

                    st.success(f"✅ Rs {amount:,.0f} transferred to {ben_name}!")
                    st.metric("New Balance", format_currency(new_balance))

                except Exception as e:
                    st.error(f"❌ Transfer failed: {e}")

# ── TRANSACTION HISTORY ──
elif st.session_state.page == 'history':
    st.subheader("📋 Transaction History")

    transactions = get_transactions(
        st.session_state.account_number, limit=50
    )

    if transactions:
        import pandas as pd
        df = pd.DataFrame(transactions)
        df = df[['timestamp','transaction_type','amount',
                 'balance_after','description']]
        df.columns = ['Date','Type','Amount (Rs)',
                      'Balance After (Rs)','Description']

        # Summary metrics
        deposits    = df[df['Type']=='DEPOSIT']['Amount (Rs)'].sum()
        withdrawals = df[df['Type'].isin(['WITHDRAWAL','TRANSFER'])]['Amount (Rs)'].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Deposits",     f"Rs {deposits:,.0f}")
        col2.metric("Total Withdrawals",  f"Rs {withdrawals:,.0f}")
        col3.metric("Total Transactions", len(df))

        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)

        # CSV Export
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV Statement",
            data=csv,
            file_name=f"statement_{st.session_state.account_number}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No transactions found.")

# Footer
st.divider()
st.markdown("""
<div style='text-align:center; color:gray; font-size:12px;'>
    Built by Stephen David | Python + OOP + SQLite + Streamlit |
    AI & Data Science Portfolio Project
</div>
""", unsafe_allow_html=True)
