from datetime import datetime, timezone, timedelta
from sqlalchemy import func, and_
from sqlalchemy import exc as sqlalchemy_exc
import logging

from app.models.session import UserSession
from app.models.user import User
from app.config.config import Config


class SessionManager:
    """Manager for handling user sessions and session-related operations"""

    def __init__(self, db_session):
        self.db_session = db_session
        config = Config()
        self.session_timeout = timedelta(hours=config.session_timeout)
        self.max_concurrent_sessions = {
            'admin': 1,
            'data_warehouse': 1,
            'teacher': 1,
            'supervisor': 1
        }
        self.config = config

    def create_session(self, user, ip_address=None, user_agent=None):
        """
        Create a new session for a user

        Args:
            user: User object for whom to create session
            ip_address: IP address of client (optional)
            user_agent: User agent of client (optional)

        Returns:
            Tuple of (session, message)
        """
        try:
            # Check concurrent sessions limit
            active_sessions = self._get_active_sessions_count(user.role.value)
            if active_sessions >= self.max_concurrent_sessions.get(user.role.value, 1):
                return None, "Maximum concurrent sessions reached for this role."

            # Deactivate all existing sessions for this user
            self._deactivate_existing_sessions(user.id)

            # Get current time as naive UTC for MySQL storage
            current_time = datetime.now(timezone.utc).replace(tzinfo=None)

            # Create new session
            new_session = UserSession(
                user_id=user.id,
                session_token=UserSession.generate_token(),
                ip_address=ip_address,
                user_agent=user_agent,
                is_active=True,
                created_at=current_time,
                last_activity=current_time
            )

            # Update user's last login time
            user.last_login = current_time

            # Format timestamp for config update
            timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            # Update config with last login info if user is authenticated
            if hasattr(user, 'username'):
                self.config.update_last_login(user.username, timestamp_str)

            self.db_session.add(new_session)
            self.db_session.commit()

            return new_session, "Session created successfully."

        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Session creation error: {str(e)}")
            return None, f"Session creation error: {str(e)}"

    def _deactivate_existing_sessions(self, user_id):
        """
        Deactivate all existing sessions for a user

        Args:
            user_id: ID of the user whose sessions to deactivate
        """
        active_sessions = self.db_session.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()

        for existing_session in active_sessions:
            existing_session.is_active = False

    def validate_session(self, session_token):
        """
        Validate if a session is active and not expired

        Args:
            session_token: The token of the session to validate

        Returns:
            Tuple of (user, message)
        """
        try:
            # Find session
            session = self.db_session.query(UserSession).filter(
                UserSession.session_token == session_token,
                UserSession.is_active == True
            ).first()

            if not session:
                return None, "Session not found or inactive"

            # Check if session has expired
            if self._is_session_expired(session):
                session.is_active = False
                self.db_session.commit()
                return None, "Session expired"

            # Get user
            user = self.db_session.query(User).filter(User.id == session.user_id).first()

            if not user or not user.is_active:
                session.is_active = False
                self.db_session.commit()
                return None, "User not found or inactive"

            # Update last activity time - naive UTC for MySQL
            session.last_activity = datetime.now(timezone.utc).replace(tzinfo=None)
            self.db_session.commit()

            return user, "Session valid"

        except Exception as e:
            logging.error(f"Session validation error: {str(e)}")
            return None, f"Session validation error: {str(e)}"

    def _is_session_expired(self, session):
        """
        Helper method to determine if a session is expired

        Args:
            session: The session to check

        Returns:
            Boolean indicating whether the session is expired
        """
        # Get current time as naive UTC for MySQL
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)

        # Since we're using naive datetimes, we can compare directly
        session_age = current_time - session.last_activity
        return session_age > self.session_timeout

    def end_session(self, session_token):
        """
        End an active user session

        Args:
            session_token: The token of the session to end

        Returns:
            Tuple of (success, message)
        """
        try:
            # Find session
            session = self.db_session.query(UserSession).filter(
                UserSession.session_token == session_token
            ).first()

            if not session:
                return False, "Session not found"

            if not session.is_active:
                return False, "Session already ended"

            # End session
            session.is_active = False
            self.db_session.commit()

            return True, "Session ended successfully"

        except Exception as e:
            self.db_session.rollback()
            logging.error(f"Session ending error: {str(e)}")
            return False, f"Session ending error: {str(e)}"

    def _get_active_sessions_count(self, role):
        """
        Get count of active sessions for a specific role

        Args:
            role: Role to count sessions for

        Returns:
            Count of active non-expired sessions
        """
        # Get current time as naive UTC for MySQL
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        comparison_time = current_time - self.session_timeout

        return self.db_session.query(func.count(UserSession.id)).join(User).filter(
            and_(
                User.role == role,
                UserSession.is_active == True,
                UserSession.last_activity >= comparison_time
            )
        ).scalar()

    def cleanup_expired_sessions(self):
        """
        Clean up expired sessions using an optimized database query

        Returns:
            Number of sessions deactivated
        """
        try:
            # Calculate expiration threshold - naive UTC for MySQL
            current_time = datetime.now(timezone.utc).replace(tzinfo=None)
            expiration_time = current_time - self.session_timeout

            # Use direct SQL update for better performance
            result = self.db_session.query(UserSession).filter(
                UserSession.is_active == True,
                UserSession.last_activity < expiration_time
            ).update({"is_active": False}, synchronize_session=False)

            self.db_session.commit()
            return result

        except sqlalchemy_exc.SQLAlchemyError as e:
            # Handle database-specific errors
            self.db_session.rollback()
            error_message = f"Database error during session cleanup: {str(e)}"
            logging.error(error_message)
            return 0

        except Exception as e:
            # Still have a catch-all as last resort, but with better logging
            self.db_session.rollback()
            error_message = f"Unexpected error during session cleanup: {str(e)}, Type: {type(e).__name__}"
            logging.error(error_message)
            return 0