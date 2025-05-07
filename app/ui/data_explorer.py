from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer

from app.database.db_connection import DataDatabase
from app.utils.logger import Logger
from app.ui.student_registration_module import StudentRegistrationModule


class DataExplorerWidget(QWidget):
    """Main data exploration widget with Student Registration as the sole content"""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.logger = Logger()
        self.user = user
        self.db = None
        self.db_session = None
        self.student_module = None
        self.refresh_timer = None

        # Log user information for debugging
        if self.user:
            self.logger.info(
                f"DataExplorerWidget initialized with user: {self.user.username}, role: {self.user.role.value}")
        else:
            self.logger.warning("DataExplorerWidget initialized without user information")

        # Initialize database connection safely
        try:
            self.db = DataDatabase()
            self.db_session = self.db.get_session()
            self.init_ui()

            # Set up auto-refresh timer - refresh every 30 seconds
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.auto_refresh)
            self.refresh_timer.start(30000)  # 30 seconds

            self.logger.info("Auto-refresh timer started (30 second interval)")
        except Exception as e:
            self.logger.error(f"Failed to initialize DataExplorerWidget: {str(e)}")
            self.show_error_ui(str(e))

    def auto_refresh(self):
        """Automatically refresh the content"""
        try:
            if hasattr(self, 'student_module') and self.student_module:
                self.student_module.refresh()
                self.logger.info("Student module auto-refreshed successfully")
        except Exception as e:
            self.logger.error(f"Error during auto-refresh: {str(e)}")

    def init_ui(self):
        """Initialize the UI with Student Registration as the main content"""
        main_layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("<h2>Data Management - Student Registration</h2>")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        # Student Registration Module - pass the user object
        try:
            self.student_module = StudentRegistrationModule(parent=self, user=self.user)
            main_layout.addWidget(self.student_module)
        except Exception as e:
            self.logger.error(f"Failed to initialize StudentRegistrationModule: {str(e)}")
            self.show_error_ui(f"Error loading Student Registration: {str(e)}")

    def show_error_ui(self, error_message):
        """Show error UI when initialization fails"""
        layout = QVBoxLayout(self)
        error_label = QLabel(f"<h3>Error Loading Data Explorer</h3>")
        error_label.setAlignment(Qt.AlignCenter)

        message_label = QLabel(f"Error: {error_message}")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: red;")

        layout.addWidget(error_label)
        layout.addWidget(message_label)
        layout.addStretch()

    def refresh_current_view(self):
        """Manually refresh the content"""
        try:
            if hasattr(self, 'student_module') and self.student_module:
                self.student_module.refresh()
                self.logger.info("Student module manually refreshed")
        except Exception as e:
            self.logger.error(f"Error in refresh_current_view: {str(e)}")

    def showEvent(self, event):
        """Override showEvent to refresh data whenever the widget becomes visible"""
        try:
            super().showEvent(event)
            QTimer.singleShot(200, self.refresh_current_view)
        except Exception as e:
            self.logger.error(f"Error in showEvent: {str(e)}")

    def hideEvent(self, event):
        """Override hideEvent to stop timer temporarily when widget is hidden"""
        try:
            super().hideEvent(event)
            # Stop the refresh timer temporarily
            if hasattr(self, 'refresh_timer') and self.refresh_timer and self.refresh_timer.isActive():
                self.refresh_timer.stop()
                self.logger.info("Refresh timer stopped during hide")
        except Exception as e:
            self.logger.error(f"Error in hideEvent: {str(e)}")

    def cleanup(self):
        """Clean up resources"""
        try:
            # Stop timers
            if hasattr(self, 'refresh_timer') and self.refresh_timer:
                if self.refresh_timer.isActive():
                    self.refresh_timer.stop()

                # Disconnect the timer signal
                try:
                    self.refresh_timer.timeout.disconnect()
                except TypeError:
                    pass  # Signal might not be connected

                # Delete the timer
                self.refresh_timer.deleteLater()
                self.refresh_timer = None

            # Clean up student module
            if hasattr(self, 'student_module') and self.student_module:
                if hasattr(self.student_module, 'cleanup'):
                    self.student_module.cleanup()
                self.student_module.deleteLater()
                self.student_module = None

            # Close database session if it exists
            if hasattr(self, 'db_session') and self.db_session:
                self.db_session.close()
                self.db_session = None

            self.logger.info("DataExplorerWidget cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up DataExplorerWidget: {str(e)}")

    def closeEvent(self, event):
        """Override closeEvent to stop the timer when widget is closed"""
        try:
            self.cleanup()
            super().closeEvent(event)
        except Exception as e:
            self.logger.error(f"Error in closeEvent: {str(e)}")
            event.accept()  # Accept anyway to prevent being stuck