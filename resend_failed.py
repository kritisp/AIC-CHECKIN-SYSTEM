import csv
import time
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Import your own local email_service functions!
from email_service import send_qr_email

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: Missing Supabase credentials in .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Point this to whatever CSV you want to force-resend to.
CSV_FILE_PATH = "resend_users.csv"

def force_resend_emails():
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"Reading {CSV_FILE_PATH} to forcefully resend emails...")
            
            success_count = 0
            
            for row in reader:
                name = row.get("Full Name", "")
                email = row.get("Email Address", "") or row.get("Email ID", "")
                
                if not email:
                    continue
                
                # Check Supabase to retrieve their existing Entry ID (UID)
                print(f"Looking up {email} in Supabase...")
                response = supabase.table("participants").select("uid").eq("email", email).execute()
                
                if len(response.data) > 0:
                    uid = response.data[0]["uid"]
                    print(f"  -> Found! UID is {uid}. Force sending email now via your NEW Brevo account...")
                    
                    # Because we are running this locally, it uses your updated .env with the new Brevo account!
                    send_qr_email(email, name, uid)
                    success_count += 1
                else:
                    print(f"  [ERROR] -> {email} is NOT in Supabase. You must use import_existing.py for them first.")
                
                time.sleep(1) # Sleep to respect Brevo's speed limits
                
            print(f"\nDone! Successfully force-resent emails to {success_count} people.")
            
    except FileNotFoundError:
        print(f"Error: Could not find the file '{CSV_FILE_PATH}'. Please ensure it is in this folder.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    force_resend_emails()
