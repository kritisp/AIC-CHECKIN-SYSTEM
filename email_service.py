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

We are thrilled to officially confirm your registration for the Inaugural Ceremony of the AIC–SOA Foundation!

As a participant, you are the future of innovation. This milestone event marks the beginning of a vibrant entrepreneurship ecosystem, and we are excited to have you join us to connect with startup founders, industry experts, and ecosystem enablers.

Event Details:
Date: 19th March 2026
Time: 3:30 PM

Your Entry ID: {uid}
Please find your QR code attached to this email. You must present this QR code at the registration desk for seamless entry into the event.

Event Agenda:
https://drive.google.com/file/d/16QuhxLkcRvCr8qTUIxitC2C9EQex68GI/view?usp=sharing

We look forward to welcoming you and building the future of innovation together!

Warm regards,
Team AIC–SOA Foundation
""")

    # HTML Body: Professional Student Template
    html_content = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            
            <div style="background-color: #2b5797; padding: 25px; text-align: center;">
                <h2 style="color: #ffffff; margin: 0; font-size: 24px;">AIC–SOA Foundation</h2>
                <p style="color: #e0e0e0; margin: 5px 0 0 0; font-size: 16px;">Inaugural Ceremony 2026</p>
            </div>

            <div style="padding: 30px;">
                <p style="font-size: 16px;">Dear <strong>{name}</strong>,</p>

                <p style="font-size: 15px;">We are thrilled to officially confirm your registration for the <strong>Inaugural Ceremony of the AIC–SOA Foundation!</strong></p>

                <p style="font-size: 15px;">As a participant, you are a vital part of the future of innovation. This milestone event marks the beginning of a strengthened entrepreneurship ecosystem, and we are immensely excited to welcome you to connect with startup founders, industry experts, and ecosystem leaders.</p>

                <div style="background-color: #f0f4f8; border-left: 4px solid #2b5797; padding: 15px; margin: 25px 0;">
                    <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;"><strong>Date:</strong> 19th March 2026</p>
                    <p style="margin: 0 0 5px 0; font-size: 14px; color: #555;"><strong>Time:</strong> 3:30 PM</p>
                    <p style="margin: 0; font-size: 14px; color: #555;"><strong>Your Entry ID:</strong> <span style="background-color: #dfe6e9; padding: 2px 6px; border-radius: 4px;">{uid}</span></p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 14px; color: #666; margin-bottom: 10px;">Please present this QR code at the registration desk for seamless entry.</p>
                    <img src="cid:qr_image" width="200" alt="Your Entry QR Code" style="border: 1px solid #ddd; border-radius: 8px; padding: 5px;"/>
                </div>

                <p style="text-align: center;">
                    <a href="https://drive.google.com/file/d/16QuhxLkcRvCr8qTUIxitC2C9EQex68GI/view?usp=sharing" style="display: inline-block; background-color: #2b5797; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 14px;">View Full Event Agenda</a>
                </p>

                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;" />
                
                <p style="font-size: 14px; color: #777; margin: 0;">We look forward to welcoming you!</p>
                <p style="font-size: 14px; color: #333; margin: 5px 0 0 0;">Warm regards,<br/><strong>Team AIC–SOA Foundation</strong></p>
            </div>
        </div>
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
