from fastapi import FastAPI, HTTPException
from datetime import datetime
from supabase_client import supabase
from utils import generate_uid
from qr_service import generate_qr
from auth_utils import verify_password
from jwt_utils import create_access_token
from auth_dependency import get_current_user, require_role
from fastapi import Depends


app = FastAPI(title="AIC Check-in System")

# --------------------------------------------------
# BASIC HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.get("/test-db")
def test_db():
    res = supabase.table("participants").select("id").limit(1).execute()
    return {"ok": True, "data": res.data}

# --------------------------------------------------
# REGISTRATION (USED BY GOOGLE FORM)
# --------------------------------------------------

@app.post("/register")
def register_participant(payload: dict):
    name = payload.get("name")
    email = payload.get("email")
    phone = payload.get("phone")
    college = payload.get("college")
    role = payload.get("role")

    if not name or not email or not role:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # 1. Prevent duplicate registration
    existing = (
        supabase
        .table("participants")
        .select("id")
        .eq("email", email)
        .execute()
    )

    if existing.data:
        raise HTTPException(status_code=409, detail="Email already registered")

    # 2. Generate unique ID
    uid = generate_uid()

    # 3. Generate QR code
    qr_path = generate_qr(uid)

    # 4. Insert participant into DB
    data = {
        "uid": uid,
        "name": name,
        "email": email,
        "phone": phone,
        "college": college,
        "role": role,
        "checked_in": False,
        "qr_path": qr_path,
        "created_at": datetime.utcnow().isoformat()
    }

    supabase.table("participants").insert(data).execute()

    return {
        "success": True,
        "uid": uid,
        "qr_path": qr_path,
        "message": "Registration successful"
    }

# --------------------------------------------------
# SCAN QR (READ-ONLY, NO CHECK-IN)
# --------------------------------------------------
@app.post("/scan")
def scan_participant(
    payload: dict,
    user=Depends(get_current_user)  # volunteer OR admin
):
    uid = payload.get("uid")

    if not uid:
        raise HTTPException(status_code=400, detail="UID is required")

    res = (
        supabase
        .table("participants")
        .select(
            "uid, name, email, phone, college, role, checked_in, checkin_time"
        )
        .eq("uid", uid)
        .execute()
    )

    if not res.data:
        return {
            "valid": False,
            "message": "Invalid QR code"
        }

    participant = res.data[0]

    return {
        "valid": True,
        "already_checked_in": participant["checked_in"],
        "participant": {
            "uid": participant["uid"],
            "name": participant["name"],
            "email": participant["email"],
            "phone": participant["phone"],
            "college": participant["college"],
            "role": participant["role"]
        },
        "checkin_time": participant["checkin_time"]
    }


# --------------------------------------------------
# CONFIRM CHECK-IN (AFTER VOLUNTEER APPROVAL)
# --------------------------------------------------
@app.post("/checkin")
def confirm_checkin(
    payload: dict,
    user=Depends(get_current_user)  # volunteer OR admin
):
    uid = payload.get("uid")

    if not uid:
        raise HTTPException(status_code=400, detail="UID is required")

    res = (
        supabase
        .table("participants")
        .select("checked_in")
        .eq("uid", uid)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Invalid QR code")

    participant = res.data[0]

    if participant["checked_in"]:
        return {
            "status": "already_checked_in",
            "message": "Participant already checked in"
        }

    supabase.table("participants").update({
        "checked_in": True,
        "checkin_time": datetime.utcnow().isoformat()
    }).eq("uid", uid).execute()

    return {
        "status": "checked_in",
        "message": "Check-in successful"
    }


@app.post("/login")
def login(payload: dict):
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    # Fetch user
    res = (
        supabase
        .table("users")
        .select("username, password_hash, role, active")
        .eq("username", username)
        .limit(1)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user = res.data[0]

    if not user["active"]:
        raise HTTPException(status_code=403, detail="User is disabled")

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT
    token = create_access_token({
        "username": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "role": user["role"]
    }

@app.get("/stats")
def get_stats(user=Depends(require_role("admin"))):
    # Total registrations
    total_res = (
        supabase
        .table("participants")
        .select("id", count="exact")
        .execute()
    )
    total = total_res.count or 0

    # Checked-in count
    checked_res = (
        supabase
        .table("participants")
        .select("id", count="exact")
        .eq("checked_in", True)
        .execute()
    )
    checked_in = checked_res.count or 0

    # Pending
    pending = total - checked_in

    # Role-wise breakdown
    role_res = (
        supabase
        .table("participants")
        .select("role")
        .execute()
    )

    role_counts = {}
    for r in role_res.data:
        role = r.get("role", "unknown")
        role_counts[role] = role_counts.get(role, 0) + 1

    # Recent check-ins (last 10)
    recent_res = (
        supabase
        .table("participants")
        .select("name, email, role, checkin_time")
        .eq("checked_in", True)
        .order("checkin_time", desc=True)
        .limit(10)
        .execute()
    )

    return {
        "total_registrations": total,
        "checked_in": checked_in,
        "pending": pending,
        "role_breakdown": role_counts,
        "recent_checkins": recent_res.data
    }

