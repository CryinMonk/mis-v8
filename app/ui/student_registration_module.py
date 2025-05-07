from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from app.ui.components.student.student_crud_widget import StudentCrudWidget
from app.utils.logger import Logger


class StudentRegistrationModule(QWidget):
    """Module for student registration and management"""

    # Add signals for data changes
    data_changed = pyqtSignal()

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.logger = Logger()
        self.user = user

        # Log user information for debugging
        if self.user:
            self.logger.info(
                f"StudentRegistrationModule initialized with user: {self.user.username}, role: {self.user.role.value}")
        else:
            self.logger.warning("StudentRegistrationModule initialized without user information")

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Student Registration & Management")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(header_label)

        # Description
        description_label = QLabel(
            "This module allows you to manage student records including personal information, "
            "education history, enrollments, medical history, and more."
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description_label)

        # Add user role information if available
        if self.user:
            user_label = QLabel(f"Logged in as: {self.user.username} ({self.user.role.value})")
            user_label.setAlignment(Qt.AlignRight)
            main_layout.addWidget(user_label)

        # Create StudentCrudWidget with user role information
        if self.user:
            self.student_crud = StudentCrudWidget(
                parent=self,
                current_user=self.user.username,
                user_role=self.user.role  # Pass the actual role enum
            )
            # Connect student CRUD data change signals
            if hasattr(self.student_crud, 'data_changed'):
                self.student_crud.data_changed.connect(self.on_data_changed)

            self.logger.info(f"Created StudentCrudWidget with role: {self.user.role}")
        else:
            # Fallback if no user info is available
            self.student_crud = StudentCrudWidget(parent=self)
            self.logger.warning("Created StudentCrudWidget without user role information")

        main_layout.addWidget(self.student_crud)

    def refresh(self):
        """Refresh the current view"""
        self.logger.info("Refreshing StudentRegistrationModule")

        if hasattr(self, 'student_crud'):
            # Call refresh_current_view() instead of load_students()
            # This will respect the currently selected table
            self.student_crud.refresh_current_view()

            # Log refresh for debugging
            if self.user:
                self.logger.info(f"Refreshed student data for user: {self.user.username}")

    def on_data_changed(self):
        """Handle data changed signal from student crud widget"""
        self.logger.info("Data changed signal received in StudentRegistrationModule")
        self.data_changed.emit()  # Propagate signal upward

    def showEvent(self, event):
        """Refresh when widget becomes visible"""
        super().showEvent(event)
        self.refresh()

    def hideEvent(self, event):
        """Handle cleanup when widget is hidden"""
        super().hideEvent(event)
        self.logger.info("StudentRegistrationModule hidden")

    def cleanup(self):
        """Clean up resources when module is being closed"""
        try:
            # Clean up student crud widget
            if hasattr(self, 'student_crud'):
                if hasattr(self.student_crud, 'data_changed'):
                    try:
                        self.student_crud.data_changed.disconnect()
                    except TypeError:
                        pass  # Signal might not be connected

                # If student_crud has cleanup method, call it
                if hasattr(self.student_crud, 'cleanup'):
                    self.student_crud.cleanup()

            # Disconnect own signals
            try:
                self.data_changed.disconnect()
            except TypeError:
                pass  # Signal might not be connected

            self.logger.info("StudentRegistrationModule cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up StudentRegistrationModule: {str(e)}")

    def closeEvent(self, event):
        """Handle close event"""
        try:
            self.cleanup()
            super().closeEvent(event)
        except Exception as e:
            self.logger.error(f"Error in StudentRegistrationModule closeEvent: {str(e)}")
            event.accept()  # Accept anyway to prevent being stuck