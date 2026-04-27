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
            reader = csv.reader(file)
            headers = next(reader)
            print(f"Found headers in CSV: {headers}")
            
            success_count = 0
            
            for row in reader:
                if not row or len(row) < 5:
                    continue
                    
                # Based on the CSV structure:
                # 0: Timestamp, 1: Email Address, 2: Full Name, 3: Mobile Number, 4: Email ID
                # 5: Select your Profession
                # 6: Institute (Student), 7: Dept, 8: Reg Num
                # 9: Designation, 10: Institute (Academician), 11: Dept
                # 12: Designation, 13: Organisation (Industrialist), 14: Dept
                # 15: Organisation (Others)
                
                name = row[2].strip() if len(row) > 2 else ""
                email = row[4].strip() if len(row) > 4 and row[4].strip() else (row[1].strip() if len(row) > 1 else "")
                phone = row[3].strip() if len(row) > 3 else ""
                role = row[5].strip() if len(row) > 5 else "Delegate"
                reg_num = row[8].strip() if len(row) > 8 else ""
                
                # Find the college/organisation by checking all possible columns
                college = ""
                for idx in [6, 10, 13, 15]:
                    if len(row) > idx and row[idx].strip():
                        college = row[idx].strip()
                        break
                
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
