from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
# import os
# import base64
import secrets
from app.models.base import Base
# from app.models.user import User


class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    # For MySQL, we use naive datetimes in UTC
    # The default function converts timezone-aware datetime to naive UTC
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Define the relationship to User
    user = relationship("User", backref="sessions")

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)


class LoginAttempt(Base):
    __tablename__ = 'login_attempts'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    successful = Column(Boolean, default=False)

    # For MySQL, we use naive datetimes in UTC
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relationship with User
    user = relationship("User")