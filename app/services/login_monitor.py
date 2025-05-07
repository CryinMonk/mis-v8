from datetime import datetime, timedelta

from app.models.session import LoginAttempt
from app.config.config import Config


class LoginMonitor:
    def __init__(self, db_session):
        self.db_session = db_session
        self.config = Config()

    def record_attempt(self, username, ip_address=None, successful=False, user=None):
        # Create login attempt record
        attempt = LoginAttempt(
            username=username,
            ip_address=ip_address,
            successful=successful,
            user_id=user.id if user else None
        )

        self.db_session.add(attempt)
        self.db_session.commit()

    def is_account_locked(self, username):
        # Get config values
        max_attempts = self.config.max_failed_attempts
        lockout_duration = timedelta(minutes=self.config.lockout_duration)

        # Calculate time threshold
        time_threshold = datetime.utcnow() - lockout_duration

        # Count failed attempts within the lockout window
        failed_attempts = self.db_session.query(LoginAttempt).filter(
            LoginAttempt.username == username,
            LoginAttempt.successful == False,
            LoginAttempt.timestamp >= time_threshold
        ).count()

        return failed_attempts >= max_attempts

    def get_failed_attempts(self, username):
        # Calculate time threshold (last 24 hours)
        time_threshold = datetime.utcnow() - timedelta(days=1)

        # Count failed attempts
        failed_attempts = self.db_session.query(LoginAttempt).filter(
            LoginAttempt.username == username,
            LoginAttempt.successful == False,
            LoginAttempt.timestamp >= time_threshold
        ).count()

        return failed_attempts