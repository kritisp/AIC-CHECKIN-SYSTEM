import csv
import requests
import time

# -----------------------------------------------------------------------------------------
# HOW TO USE:
# 1. Export your Google Form responses as a CSV file and save it in this same folder.
# 2. Rename that CSV file to 'existing_users.csv'. 
# 3. We will read the CSV and send them one-by-one to your live backend.
# -----------------------------------------------------------------------------------------

CSV_FILE_PATH = "existing_users.csv"
BACKEND_URL = "https://aic-checkin-system.onrender.com/register"

def import_users():
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Print the columns found to help debug if names don't match
            print(f"Found columns in CSV: {reader.fieldnames}")
            
            success_count = 0
            
            for row in reader:
                # IMPORTANT: Update these keys to exactly match your CSV column headers
                # Look at the first row of your CSV to see exactly what they are called.
                name = row.get("Full Name", "")
                email = row.get("Email Address", "") or row.get("Email ID", "")
                phone = row.get("Mobile Number", "")
                college = row.get("Institute Name", "") or row.get("Organisation Name", "")
                reg_num = row.get("Registration Number (for Students)", "")
                role = "participant"
                
                if not email:
                    continue # Skip empty rows
                
                payload = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "college": college,
                    "role": role,
                    "registration_number": reg_num
                }
                
                print(f"Sending {email}...")
                response = requests.post(BACKEND_URL, json=payload)
                
                if response.status_code == 200 or response.status_code == 201:
                    print(f"  [SUCCESS] -> Added to Supabase & Email sent to {email}")
                    success_count += 1
                elif response.status_code == 409:
                    print(f"  [SKIPPED] -> {email} is already in Supabase")
                else:
                    print(f"  [FAILED] -> {email} Error: {response.text}")
                
                # Sleep briefly to avoid overwhelming the server
                time.sleep(1)
                
            print(f"\nDone! Successfully imported {success_count} users.")
            
    except FileNotFoundError:
        print(f"Error: Could not find the file '{CSV_FILE_PATH}'. Please ensure it is in this folder.")

if __name__ == "__main__":
    import_users()
