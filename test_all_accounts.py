import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# Change to your email if you want to test with a different one
TEST_EMAIL = "kspchimun@gmail.com"

# Load accounts from .env
SMTP_ACCOUNTS = []
for i in range(1, 11):
    email = os.getenv(f"SMTP_EMAIL_{i}")
    password = os.getenv(f"SMTP_PASSWORD_{i}")
    sender = os.getenv(f"SMTP_SENDER_{i}") or "aic.soa.2026@gmail.com"
    if email and password:
        SMTP_ACCOUNTS.append({"email": email, "password": password, "sender": sender})

print(f"🔍 Found {len(SMTP_ACCOUNTS)} accounts configured in .env. Testing them now...\n")

for i, account in enumerate(SMTP_ACCOUNTS):
    print(f"--- Testing Account {i+1} ({account['email']}) ---")
    
    msg = EmailMessage()
    msg["Subject"] = f"🟢 Setup Test - Account {i+1}"
    msg["From"] = f"AIC SOA <{account['sender']}>"
    msg["To"] = TEST_EMAIL
    msg.set_content(f"Hello!\n\nThis is a test email sent from your Brevo Account {i+1} (Login: {account['email']}).\n\nIf you are reading this, this account is verified and ready to send passes!")

    try:
        with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
            server.starttls()
            server.login(account["email"], account["password"])
            server.send_message(msg)
            print(f"✅ SUCCESS: Email sent via Account {i+1}!")
    except smtplib.SMTPAuthenticationError:
        print(f"❌ ERROR: Authentication failed for Account {i+1}. Check your API key in .env.")
    except Exception as e:
        print(f"❌ ERROR: Failed to send via Account {i+1}. Reason: {e}")
    print("-" * 50)

print("\n🎉 Testing Complete! Check your inbox for the test emails.")
