import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
import socket
import datetime

from app.database.db_connection import AuthDatabase
from app.controllers.auth_controller import AuthController
from app.ui.main_window import MainWindow
from app.utils.logger import Logger
from app.config.config import Config


class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(object, object)  # Signals: user, session

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIS Login")
        self.setMinimumSize(400, 300)
        self.logger = Logger()

        # Connect to database
        try:
            self.db = AuthDatabase()
            self.db_session = self.db.get_session()
            self.auth_controller = AuthController(self.db_session)
        except Exception as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            QMessageBox.critical(self, "Database Error", f"Failed to connect to database: {str(e)}")
            sys.exit(1)

        self.init_ui()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("Management Information System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))

        # Username input
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setMinimumWidth(80)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)

        # Password input
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setMinimumWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.attempt_login)

        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)
        main_layout.addLayout(username_layout)
        main_layout.addLayout(password_layout)
        main_layout.addStretch(1)
        main_layout.addWidget(self.login_button)

        # Set return/enter key to trigger login
        self.username_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)

        # Set initial focus to username field
        self.username_input.setFocus()

    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        # Get client information for session
        client_ip = socket.gethostbyname(socket.gethostname())
        user_agent = f"PyQt5 MIS Client {QApplication.applicationVersion()}"

        # Authenticate user
        user, session, message = self.auth_controller.authenticate(
            username, password, client_ip, user_agent
        )

        if user and session:
            # Update last login in config
            config = Config()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            config.update_last_login(username, timestamp)

            self.logger.info(f"User {username} logged in successfully")
            # QMessageBox.information(self, "Login Successful", f"Welcome, {user.username}!")
            self.login_successful.emit(user, session)
            self.hide()  # Hide login window instead of closing it
        else:
            self.logger.warning(f"Failed login attempt for user {username}: {message}")
            QMessageBox.warning(self, "Login Failed", message)


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user = None
        self.session = None
        self.main_window = None  # Reference to main window
        self.login_window = None  # Initialize the login_window attribute

        # Initialize database connection
        self.db = AuthDatabase()
        self.logger = Logger()

        # Ensure tables exist for auth database
        try:
            self.db.create_tables()
            self.logger.info("Auth database tables checked/created")
        except Exception as e:
            self.logger.error(f"Failed to create database tables: {str(e)}")
            QMessageBox.critical(self, "Database Error", f"Failed to create database tables: {str(e)}")
            sys.exit(1)

        # Show login window
        self.show_login()

    def show_login(self):
        """Show the login window"""
        # Create login window if it doesn't exist
        if self.login_window is None:
            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.on_login_successful)

        # Clear previous credentials if any
        if hasattr(self.login_window, 'username_input') and self.login_window.username_input is not None:
            self.login_window.username_input.clear()
            self.login_window.password_input.clear()

        # Show the login window
        self.login_window.show()

    def on_login_successful(self, user, session):
        """Handle successful login"""
        self.user = user
        self.session = session

        # Hide login window
        if self.login_window:
            self.login_window.hide()

        # Initialize and show main window with error handling
        try:
            self.main_window = MainWindow(user, session)
            self.main_window.logout_requested.connect(self.logout)
            self.main_window.show()
        except Exception as e:
            self.logger.error(f"Error initializing main window: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize main window: {str(e)}")
            # Show login window again if main window fails
            self.login_window.show()

    def logout(self):
        """Handle user logout"""
        # Get a new session to handle the logout
        db_session = self.db.get_session()
        auth_controller = AuthController(db_session)

        # End the session
        success, message = auth_controller.logout(self.session.session_token)

        if success:
            self.logger.info(f"User {self.user.username} logged out successfully")
            # QMessageBox.information(self, "Logout", "You have been logged out successfully.")
        else:
            self.logger.warning(f"Logout error for user {self.user.username}: {message}")
            QMessageBox.warning(self, "Logout Error", f"Error during logout: {message}")

        # Close DB session
        self.db.close_session(db_session)

        # Hide main window (don't close it yet)
        if self.main_window:
            self.main_window.hide()
            if hasattr(self.main_window, 'disconnect_signals'):
                self.main_window.disconnect_signals()  # Add this method to MainWindow

        # Reset user and session
        self.user = None
        self.session = None

        # Show login window again
        self.show_login()