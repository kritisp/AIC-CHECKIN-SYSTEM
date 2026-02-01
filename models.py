from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    college = Column(String)
    role = Column(String)
    checked_in = Column(Boolean, default=False)
    qr_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    checkin_time = Column(DateTime)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    active = Column(Boolean, default=True)
