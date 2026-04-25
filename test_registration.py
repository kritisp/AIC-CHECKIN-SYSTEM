import requests
import time

# Change this to your live Render URL if testing production
BACKEND_URL = "http://127.0.0.1:8000/register" 

# 👉 YOUR EMAIL GOES HERE so you can receive the test emails!
TEST_EMAIL = "kspchimun@gmail.com" 

def run_tests():
    print("🚀 Starting local registration tests...")
    
    # 1. Test Student Flow
    print("\n[Test 1] Simulating 'Student' Form Submission...")
    student_payload = {
        "name": "Student Tester",
        "email": TEST_EMAIL,
        "phone": "1234567890",
        "role": "Student",
        "college": "SOA University",
        "registration_number": "ITER1234"
    }
    
    try:
        resp = requests.post(BACKEND_URL, json=student_payload)
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect. Is the local server running (uvicorn main:app --reload)?")
        return

    # Sleep so we don't spam the email server too fast
    time.sleep(2)

    # 2. Test Delegate Flow
    print("\n[Test 2] Simulating 'Academician/Delegate' Form Submission...")
    
    # Use Gmail's + trick so it sends to your real inbox but counts as a new email
    email_parts = TEST_EMAIL.split("@")
    delegate_email = f"{email_parts[0]}+delegate@{email_parts[1]}"
    
    delegate_payload = {
        "name": "Delegate Tester",
        "email": delegate_email,
        "phone": "0987654321",
        "role": "Academician",
        "college": "Tech Institute",
        "registration_number": ""
    }
    
    try:
        resp = requests.post(BACKEND_URL, json=delegate_payload)
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if TEST_EMAIL == "your-email@example.com":
        print("⚠️ Please edit this file and change TEST_EMAIL to your actual email address before running!")
    else:
        run_tests()
