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
- We kindly request you to arrive at least 30 minutes early to ensure a smooth check-in.
- Our volunteer team will be happy to assist you throughout the event.
- We appreciate your cooperation in maintaining a professional atmosphere during all sessions.
"""
        instructions_html = """
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #1a365d; font-size: 16px;">📌 Helpful Guidelines</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #475569; line-height: 1.6;">
                        <li>We kindly request you to arrive <strong>at least 30 minutes early</strong> to ensure a smooth check-in process.</li>
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
- Registration desks will be open 30 minutes prior to the event for a seamless check-in experience.
- Dedicated help desks will be available at the venue to assist you.
"""
        instructions_html = """
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #1a365d; font-size: 16px;">ℹ️ Event Information</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #475569; line-height: 1.6;">
                        <li>Registration desks will be open 30 minutes prior to the event for a seamless check-in experience.</li>
                        <li>Dedicated help desks will be available at the venue to assist you.</li>
                    </ul>
                </div>
"""

    # Plain text fallback
    plain_text_content = f"""
Dear {name},

Greetings from SIKSHA ‘O’ ANUSANDHAN (Deemed to be University) and AIC–SOA Foundation.

We are pleased to confirm your participation in the National Conclave on Cyber Security, AI & Emerging Technologies, scheduled on 29th & 30th April 2026 at Auditorium, Campus–2, SOA University, Bhubaneswar.

🎟️ Your Entry Pass
Please find your QR Code attached. This will serve as your official entry pass for the event.
Category: {pass_type}
Your Entry ID: {uid}

📌 Important:
- Carry this QR code (printed or on your phone) for smooth entry
- Entry will be granted only after scanning at the registration desk

📅 Event Highlights
- Expert talks on Cyber Security, AI & Emerging Technologies
- Panel discussions with industry leaders
- Innovation showcases & networking opportunities

🕘 Reporting Details
- Date: 29th April 2026
- Reporting Time: 10:00 AM
- Venue: Auditorium, Campus–2, SOA University
{instructions_text}
📝 Note (Very Important)
- After the event, you will receive a Feedback Form
- Submission of the feedback form is mandatory
- 🎓 Participation Certificates will be issued only after completing the feedback form

We look forward to your presence at this prestigious conclave.
For any queries, feel free to contact the organizing team.

