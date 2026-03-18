import os
import smtplib
import io
import qrcode
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# We use standard SMTP variables that can point to Brevo, SendGrid, Resend, etc.
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def generate_qr_bytes(uid: str) -> bytes:
    """Generates a QR code image entirely in memory and returns its bytes."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uid)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def send_qr_email(to_email: str, name: str, uid: str):
    """Generates the QR code and emails it to the participant."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print(f"Warning: SMTP credentials not set, email not sent to {to_email}.")
        return

    msg = EmailMessage()
    msg["Subject"] = "Invitation: AIC–SOA Foundation Inaugural Ceremony"
    
    # Clean sender representation (important for avoid spam filters)
    # Brevo drops emails silently if the From address doesn't exactly match the account
    sender_email = "aic.soa.2026@gmail.com" # The verified email on Brevo
    msg["From"] = f"AIC SOA <{sender_email}>"
    msg["To"] = to_email

    # Plain text fallback
    msg.set_content(f"""
Dear {name},

The much-awaited moment is here! We are delighted to invite you to the Inaugural Ceremony of AIC–SOA Foundation, scheduled at 3:30PM on 19th March 2026.

This milestone marks the beginning of a strengthened innovation and entrepreneurship ecosystem, and your presence as a valued stakeholder will make the occasion even more meaningful. We also encourage Ecosystem Enablers & Startup Founders to join with their innovations and products during the event and engage with fellow founders, industry experts, and ecosystem partners.

In case you are unable to attend personally, you may kindly nominate a representative to participate on your behalf.

Your Entry ID: {uid}
Please find your QR code attached to this email. Show this QR code at the venue entrance.

Event Agenda:
https://drive.google.com/file/d/16QuhxLkcRvCr8qTUIxitC2C9EQex68GI/view?usp=sharing

Your presence and support will greatly contribute to making this inauguration a grand success. We look forward to welcoming you!

Warm regards,
Team AIC–SOA Foundation
""")

    # HTML Body exactly matching new Inauguration script
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2b5797;">AIC–SOA Foundation Inauguration</h2>
        <p>Dear {name},</p>

        <p>The much-awaited moment is here! We are delighted to invite you to the <strong>Inaugural Ceremony of AIC–SOA Foundation</strong>, scheduled at <strong>3:30 PM on 19th March 2026</strong>.</p>

        <p>This milestone marks the beginning of a strengthened innovation and entrepreneurship ecosystem, and your presence as a valued stakeholder will make the occasion even more meaningful. We also encourage Ecosystem Enablers & Startup Founders to join with their innovations and products during the event and engage with fellow founders, industry experts, and ecosystem partners.</p>

        <p><em>In case you are unable to attend personally, you may kindly nominate a representative to participate on your behalf.</em></p>

        <div style="background-color: #f4f6f9; padding: 15px; border-left: 4px solid #2b5797; margin: 20px 0;">
            <p style="margin: 0;"><strong>Your Entry ID:</strong> {uid}</p>
            <p style="margin- 10px 0 0 0;">Please present the QR code below at the registration desk for seamless entry.</p>
        </div>

        <img src="cid:qr_image" width="220" alt="Your Entry QR Code" style="display: block; margin: 10px 0;"/>

        <p><strong>Event Agenda:</strong> <a href="https://drive.google.com/file/d/16QuhxLkcRvCr8qTUIxitC2C9EQex68GI/view?usp=sharing" style="color: #2b5797; text-decoration: none;">View Agenda Here</a></p>

        <p>Your presence and support will greatly contribute to making this inauguration a grand success.<br/>
        We look forward to welcoming you!</p>

        <p>Warm regards,<br/><strong>Team AIC–SOA Foundation</strong></p>
      </body>
    </html>
    """
    
    msg.add_alternative(html_content, subtype="html")

    # Generate the QR code image
    qr_bytes = generate_qr_bytes(uid)
    
    # Attach the QR code and assign a Content-ID so the HTML <img> tag can reference it
    # We add it as an attachment, but specify it's an inline cid reference.
    msg.add_attachment(qr_bytes, maintype='image', subtype='png', filename=f'AIC_QR_{uid}.png', cid="<qr_image>")

    try:
        # Connect to dynamic SMTP server (usually port 587 requires STARTTLS)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            if SMTP_PORT in (587, 2525):
                server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"Successfully sent QR email to {to_email} on port {SMTP_PORT}")
            
    except OSError as oe:
        print(f"Port {SMTP_PORT} timed out/failed (likely blocked by Render firewall). Retrying on fallback port 2525...")
        try:
            # Render blocks port 25, 465, and 587 on their Free Tier. Port 2525 is often unfiltered.
            with smtplib.SMTP(SMTP_SERVER, 2525) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)
                print(f"Successfully sent QR email to {to_email} on fallback port 2525")
        except Exception as e2:
            print(f"Fallback port 2525 also failed for {to_email}: {e2}")
            
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
