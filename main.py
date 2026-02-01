from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.orm import Session

from database import get_db
from models import Participant, User
from utils import generate_uid
from auth_utils import verify_password
from jwt_utils import create_access_token
from auth_dependency import get_current_user, require_role


app = FastAPI(title="AIC Check-in System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://aic-checkin-system.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# BASIC HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "Backend running (PostgreSQL)"}


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    count = db.query(Participant).count()
    return {"ok": True, "participants": count}


# --------------------------------------------------
# REGISTRATION (USED BY GOOGLE FORM)
# --------------------------------------------------

@app.post("/register")
def register_participant(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    existing = db.query(Participant).filter(
        Participant.email == email
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    uid = generate_uid()

    participant = Participant(
        uid=uid,
        name=payload.get("name"),
        email=email,
        phone=payload.get("phone"),
        college=payload.get("college"),
        role=payload.get("role"),
        checked_in=False,
        created_at=datetime.utcnow()
    )

    db.add(participant)
    db.commit()
    db.refresh(participant)

    return {
        "success": True,
        "uid": uid,
        "message": "Registration successful. QR will be sent via email."
    }


# --------------------------------------------------
# SCAN QR (READ-ONLY)
# --------------------------------------------------

@app.post("/scan")
def scan_participant(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    uid = payload.get("uid")

    if not uid:
        raise HTTPException(status_code=400, detail="UID is required")

    participant = db.query(Participant).filter(
        Participant.uid == uid
    ).first()

    if not participant:
        return {"valid": False, "message": "Invalid QR code"}

    return {
        "valid": True,
        "already_checked_in": participant.checked_in,
        "participant": {
            "uid": participant.uid,
            "name": participant.name,
            "email": participant.email,
            "phone": participant.phone,
            "college": participant.college,
            "role": participant.role
        },
        "checkin_time": (
            participant.checkin_time.isoformat()
            if participant.checkin_time else None
        )
    }


# --------------------------------------------------
# CONFIRM CHECK-IN
# --------------------------------------------------

@app.post("/checkin")
def confirm_checkin(
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    uid = payload.get("uid")

    if not uid:
        raise HTTPException(status_code=400, detail="UID is required")

    participant = db.query(Participant).filter(
        Participant.uid == uid
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Invalid QR code")

    if participant.checked_in:
        return {
            "status": "already_checked_in",
            "message": "Participant already checked in"
        }

    participant.checked_in = True
    participant.checkin_time = datetime.utcnow()

    db.commit()

    return {
        "status": "checked_in",
        "message": "Check-in successful"
    }


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user.active:
        raise HTTPException(status_code=403, detail="User is disabled")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({
        "username": user.username,
        "role": user.role
    })

    return {
        "access_token": token,
        "role": user.role
    }


# --------------------------------------------------
# ADMIN STATS
# --------------------------------------------------

@app.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin"))
):
    total = db.query(Participant).count()
    checked_in = db.query(Participant).filter(
        Participant.checked_in == True
    ).count()

    pending = total - checked_in

    role_counts = {}
    for r in db.query(Participant.role).all():
        role = r[0] or "unknown"
        role_counts[role] = role_counts.get(role, 0) + 1

    recent = (
        db.query(Participant)
        .filter(Participant.checked_in == True)
        .order_by(Participant.checkin_time.desc())
        .limit(10)
        .all()
    )

    return {
        "total_registrations": total,
        "checked_in": checked_in,
        "pending": pending,
        "role_breakdown": role_counts,
        "recent_checkins": [
            {
                "name": p.name,
                "email": p.email,
                "role": p.role,
                "checkin_time": p.checkin_time.isoformat()
            }
            for p in recent
        ]
    }