Warm regards,
Organizing Committee
National Conclave on Cyber Security, AI & Emerging Technologies
SIKSHA ‘O’ ANUSANDHAN (Deemed to be University)
Bhubaneswar, Odisha
"""

    # HTML Body: Boarding Pass Ticket Layout
    html_content = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f7f6; padding: 20px;">
        <div style="max-width: 700px; margin: 0 auto;">
            
            <p style="font-size: 16px; margin-top: 0;">Dear <strong>{name}</strong>,</p>
            <p style="font-size: 15px;">Greetings from <strong>SIKSHA ‘O’ ANUSANDHAN (Deemed to be University)</strong> and <strong>AIC–SOA Foundation</strong>.</p>
            <p style="font-size: 15px; margin-bottom: 25px;">We are pleased to confirm your participation in the <strong>National Conclave on Cyber Security, AI & Emerging Technologies</strong>.</p>

            <!-- BOARDING PASS TICKET -->
            <div style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; margin-bottom: 30px;">
                
                <!-- Ticket Header -->
                <div style="background-color: {theme_color}; padding: 15px 20px; color: #ffffff;">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td align="left" style="font-size: 18px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase;">
                                {pass_type}
                            </td>
                            <td align="right" style="font-size: 14px; font-weight: 500; opacity: 0.9;">
                                NATIONAL CONCLAVE '26
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- Ticket Body -->
                <div style="padding: 0;">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: {theme_bg};">
                        <tr>
                            <!-- Left Section: Details -->
                            <td width="70%" valign="top" style="padding: 25px; border-right: 2px dashed #cbd5e1;">
                                <div style="margin-bottom: 15px;">
                                    <span style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold;">Participant Name</span><br/>
                                    <strong style="font-size: 20px; color: #0f172a;">{name}</strong>
                                </div>
                                
                                <div style="margin-bottom: 15px;">
                                    <span style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold;">Category</span><br/>
                                    <strong style="font-size: 16px; color: {theme_color};">{role_display}</strong>
                                </div>

                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td width="50%" valign="top">
                                            <span style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold;">Date</span><br/>
                                            <strong style="font-size: 14px; color: #0f172a;">29 Apr 2026</strong>
                                        </td>
                                        <td width="50%" valign="top">
                                            <span style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold;">Reporting Time</span><br/>
                                            <strong style="font-size: 14px; color: #0f172a;">10:00 AM</strong>
                                        </td>
                                    </tr>
                                </table>
                                
                                <div style="margin-top: 15px;">
                                    <span style="font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold;">Venue</span><br/>
                                    <strong style="font-size: 14px; color: #0f172a;">Auditorium, Campus–2, SOA University</strong>
                                </div>
                            </td>
                            
                            <!-- Right Section: QR Code -->
                            <td width="30%" valign="middle" align="center" style="padding: 20px; background-color: #ffffff;">
                                <div style="font-size: 12px; color: #64748b; margin-bottom: 10px; text-transform: uppercase; font-weight: bold;">Official Entry Pass</div>
                                <img src="cid:qr_image" width="130" alt="QR Code" style="display: block; margin: 0 auto;"/>
                                <div style="margin-top: 10px; font-family: monospace; font-size: 14px; color: #334155; background-color: #f1f5f9; padding: 4px 8px; border-radius: 4px; display: inline-block;">{uid}</div>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <!-- Ticket Footer -->
                <div style="background-color: #f8fafc; padding: 12px 20px; text-align: center; font-size: 12px; color: #475569; border-top: 1px solid #e2e8f0;">
                    <strong>📌 Important:</strong> Please present this ticket (printed or digital) at the registration desk.
                </div>
            </div>

            <!-- Other details below the ticket -->
            <div style="background-color: #ffffff; border-radius: 12px; padding: 30px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #1a365d; font-size: 16px;">📅 Event Highlights</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #475569; line-height: 1.6;">
                        <li>Expert talks on Cyber Security, AI & Emerging Technologies</li>
                        <li>Panel discussions with industry leaders</li>
                        <li>Innovation showcases & networking opportunities</li>
                    </ul>
                </div>
{instructions_html}
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin-bottom: 30px;">
                    <h4 style="margin: 0 0 5px 0; color: #991b1b; font-size: 15px;">📝 Note (Mandatory)</h4>
                    <p style="margin: 0; font-size: 13px; color: #7f1d1d; line-height: 1.5;">After the event, you will receive a Feedback Form. Submission is mandatory to receive your Participation Certificate.</p>
                </div>

                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 25px 0;" />
                
                <div style="font-size: 14px; color: #334155; line-height: 1.5;">
                    <p style="margin: 0;">Warm regards,</p>
                    <p style="margin: 5px 0 0 0; font-weight: bold; font-size: 16px; color: #1a365d;">Organizing Committee</p>
                    <p style="margin: 0;">National Conclave on Cyber Security, AI & Emerging Technologies</p>
                    <p style="margin: 0;">SIKSHA ‘O’ ANUSANDHAN (Deemed to be University)</p>
                    <p style="margin: 0;">Bhubaneswar, Odisha</p>
                </div>
            </div>
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
        msg["Subject"] = f"Your {pass_type} – National Conclave on Cyber Security, AI & Emerging Technologies"
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
                print(f"✅ Successfully sent QR to {to_email} using Account {i+1} ({account['email']})")
                return # Exit the function, success!
                
        except smtplib.SMTPException as e:
            print(f"⚠️ Account {i+1} ({account['email']}) failed (Limit reached or bad credentials): {e}")
            if i < len(SMTP_ACCOUNTS) - 1:
                print(f"🔄 Switching to Account {i+2}...")
            else:
                print(f"❌ CRITICAL ERROR: All {len(SMTP_ACCOUNTS)} accounts failed for {to_email}.")
                
        except OSError as oe:
            # Handle Render firewall blocked ports
            print(f"Port {SMTP_PORT} blocked. Retrying on fallback port 2525 for Account {i+1}...")
            try:
                with smtplib.SMTP(SMTP_SERVER, 2525) as server:
                    server.starttls()
                    server.login(account["email"], account["password"])
                    server.send_message(msg)
                    print(f"✅ Sent QR to {to_email} using Account {i+1} on fallback port 2525")
                    return
            except Exception as e2:
                print(f"⚠️ Account {i+1} failed on fallback port: {e2}")
                if i < len(SMTP_ACCOUNTS) - 1:
                    print(f"🔄 Switching to Account {i+2}...")
                else:
                    print(f"❌ CRITICAL ERROR: All {len(SMTP_ACCOUNTS)} accounts failed for {to_email}.")
