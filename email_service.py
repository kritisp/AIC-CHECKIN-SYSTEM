import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_qr_email(to_email, name, uid, qr_url):
    msg = EmailMessage()
    msg["Subject"] = "AIC SOA 2026 | Your Entry QR Code"
    msg["From"] = f"AIC SOA <{SMTP_EMAIL}>"
    msg["To"] = to_email

    msg.set_content(f"""
Dear {name},

Thank you for registering for the AIC–SOA program.

Your Entry ID: {uid}

QR Code: {qr_url}

Please show this QR code at the venue entrance.

Venue: SOA Convention Hall
Date: 7 Feb 2026

Regards,
AIC SOA Foundation
""")

    msg.add_alternative(f"""
    <html>
      <body style="font-family: Arial;">
        <h2>AI for Education 2026</h2>
        <p><strong>Policy • Practice • Future Pathways</strong></p>

        <p>Dear {name},</p>

        <p><strong>Entry ID:</strong> {uid}</p>

        <img src="{qr_url}" width="220"/>

        <p>📍 SOA Convention Hall<br/>
        🕘 7 Feb 2026</p>

        <p><strong>Please do not share this QR.</strong></p>

        <p>Regards,<br/>AIC SOA Foundation</p>
      </body>
    </html>
    """, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp.send_message(msg)
