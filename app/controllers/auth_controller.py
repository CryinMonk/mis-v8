import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import func

from app.models import User, LoginAttempt
from app.config.config import Config
from app.services.session_manager import SessionManager


class AuthController:
    """Controller for handling authentication"""

    def __init__(self, db_session):
        self.db_session = db_session
        self.config = Config()
        self.session_manager = SessionManager(db_session)

    def authenticate(self, username, password, ip_address=None, user_agent=None):
        """
        Authenticate a user

        Args:
            username: Username to authenticate
            password: Password to verify
            ip_address: IP address of client (optional)
            user_agent: User agent of client (optional)

        Returns:
            Tuple of (user, session, message)
            If authentication fails, user and session will be None
        """
        # Check for too many login attempts from this IP in the past hour
        if ip_address:
            # Fixed: use correct datetime import and convert to naive for MySQL compatibility
            one_hour_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1)
            attempt_count = self.db_session.query(func.count(LoginAttempt.id)).filter(
                LoginAttempt.ip_address == ip_address,
                LoginAttempt.timestamp >= one_hour_ago
            ).scalar()

            if attempt_count >= 100:
                return None, None, "Invalid username or password"

        # Record login attempt
        login_attempt = LoginAttempt(
            username=username,
            ip_address=ip_address,
            successful=False
        )

        try:
            # Find user
            user = self.db_session.query(User).filter(User.username == username).first()

            # Check if user exists and is active
            if not user:
                self.db_session.add(login_attempt)
                self.db_session.commit()
                return None, None, "Invalid username or password"

            if not user.is_active:
                self.db_session.add(login_attempt)
                self.db_session.commit()
                return None, None, "Account is disabled"

            # Check password
            if not user.check_password(password):
                self.db_session.add(login_attempt)
                self.db_session.commit()
                return None, None, "Invalid username or password"

            # Use SessionManager to create a new session
            session, session_message = self.session_manager.create_session(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )

            if not session:
                # Session creation failed
                self.db_session.add(login_attempt)
                self.db_session.commit()
                return None, None, session_message

            # Update login attempt
            login_attempt.successful = True
            login_attempt.user_id = user.id

            # Save login attempt to database
            self.db_session.add(login_attempt)
            self.db_session.commit()

            return user, session, "Authentication successful"

        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Authentication error: {str(e)}")
            return None, None, f"Authentication error: {str(e)}"

    def logout(self, session_token):
        """
        End an active user session

        Args:
            session_token: The token of the session to end

        Returns:
            Tuple of (success, message)
        """
        return self.session_manager.end_session(session_token)

    def validate_session(self, session_token):
        """
        Validate if a session is active and not expired

        Args:
            session_token: The token of the session to validate

        Returns:
            Tuple of (is_valid, user, message)
        """
        user, message = self.session_manager.validate_session(session_token)
        is_valid = user is not None
        return is_valid, user, message

    def cleanup_expired_sessions(self):
        """
        Clean up expired sessions

        Returns:
            Number of sessions deactivated
        """
        return self.session_manager.cleanup_expired_sessions()