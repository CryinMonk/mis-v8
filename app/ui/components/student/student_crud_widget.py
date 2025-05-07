from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QApplication, QFrame, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from app.ui.components.student_edit_dialog import StudentEditDialog
from app.services.student_service import StudentService
from app.utils.logger import Logger
from app.controllers.rbac_controller import RBACController
from app.config.config import Config
from app.utils.timer_manager import TimerManager
from app.ui.components.student_details_dialog import StudentDetailsDialog
from app.ui.components.student.student_crud_table_manager import StudentTableManager
from app.ui.components.student.student_crud_ui_builder import StudentCrudUIBuilder
from app.ui.components.student.student_crud_search_handler import StudentSearchHandler
from app.ui.components.student.student_crud_action_handler import StudentActionHandler
from app.ui.components.student.student_crud_utils import StudentCrudUtils

class StudentCrudWidget(QWidget):
    """Widget for Student CRUD operations with role-based permissions"""

    # Add signal for data changes
    data_changed = pyqtSignal()

    def __init__(self, parent=None, current_user=None, user_role=None):
        super().__init__(parent)
        self.student_service = StudentService()
        self.logger = Logger()
        self.config = Config()

        # Get current user from Config if not provided
        self.current_user = current_user or self.config.current_user or "CryinMonk"

        # Create a user object for logging purposes
        self.user = type('User', (), {'username': self.current_user})

        # Initialize RBAC controller
        self.rbac = RBACController()

        # Store user role for permission checks
        self.user_role = user_role

        # Setup auto-refresh when this widget becomes visible
        self.visible_refresh_timer = None

        # Get timer manager instance (centralized timer)
        self.timer_manager = TimerManager.instance()

        # Track the currently selected table
        self.selected_table = "students"

        # Define table options
        self.table_options = [
            {"id": "students", "display": "Students"},
            {"id": "guardians", "display": "Guardians"},
            {"id": "medical_history", "display": "Medical History"},
            {"id": "education", "display": "Education History"},
            {"id": "enrollments", "display": "Enrollments"},
            {"id": "hostel", "display": "Hostel Management"},
            {"id": "transportation", "display": "Transportation"}
        ]

        # Initialize helper classes
        self.utils = StudentCrudUtils(self)
        self.ui_builder = StudentCrudUIBuilder(self)
        self.table_manager = StudentTableManager(self)
        self.search_handler = StudentSearchHandler(self)
        self.action_handler = StudentActionHandler(self)

        # Log initialization with dynamic timestamp
        self.utils._log_activity("StudentCrudWidget initialized")

        # Setup UI
        self.ui_builder.init_ui()
        self.table_manager.load_students()

        # Connect to timer manager for auto-refresh
        self.timer_manager.student_data_refresh_signal.connect(self.on_auto_refresh)

    def on_auto_refresh(self):
        """Handle auto-refresh from timer manager"""
        # Only refresh if widget is visible
        if self.isVisible():
            # Get current selection before refresh
            current_index = self.table_selector.currentIndex()
            current_table_id = self.table_selector.itemData(current_index)

            # Log the refresh action with the current selected table
            self.utils._log_activity(f"Auto-refreshing {current_table_id} data via timer manager")

            # Temporarily block signals from the table selector
            old_block_state = self.table_selector.blockSignals(True)

            # Ensure selected_table matches current UI selection
            self.selected_table = current_table_id

            # Refresh the data for the current table
            if self.selected_table == "students":
                self.table_manager.load_students()
            else:
                self.table_manager.load_related_table_data()

            # Restore the UI selection and unblock signals
            self.table_selector.setCurrentIndex(current_index)
            self.table_selector.blockSignals(old_block_state)
        else:
            self.utils._log_activity("Auto-refresh skipped - widget not visible")

    def refresh_current_view(self):
        """Refresh the currently selected table view without changing selection"""
        # Get current selection
        current_index = self.table_selector.currentIndex()
        current_table_id = self.table_selector.itemData(current_index)

        # Block signals
        old_block_state = self.table_selector.blockSignals(True)

        # Update internal state to match UI
        self.selected_table = current_table_id

        # Refresh appropriate data
        if self.selected_table == "students":
            self.table_manager.load_students()
        else:
            self.table_manager.load_related_table_data()

        # Restore selection and unblock signals
        self.table_selector.setCurrentIndex(current_index)
        self.table_selector.blockSignals(old_block_state)

    def on_table_changed(self, index):
        """Handle table selection change from dropdown"""
        # Get the selected table from the dropdown data
        selected_table = self.table_selector.currentData()

        # Skip if same table is selected
        if selected_table == self.selected_table:
            return

        # Block signals to prevent auto-refresh from interfering with this change
        old_state = self.table_selector.blockSignals(True)

        self.utils._log_activity(f"Changing view from '{self.selected_table}' to '{selected_table}'")
        self.selected_table = selected_table

        # Update UI based on selection
        self.ui_builder.update_ui_for_selected_table()

        # Reset search input
        self.search_input.clear()
        self.search_input.setStyleSheet("")

        # Load data for the selected table
        self.refresh_current_view()

        # Unblock signals
        self.table_selector.blockSignals(old_state)

    def on_reset_clicked(self):
        """Handle reset button click based on selected table"""
        # Simply refresh the current view instead of hardcoding to students
        self.refresh_current_view()

    def search_students(self):
        """Search for students or related records based on current table selection"""
        self.search_handler.search_students()

    def add_student(self):
        """Show comprehensive dialog to register a new student"""
        self.action_handler.add_student()

    def on_student_added(self, student_id):
        """Handle when a new student is added"""
        self.action_handler.on_student_added(student_id)

    def highlight_student(self, student_id):
        """Highlight a specific student in the table by ID"""
        self.table_manager.highlight_student(student_id)

    def edit_student(self):
        """Show dialog to edit an existing student"""
        self.action_handler.edit_student()

    def view_student(self):
        """Show detailed view of a student"""
        self.action_handler.view_student()

    def delete_student(self):
        """Delete a student after confirmation"""
        self.action_handler.delete_student()

    def show_search_info(self):
        """Show information about search capabilities"""
        self.search_handler.show_search_info()

    def showEvent(self, event):
        """Override showEvent to refresh data when widget becomes visible"""
        super().showEvent(event)

        # Store current table selection
        current_selection = self.table_selector.currentIndex()

        # Create a short timer to refresh data when widget becomes visible
        if not self.visible_refresh_timer:
            self.visible_refresh_timer = QTimer(self)
            self.visible_refresh_timer.setSingleShot(True)
            self.visible_refresh_timer.timeout.connect(self.on_refresh_timer)

        self.visible_refresh_timer.start(100)  # 100ms delay
        self.utils._log_activity("Widget became visible, scheduling refresh")

        # Ensure the table selection is preserved
        self.table_selector.setCurrentIndex(current_selection)

    def on_refresh_timer(self):
        """Handle refresh timer based on selected table"""
        # Store current table selection
        current_selection = self.table_selector.currentIndex()

        # Use the refresh_current_view method to maintain table selection
        self.refresh_current_view()

        # Restore table selection
        self.table_selector.setCurrentIndex(current_selection)

    def hideEvent(self, event):
        """Overrides hideEvent to save resources when widget is hidden"""
        super().hideEvent(event)
        self.utils._log_activity("Widget hidden")

    def disconnect_signals(self):
        """Disconnect signals to prevent memory leaks"""
        try:
            # Disconnect from timer manager
            self.timer_manager.datetime_update_signal.disconnect(self.update_time_display)
            self.timer_manager.student_data_refresh_signal.disconnect(self.on_auto_refresh)

            # Stop local timer if it exists
            if self.visible_refresh_timer and self.visible_refresh_timer.isActive():
                self.visible_refresh_timer.stop()

            self.utils._log_activity("Signals disconnected")
        except Exception as e:
            self.logger.error(f"Error disconnecting signals: {str(e)}")

    def update_time_display(self):
        """Update the time display in the header - connected to timer manager signal"""
        self.user_time_label.setText(f"User: {self.current_user} | {self.utils._get_current_time_utc()}")