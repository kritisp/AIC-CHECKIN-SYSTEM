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

# Automatically load up to 10 accounts from .env
SMTP_ACCOUNTS = []

# Fallback to single account if no numbered accounts exist
if os.getenv("SMTP_EMAIL"):
    SMTP_ACCOUNTS.append({
        "email": os.getenv("SMTP_EMAIL"),
        "password": os.getenv("SMTP_PASSWORD"),
        "sender": "aic.soa.2026@gmail.com"
    })

for i in range(1, 11):
    email = os.getenv(f"SMTP_EMAIL_{i}")
    password = os.getenv(f"SMTP_PASSWORD_{i}")
    sender = os.getenv(f"SMTP_SENDER_{i}") or "aic.soa.2026@gmail.com"
    
    if email and password:
        SMTP_ACCOUNTS.append({
            "email": email,
            "password": password,
            "sender": sender
        })


def generate_qr_bytes(uid: str) -> bytes:
    """Generates a QR code image entirely in memory and returns its bytes."""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uid)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def send_qr_email(to_email: str, name: str, uid: str, category: str = "delegate"):
    """Generates the QR code and emails it, automatically falling back if an account limit is reached."""
    if not SMTP_ACCOUNTS:
        print(f"Warning: No SMTP accounts configured in .env, email not sent to {to_email}.")
        return

    # Determine the pass type and theme color based on category
    cat_lower = category.lower() if category else "delegate"
    
    if "student" in cat_lower:
        pass_type = "Student Pass"
        role_display = "Student"
        theme_color = "#2563eb" # Blue Theme
        theme_bg = "#eff6ff"
        instructions_text = """
📌 Helpful Guidelines
- Our volunteer team will be happy to assist you throughout the event.
- We appreciate your cooperation in maintaining a professional atmosphere during all sessions.
"""
        instructions_html = """
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #1a365d; font-size: 16px;">📌 Helpful Guidelines</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #475569; line-height: 1.6;">
                        <li>Our volunteer team will be happy to assist you with any guidance throughout the event.</li>
                        <li>We appreciate your cooperation in maintaining a positive and professional atmosphere during all sessions.</li>
                    </ul>
                </div>
"""
    else:
        pass_type = "Delegate Pass"
        role_display = category.title() if category else "Delegate"
        theme_color = "#475569" # Professional Grey Theme
        theme_bg = "#f8fafc"
        instructions_text = """
ℹ️ Event Information
- Dedicated help desks will be available at the venue to assist you.
"""
        instructions_html = """
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #1a365d; font-size: 16px;">ℹ️ Event Information</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #475569; line-height: 1.6;">
                        <li>Dedicated help desks will be available at the venue to assist you.</li>
                    </ul>
                </div>
"""

    # Plain text fallback
    plain_text_content = f"""
Dear {name},

Greetings from SIKSHA ‘O’ ANUSANDHAN (Deemed to be University) and INAE.

We are pleased to confirm your participation in the INAE Technology Conclave 2026, scheduled on 11th & 12th July 2026 at Campus-II, SOA University, Bhubaneswar.

🎟️ Your Entry Pass
Please find your QR Code attached. This will serve as your official entry pass for the event.
Category: {pass_type}
Your Entry ID: {uid}

📌 Important:
- Carry this QR code (printed or on your phone) for smooth entry
- Entry will be granted only after scanning at the registration desk

📅 Event Highlights
- Flagship program for engineering research, faculty, and professional discourse
- Panel discussions and expert talks
- Innovation showcases & networking opportunities

🕘 Reporting Details
- Date: 11th July 2026
- Reporting Time: 9:00 AM
- Venue: Campus-II, SOA University
{instructions_text}
📝 Note (Very Important)
- After the event, you will receive a Feedback Form
- Submission of the feedback form is mandatory
- 🎓 Participation Certificates will be issued only after completing the feedback form

We look forward to your presence at this prestigious conclave.
For any queries, feel free to contact the organizing team.

Warm regards,
Organizing Committee
INAE Technology Conclave 2026
SIKSHA ‘O’ ANUSANDHAN (Deemed to be University)
Bhubaneswar, Odisha
"""

    # HTML Body: Mobile-Friendly Portrait Ticket Layout
    html_content = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f7f6; padding: 20px 10px; margin: 0;">
        
        <!-- Greeting Section -->
        <div style="max-width: 450px; margin: 0 auto 20px auto; text-align: center;">
            <p style="font-size: 16px; margin-top: 0; margin-bottom: 5px;">Dear <strong>{name}</strong>,</p>
            <p style="font-size: 14px; margin-bottom: 5px;">Welcome to the <strong>INAE Technology Conclave 2026</strong>.</p>
        </div>

        <!-- PORTRAIT TICKET -->
        <div style="max-width: 400px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;">
            
            <!-- Header Banner -->
            <div style="background-color: {theme_color}; padding: 30px 20px; text-align: center; color: #ffffff;">
                <div style="font-size: 12px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px; opacity: 0.9;">
                    Official Entry Pass
                </div>
                <div style="font-size: 24px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin: 0;">
                    {pass_type}
                </div>
            </div>

            <!-- Body Details -->
            <div style="padding: 30px 25px; background-color: {theme_bg};">
                <div style="text-align: center; margin-bottom: 25px;">
                    <div style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold; margin-bottom: 5px;">Participant Name</div>
                    <div style="font-size: 22px; font-weight: 700; color: #0f172a; line-height: 1.2;">{name}</div>
                </div>

                <div style="text-align: center; margin-bottom: 25px;">
                    <div style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold; margin-bottom: 5px;">Category</div>
                    <div style="font-size: 18px; font-weight: 600; color: {theme_color};">{role_display}</div>
                </div>

                <div style="background-color: #ffffff; border-radius: 12px; padding: 20px; margin-bottom: 25px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td width="50%" valign="top" style="border-right: 1px solid #e2e8f0;">
                                <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: bold;">Date</div>
                                <div style="font-size: 15px; font-weight: 600; color: #0f172a; margin-top: 4px;">11 Jul 2026</div>
                            </td>
                            <td width="50%" valign="top">
                                <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: bold;">Reporting</div>
                                <div style="font-size: 15px; font-weight: 600; color: #0f172a; margin-top: 4px;">9:00 AM</div>
                            </td>
                        </tr>
                    </table>
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e2e8f0;">
                        <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: bold;">Venue</div>
                        <div style="font-size: 14px; font-weight: 600; color: #0f172a; margin-top: 4px;">Campus-II, SOA University</div>
                    </div>
                </div>

                <!-- QR Code Section -->
                <div style="text-align: center; background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px dashed #cbd5e1;">
                    <img src="cid:qr_image" width="180" alt="QR Code" style="display: block; margin: 0 auto;"/>
                    <div style="margin-top: 15px; font-family: monospace; font-size: 16px; color: #334155; font-weight: 600; letter-spacing: 2px; background-color: #f1f5f9; padding: 8px; border-radius: 6px; display: inline-block;">{uid}</div>
                </div>
            </div>

            <!-- Ticket Footer -->
            <div style="background-color: #f8fafc; padding: 25px 20px; border-top: 1px solid #e2e8f0; text-align: left;">
                <div style="text-align: center; font-size: 13px; color: #475569; margin-bottom: 25px; background-color: #e2e8f0; padding: 10px; border-radius: 8px;">
                    <strong>📌 Important:</strong> Please present this pass at the registration desk.
                </div>
                
                {instructions_html}
                
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin-top: 20px; border-radius: 0 8px 8px 0;">
                    <h4 style="margin: 0 0 5px 0; color: #991b1b; font-size: 14px;">📝 Note (Mandatory)</h4>
                    <p style="margin: 0; font-size: 12px; color: #7f1d1d; line-height: 1.5;">Submission of the Feedback Form after the event is mandatory to receive your Participation Certificate.</p>
                </div>
            </div>
        </div>

        <div style="max-width: 450px; margin: 30px auto 0 auto; text-align: center; font-size: 13px; color: #64748b; line-height: 1.5;">
            <p style="margin: 0;">Warm regards,<br/><strong style="color: #334155;">Organizing Committee</strong></p>
            <p style="margin: 5px 0 0 0;">INAE Technology Conclave 2026<br/>SIKSHA ‘O’ ANUSANDHAN (Deemed to be University)</p>
        </div>
      </body>
    </html>
    """

    # Generate the QR code image ONCE per participant
    qr_bytes = generate_qr_bytes(uid)
    
    # Try sending with each account in the list until one succeeds
    for i, account in enumerate(SMTP_ACCOUNTS):
        # We MUST create a fresh EmailMessage for each attempt to avoid duplicate attachments or errors
        msg = EmailMessage()
        msg["Subject"] = f"Your {pass_type} – INAE Technology Conclave 2026"
        msg["From"] = f"AIC SOA <{account['sender']}>"
        msg["To"] = to_email
        msg.set_content(plain_text_content)
        msg.add_alternative(html_content, subtype="html")
        msg.add_attachment(qr_bytes, maintype='image', subtype='png', filename=f'AIC_QR_{uid}.png', cid="<qr_image>")

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if SMTP_PORT in (587, 2525):
                    server.starttls()
                server.login(account["email"], account["password"])
                server.send_message(msg)
                print(f"[SUCCESS] Successfully sent QR to {to_email} using Account {i+1} ({account['email']})")
                return # Exit the function, success!
                
        except smtplib.SMTPException as e:
            print(f"[WARNING] Account {i+1} ({account['email']}) failed (Limit reached or bad credentials): {e}")
            if i < len(SMTP_ACCOUNTS) - 1:
                print(f"[RETRY] Switching to Account {i+2}...")
            else:
                print(f"[ERROR] CRITICAL ERROR: All {len(SMTP_ACCOUNTS)} accounts failed for {to_email}.")
                
        except OSError as oe:
            # Handle Render firewall blocked ports
            print(f"Port {SMTP_PORT} blocked. Retrying on fallback port 2525 for Account {i+1}...")
            try:
                with smtplib.SMTP(SMTP_SERVER, 2525) as server:
                    server.starttls()
                    server.login(account["email"], account["password"])
                    server.send_message(msg)
                    print(f"[SUCCESS] Sent QR to {to_email} using Account {i+1} on fallback port 2525")
                    return
            except Exception as e2:
                print(f"[WARNING] Account {i+1} failed on fallback port: {e2}")
                if i < len(SMTP_ACCOUNTS) - 1:
                    print(f"[RETRY] Switching to Account {i+2}...")
                else:
                    print(f"[ERROR] CRITICAL ERROR: All {len(SMTP_ACCOUNTS)} accounts failed for {to_email}.")
