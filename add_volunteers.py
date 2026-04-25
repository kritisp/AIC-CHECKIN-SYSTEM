from auth_utils import hash_password
from supabase_client import supabase

def setup_users():
    # Lists of new users, their passwords, and their roles
    groups = [
        {
            "users": ["volunteer4", "volunteer5", "volunteer6", "volunteer7"],
            "password": "volunteer123",
            "role": "volunteer"
        },
        {
            "users": ["admin2", "admin3"],
            "password": "admin123",
            "role": "admin"
        }
    ]

    for group in groups:
        print(f"--- Processing {group['role'].upper()} Accounts ---")
        hashed_password = hash_password(group["password"])
        
        for username in group["users"]:
            # Check if the user already exists
            existing = supabase.table("users").select("id").eq("username", username).execute()
            
            if existing.data:
                print(f"[SKIPPING] {username} already exists.")
                continue
                
            row = {
                "username": username,
                "password_hash": hashed_password,
                "role": group["role"],
                "active": True
            }
            
            # Insert them into the 'users' table
            supabase.table("users").insert(row).execute()
            print(f"Successfully added {username}!")

    print("\nAll new accounts have been freshly injected into Supabase!")

if __name__ == "__main__":
    setup_users()
