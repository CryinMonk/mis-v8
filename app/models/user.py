from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
import bcrypt

from app.models.base import Base


class UserRole(enum.Enum):
    ADMIN = "admin"
    DATA_WAREHOUSE = "data_warehouse"
    TEACHER = "teacher"
    SUPERVISOR = "supervisor"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)

    # Update datetime default to use timezone-aware UTC datetime
    # then strip timezone for MySQL compatibility
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_login = Column(DateTime, nullable=True)

    # Relationship will be defined later using backref

    def set_password(self, password):
        """Set the user's password by generating a salt and hashing the password"""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.salt = salt.decode('utf-8')
        self.password_hash = password_hash.decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), self.salt.encode('utf-8'))
        return password_hash.decode('utf-8') == self.password_hash

    @classmethod
    def get_current_time_utc(cls):
        """
        Class method to get current UTC time in the format required for MySQL

        Returns:
            datetime: Current UTC time without timezone info for MySQL compatibility
        """
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def update_last_login(self):
        """Update the user's last login time to the current time"""
        self.last_login = self.get_current_time_utc()