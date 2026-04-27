from auth_utils import hash_password
from supabase_client import supabase

def setup_users():
    # Lists of users to ensure they have the exact known password
    groups = [
        {
            "users": ["admin", "admin2"],
            "password": "admin123",
            "role": "admin"
        },
        {
            "users": ["volunteer1", "volunteer2", "volunteer3", "volunteer4", "volunteer5", "volunteer6"],
            "password": "volunteer123",
            "role": "volunteer"
        }
    ]

    for group in groups:
        print(f"--- Processing {group['role'].upper()} Accounts ---")
        hashed_password = hash_password(group["password"])
        
        for username in group["users"]:
            row = {
                "username": username,
                "password_hash": hashed_password,
                "role": group["role"],
                "active": True
            }
            
            # UPSERT them into the 'users' table
            supabase.table("users").upsert(row, on_conflict="username").execute()
            print(f"Successfully updated/added {username} with the new password!")

    print("\nAll accounts have been freshly updated in Supabase!")

if __name__ == "__main__":
    setup_users()
