import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymysql
import json
from app.config.config import Config
from app.utils.logger import Logger


# We need to use direct imports instead of from the initialized Config
# since we're updating the config structure
def get_config_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')


def update_config_structure():
    """Update the config.json structure if needed"""
    config_path = get_config_path()

    # Create default config if it doesn't exist
    if not os.path.exists(config_path):
        from app.config.config import Config
        # The constructor will create a default config file
        Config()
        return True

    try:
        # Load existing config
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Check if config needs updating
        needs_update = False

        # If old database structure exists, migrate to new structure
        if 'database' in config and 'auth_database' not in config:
            # Copy database settings to auth_database
            config['auth_database'] = config['database'].copy()

            # Create data_database with pwd_students_db as database name
            config['data_database'] = config['database'].copy()
            config['data_database']['database'] = 'pwd_students_db'

            # Keep original database key for backward compatibility
            needs_update = True

        # Add user_info if it doesn't exist
        if 'user_info' not in config:
            config['user_info'] = {
                "last_login": "admin",
                "last_login_time": "2025-04-26 07:34:53"
            }
            needs_update = True

        # Save the updated config if changes were made
        if needs_update:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            print("Config structure updated")
            return True

        return True
    except Exception as e:
        print(f"Error updating config structure: {str(e)}")
        return False


def create_database_if_not_exists():
    """Create the authentication database if it doesn't exist yet"""
    # Make sure config is updated first
    if not update_config_structure():
        return False

    # Now load the updated config
    config_path = get_config_path()
    with open(config_path, 'r') as f:
        config = json.load(f)

    db_config = config['auth_database']  # Now we can safely access auth_database

    try:
        # Connect without specifying the database
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['username'],
            password=db_config['password'],
            port=db_config['port']
        )

        with connection.cursor() as cursor:
            # Check if database exists
            cursor.execute("SHOW DATABASES LIKE %s", (db_config['database'],))
            result = cursor.fetchone()

            # If database doesn't exist, create it
            if not result:
                print(f"Creating database '{db_config['database']}'...")
                cursor.execute(f"CREATE DATABASE `{db_config['database']}`")
                print(f"Database '{db_config['database']}' created successfully.")
            else:
                print(f"Database '{db_config['database']}' already exists.")

        connection.close()
        return True
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False


def setup_initial_users():
    """Initialize database tables and create default users if needed"""
    logger = Logger()
    logger.info("Starting database initialization")

    # First, make sure the auth database exists and config is updated
    if not create_database_if_not_exists():
        logger.error("Failed to create/verify database. Exiting.")
        return

    # Now we can safely import these modules after config is updated
    from app.database.db_connection import AuthDatabase
    from app.models import User, UserRole

    # Initialize database connection for auth
    try:
        db = AuthDatabase()

        # Create tables if they don't exist
        db.create_tables()
        logger.info("Auth database tables created/verified successfully")

        # Get a session for user operations
        db_session = db.get_session()

        # Check if any users exist
        try:
            user_count = db_session.query(User).count()
            if user_count > 0:
                print(f"Database already has {user_count} users. Skipping user creation.")
                logger.info(f"Database already has {user_count} users. Skipping initialization.")
                return

            # Create default users
            default_users = [
                {"username": "admin", "password": "Admin@123", "role": UserRole.ADMIN},
                {"username": "datawarehouse", "password": "Data@123", "role": UserRole.DATA_WAREHOUSE},
                {"username": "teacher", "password": "Teacher@123", "role": UserRole.TEACHER},
                {"username": "supervisor", "password": "Super@123", "role": UserRole.SUPERVISOR}
            ]

            for user_data in default_users:
                user = User(username=user_data["username"], role=user_data["role"])
                user.set_password(user_data["password"])
                db_session.add(user)

            db_session.commit()
            print("Initial users created successfully.")
            logger.info("Initial users created successfully.")

        except Exception as e:
            db_session.rollback()
            print(f"Error creating users: {str(e)}")
            logger.error(f"Error creating users: {str(e)}")

    except Exception as e:
        print(f"Error during database initialization: {str(e)}")
        logger.error(f"Error during database initialization: {str(e)}")
    finally:
        if 'db_session' in locals():
            db_session.close()


if __name__ == "__main__":
    print("Starting database initialization...")
    setup_initial_users()
    print("Database initialization completed")