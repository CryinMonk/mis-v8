from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models.base import Base
from app.config.config import Config


class AuthDatabase:
    """Database connection for authentication and user management"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthDatabase, cls).__new__(cls)
            cls._instance._initialize_db()
        return cls._instance

    def _initialize_db(self):
        config = Config()
        connection_string = config.get_auth_db_connection_string()

        self.engine = create_engine(connection_string, pool_recycle=3600)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def create_tables(self):
        # Import all auth-related models here
        # from app.models import User, UserSession, LoginAttempt
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    # @staticmethod
    def close_session(self, session):
        if session:
            session.close()


class DataDatabase:
    """Database connection for student data and operations"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataDatabase, cls).__new__(cls)
            cls._instance._initialize_db()
        return cls._instance

    def _initialize_db(self):
        config = Config()
        connection_string = config.get_data_db_connection_string()

        self.engine = create_engine(connection_string, pool_recycle=3600)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def get_session(self):
        return self.Session()

    # @staticmethod
    def close_session(self, session):
        if session:
            session.close()