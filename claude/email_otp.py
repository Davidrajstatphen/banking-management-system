# email_otp.py
# OTP email verification system

import smtplib
import json
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import generate_otp, validate_email

# Load config
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

# Store OTPs temporarily
# In production use Redis or database
otp_storage = {}

def send_otp_email(recipient_email, customer_name):
    """
    Send OTP to customer email for verification
    Covers: File I/O, Exception Handling, String methods

    Returns: OTP string if sent successfully
    """
    # Validate email first
    if not validate_email(recipient_email):
        raise ValueError(f"Invalid email: {recipient_email}")

    # Generate OTP
    otp = generate_otp()

    # Store OTP for this email
    otp_storage[recipient_email] = {
        'otp':       otp,
        'timestamp': __import__('time').time(),
        'verified':  False
    }

    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Your OTP — {CONFIG['bank_name']}"
    msg['From']    = CONFIG['email']['sender_email']
    msg['To']      = recipient_email

    # Email body
    html_body = f"""
    <html>
    <body style="font-family: Arial; padding: 20px;">
        <div style="background: #1F4E79; padding: 20px;
                    border-radius: 10px; text-align: center;">
            <h2 style="color: white;">
                {CONFIG['bank_name']}
            </h2>
        </div>
        <br>
        <p>Dear <b>{customer_name}</b>,</p>
        <p>Your One Time Password (OTP) for account
           verification is:</p>
        <div style="background: #f0f0f0; padding: 20px;
                    text-align: center; border-radius: 8px;
                    margin: 20px 0;">
            <h1 style="color: #1F4E79; font-size: 48px;
                        letter-spacing: 10px;">
                {otp}
            </h1>
        </div>
        <p>This OTP is valid for <b>5 minutes</b>.</p>
        <p>Do not share this OTP with anyone.</p>
        <br>
        <p style="color: #999; font-size: 12px;">
            This is an automated message from
            {CONFIG['bank_name']}.
        </p>
    </body>
    </html>
    """

    text_body = f"""
    Dear {customer_name},
    Your OTP is: {otp}
    Valid for 5 minutes.
    Do not share with anyone.
    """

    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP(
            CONFIG['email']['smtp_server'],
            CONFIG['email']['smtp_port']
        )
        server.starttls()
        server.login(
            CONFIG['email']['sender_email'],
            CONFIG['email']['sender_password']
        )
        server.sendmail(
            CONFIG['email']['sender_email'],
            recipient_email,
            msg.as_string()
        )
        server.quit()

        print(f"OTP sent to {recipient_email}")
        return otp

    except smtplib.SMTPAuthenticationError:
        print("Email auth failed. Using console OTP for demo.")
        print(f"DEMO OTP: {otp}")
        return otp

    except Exception as e:
        print(f"Email error: {e}")
        print(f"DEMO OTP: {otp}")
        return otp

def verify_otp(email, entered_otp):
    """
    Verify OTP entered by customer
    Returns: True if valid, False otherwise
    """
    import time

    if email not in otp_storage:
        raise ValueError("No OTP generated for this email")

    stored = otp_storage[email]

    # Check expiry — 5 minutes = 300 seconds
    if time.time() - stored['timestamp'] > 300:
        del otp_storage[email]
        raise ValueError("OTP has expired. Please request a new one.")

    # Check if already verified
    if stored['verified']:
        raise ValueError("OTP already used.")

    # Verify OTP
    if stored['otp'] == entered_otp:
        otp_storage[email]['verified'] = True
        del otp_storage[email]
        print("OTP verified successfully!")
        return True
    else:
        raise ValueError("Invalid OTP. Please try again.")

def resend_otp(email, customer_name):
    """Resend a fresh OTP"""
    # Remove old OTP
    if email in otp_storage:
        del otp_storage[email]

    return send_otp_email(email, customer_name)

print("Email OTP system loaded!")