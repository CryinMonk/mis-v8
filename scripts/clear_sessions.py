import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.db_connection import AuthDatabase
from app.models import UserSession
from app.utils.logger import Logger


def clear_active_sessions():
    """Clear all active sessions from the database"""
    logger = Logger()
    logger.info("Starting session cleanup")

    # Initialize database connection
    try:
        db = AuthDatabase()
        db_session = db.get_session()

        # Count active sessions
        active_count = db_session.query(UserSession).filter(UserSession.is_active == True).count()
        logger.info(f"Found {active_count} active sessions")

        if active_count > 0:
            # Update all active sessions to inactive
            db_session.query(UserSession).filter(UserSession.is_active == True).update(
                {UserSession.is_active: False},
                synchronize_session='fetch'
            )
            db_session.commit()
            logger.info(f"Successfully deactivated {active_count} sessions")

        # Close the session
        db_session.close()

        print(f"Successfully cleared {active_count} active sessions")
        return True

    except Exception as e:
        logger.error(f"Error clearing sessions: {str(e)}")
        print(f"Error clearing sessions: {str(e)}")
        return False


if __name__ == "__main__":
    print("Clearing all active sessions...")
    clear_active_sessions()
    print("Done.")