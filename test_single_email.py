from email_service import send_qr_email

def test_email():
    try:
        print("Sending test email to kspchimun@gmail.com...")
        send_qr_email("kspchimun@gmail.com", "Test Student", "TEST-STU-456", "student")
        print("Test email function executed.")
    except Exception as e:
        print(f"Error during email send: {e}")

if __name__ == "__main__":
    test_email()
