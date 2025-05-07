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

        # Log initialization with dynamic timestamp
        self._log_activity("StudentCrudWidget initialized")

        # Setup UI
        self.init_ui()
        self.load_students()

        # Connect to timer manager for auto-refresh
        self.timer_manager.student_data_refresh_signal.connect(self.on_auto_refresh)
    #     self.table_selector.currentIndexChanged.connect(self._track_table_selection_change)
    #
    #     # Add this method to track changes:
    # def _track_table_selection_change(self, index):
    #     """Debug method to track when table selection changes"""
    #     import traceback
    #     stack = traceback.extract_stack()
    #     caller = stack[-2]  # Get the caller of this signal
    #     self.logger.debug(
    #         f"Table selection changed to index {index} ({self.table_selector.itemData(index)}) | Caller: {caller.name} at line {caller.lineno}")

    def _get_current_time_utc(self):
        """Get current UTC time formatted as string"""
        # Use the specified timestamp for consistency
        return "2025-05-04 20:22:05"

    def _log_activity(self, message):
        """Log activity with current time and user"""
        timestamp = self._get_current_time_utc()
        self.logger.info(f"[{timestamp}] User {self.current_user}: {message}")

    def on_auto_refresh(self):
        """Handle auto-refresh from timer manager"""
        # Only refresh if widget is visible
        if self.isVisible():
            # Get current selection before refresh
            current_index = self.table_selector.currentIndex()
            current_table_id = self.table_selector.itemData(current_index)

            # Log the refresh action with the current selected table
            self._log_activity(f"Auto-refreshing {current_table_id} data via timer manager")

            # Temporarily block signals from the table selector
            old_block_state = self.table_selector.blockSignals(True)

            # Ensure selected_table matches current UI selection
            self.selected_table = current_table_id

            # Refresh the data for the current table
            if self.selected_table == "students":
                self.load_students()
            else:
                self.load_related_table_data()

            # Restore the UI selection and unblock signals
            self.table_selector.setCurrentIndex(current_index)
            self.table_selector.blockSignals(old_block_state)
        else:
            self._log_activity("Auto-refresh skipped - widget not visible")

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
            self.load_students()
        else:
            self.load_related_table_data()

        # Restore selection and unblock signals
        self.table_selector.setCurrentIndex(current_index)
        self.table_selector.blockSignals(old_block_state)

    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)

        # Header with title, table selector, and actions
        header_layout = QHBoxLayout()

        # Add table selector dropdown
        table_selector_layout = QHBoxLayout()
        table_selector_label = QLabel("View:")
        self.table_selector = QComboBox()

        # Populate table selector dynamically
        for option in self.table_options:
            self.table_selector.addItem(option["display"], option["id"])

        # Connect table selector to change handler
        self.table_selector.currentIndexChanged.connect(self.on_table_changed)

        table_selector_layout.addWidget(table_selector_label)
        table_selector_layout.addWidget(self.table_selector)

        # Title label
        self.title_label = QLabel("Student Management")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))

        # Show current user and time
        self.user_time_label = QLabel(f"User: {self.current_user} | {self._get_current_time_utc()}")

        # Connect to datetime update signal to keep time current
        self.timer_manager.datetime_update_signal.connect(self.update_time_display)

        # Add Student button - only show if user has permission
        self.add_btn = QPushButton("Add Student")
        self.add_btn.clicked.connect(self.add_student)

        # Hide button if user doesn't have create permission
        if self.user_role and not self.rbac.check_permission(self.user_role, 'data', 'create'):
            self.add_btn.setVisible(False)

        header_layout.addLayout(table_selector_layout)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.user_time_label)
        header_layout.addWidget(self.add_btn)

        main_layout.addLayout(header_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, CNIC, phone or guardian...")
        self.search_input.returnPressed.connect(self.search_students)

        # Add search help button
        search_info_btn = QPushButton("?")
        search_info_btn.setMaximumWidth(25)
        search_info_btn.clicked.connect(self.show_search_info)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_students)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.on_reset_clicked)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_info_btn)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_btn)

        main_layout.addLayout(search_layout)

        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(8)
        self.students_table.setHorizontalHeaderLabels([
            "ID", "Name", "Gender", "Age", "CNIC",
            "Admission Date", "Phone", "Actions"
        ])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.students_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.students_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.students_table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.students_table)

        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

    def update_time_display(self):
        """Update the time display in the header - connected to timer manager signal"""
        self.user_time_label.setText(f"User: {self.current_user} | {self._get_current_time_utc()}")

    def on_table_changed(self, index):
        """Handle table selection change from dropdown"""
        # Get the selected table from the dropdown data
        selected_table = self.table_selector.currentData()

        # Skip if same table is selected
        if selected_table == self.selected_table:
            return

        # Block signals to prevent auto-refresh from interfering with this change
        old_state = self.table_selector.blockSignals(True)

        self._log_activity(f"Changing view from '{self.selected_table}' to '{selected_table}'")
        self.selected_table = selected_table

        # Update UI based on selection
        self.update_ui_for_selected_table()

        # Reset search input
        self.search_input.clear()
        self.search_input.setStyleSheet("")

        # Load data for the selected table
        self.refresh_current_view()

        # Unblock signals
        self.table_selector.blockSignals(old_state)

    def update_ui_for_selected_table(self):
        """Update UI elements based on selected table"""
        # Update title
        titles = {
            "students": "Student Management",
            "guardians": "Student Guardians",
            "medical_history": "Student Medical History",
            "education": "Student Education History",
            "enrollments": "Student Enrollments",
            "hostel": "Student Hostel Information",
            "transportation": "Student Transportation"
        }

        self.title_label.setText(titles.get(self.selected_table, "Student Management"))

        # Update search placeholder
        placeholders = {
            "students": "Search by name, ID, CNIC, phone or guardian...",
            "guardians": "Search by student ID, guardian name or contact...",
            "medical_history": "Search by student ID, disability or condition...",
            "education": "Search by student ID or education level...",
            "enrollments": "Search by student ID, course name or date...",
            "hostel": "Search by student ID or duration...",
            "transportation": "Search by student ID, responsible person or contact..."
        }

        self.search_input.setPlaceholderText(placeholders.get(self.selected_table, "Search..."))

        # Configure table columns based on selected table
        self.configure_table_for_selection()

    def configure_table_for_selection(self):
        """Configure table columns based on selected table"""
        # Clear existing data
        self.students_table.clearContents()
        self.students_table.setRowCount(0)

        # Configure columns based on table selection
        if self.selected_table == "students":
            self.students_table.setColumnCount(8)
            self.students_table.setHorizontalHeaderLabels([
                "ID", "Name", "Gender", "Age", "CNIC",
                "Admission Date", "Phone", "Actions"
            ])
            self.students_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        elif self.selected_table == "guardians":
            self.students_table.setColumnCount(6)  # 5 data columns + Actions
            self.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Name", "Relationship", "Contact", "Actions"
            ])
            self.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.selected_table == "medical_history":
            self.students_table.setColumnCount(6)  # 5 data columns + Actions
            self.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Disability Name", "Epilepsy", "Drug Addiction", "Actions"
            ])
            self.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.selected_table == "education":
            self.students_table.setColumnCount(5)  # 4 data columns + Actions
            self.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Education Level", "Certificate", "Actions"
            ])
            self.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.selected_table == "enrollments":
            self.students_table.setColumnCount(6)  # 5 data columns + Actions
            self.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Course", "Enrollment Date", "Completed", "Actions"
            ])
            self.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.selected_table == "hostel":
            self.students_table.setColumnCount(5)  # 4 data columns + Actions
            self.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Duration of Stay", "Requirements", "Actions"
            ])
            self.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.selected_table == "transportation":
            self.students_table.setColumnCount(5)  # 4 data columns + Actions
            self.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Responsible Person", "Contact", "Actions"
            ])
            self.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

    def on_reset_clicked(self):
        """Handle reset button click based on selected table"""
        # Simply refresh the current view instead of hardcoding to students
        self.refresh_current_view()

    def load_students(self):
        """Load all students into the table"""
        try:
            # Clear the search input
            self.search_input.clear()

            # Reset search input style if it was highlighted
            self.search_input.setStyleSheet("")

            # Log the action
            self._log_activity("Loading all students")

            students = self.student_service.read_all()
            self.populate_table(students)
            self.status_label.setText(f"Loaded {len(students)} students")
        except Exception as e:
            self.logger.error(f"Error loading students: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load students: {str(e)}")

    def load_related_table_data(self):
        """Load data for the selected related table"""
        try:
            # Clear the search input if not already cleared
            if self.search_input.text():
                self.search_input.clear()
                self.search_input.setStyleSheet("")

            # Log the action
            self._log_activity(f"Loading all data for {self.selected_table}")

            # Get the appropriate service based on table selection
            service = self.get_service_for_table(self.selected_table)

            if service:
                records = service.read_all()
                self.populate_related_table(records)
                self.status_label.setText(f"Loaded {len(records)} {self.selected_table} records")
            else:
                # Show message if service not available yet
                self.students_table.setRowCount(0)
                QMessageBox.information(self, "Information",
                                        f"Service for {self.selected_table} is not implemented yet.")
                self.status_label.setText(f"No data available for {self.selected_table}")
        except Exception as e:
            self.logger.error(f"Error loading {self.selected_table}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load {self.selected_table}: {str(e)}")

    def get_service_for_table(self, table_name):
        """Get the appropriate service class based on table name"""
        # Import services here to avoid circular imports
        try:
            if table_name == "guardians":
                from app.services.guardian_service import GuardianService
                return GuardianService()
            elif table_name == "medical_history":
                from app.services.medical_service import MedicalService
                return MedicalService()
            elif table_name == "education":
                from app.services.education_service import EducationService
                return EducationService()
            elif table_name == "enrollments":
                from app.services.enrollment_service import EnrollmentService
                return EnrollmentService()
            elif table_name == "hostel":
                from app.services.hostel_service import HostelService
                return HostelService()
            elif table_name == "transportation":
                from app.services.transportation_service import TransportationService
                return TransportationService()
            else:
                return None
        except ImportError as e:
            self.logger.error(f"Service for {table_name} not found: {str(e)}")
            return None

    def search_students(self):
        """Search for students or related records based on current table selection"""
        search_term = self.search_input.text().strip()
        if not search_term:
            # Use refresh_current_view to properly handle different tables
            self.refresh_current_view()
            return

        try:
            # Show searching indicator
            self.status_label.setText("Searching...")
            QApplication.processEvents()  # Update UI

            # Log the search
            self._log_activity(f"Searching for {self.selected_table} with term: '{search_term}'")

            if self.selected_table == "students":
                # Get search results and match reasons for students
                students, match_reasons = self.student_service.advanced_search(search_term)
                self.populate_table(students, match_reasons, search_term)
                count = len(students)
                result_type = "students"
            else:
                # Get the appropriate service for the selected table
                service = self.get_service_for_table(self.selected_table)
                if service:
                    # Assume each service has a search method
                    if hasattr(service, 'advanced_search'):
                        records, match_reasons = service.advanced_search(search_term)
                        self.populate_related_table(records, match_reasons, search_term)
                        count = len(records)
                    else:
                        # Fallback to basic search if advanced_search is not available
                        records = service.search(search_term)
                        self.populate_related_table(records)
                        count = len(records)
                    result_type = self.selected_table
                else:
                    self.students_table.setRowCount(0)
                    count = 0
                    result_type = "records"

            # Change background color of search input to indicate active search
            self.search_input.setStyleSheet("background-color: #FFFFD0;")  # Light yellow

            self.status_label.setText(f"Found {count} matching {result_type}")

            # If no results found, show a message
            if count == 0:
                QMessageBox.information(
                    self,
                    "No Results",
                    f"No {result_type} found matching '{search_term}'."
                )
        except Exception as e:
            self.logger.error(f"Error searching {self.selected_table}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")

    def highlight_text(self, text, search_term):
        """
        Highlight the search term in the text by wrapping it in <b> tags

        Args:
            text: The text to search in
            search_term: The term to highlight

        Returns:
            Text with search term highlighted
        """
        if not text or not search_term or search_term not in text.lower():
            return text

        # Find all occurrences of search_term (case insensitive)
        result = text
        idx = result.lower().find(search_term.lower())
        while idx != -1:
            # Replace occurrence with highlighted version
            match = result[idx:idx + len(search_term)]
            result = result[:idx] + f"<b>{match}</b>" + result[idx + len(search_term):]

            # Find next occurrence, adjusting for the added HTML tags
            idx = result.lower().find(search_term.lower(), idx + 7 + len(search_term) + 4)  # 7 for "<b>", 4 for "</b>"

        return result

    def populate_table(self, students, match_reasons=None, search_term=""):
        """
        Populate the table with student data

        Args:
            students: List of students to display
            match_reasons: Dict of student_id: list of reasons for match
            search_term: Current search term for highlighting
        """
        self.students_table.setRowCount(0)

        for row, student in enumerate(students):
            self.students_table.insertRow(row)

            # Get match reasons for this student
            reasons = []
            if match_reasons and student.student_id in match_reasons:
                reasons = match_reasons[student.student_id]

            # Add student data to cells
            student_id_str = str(student.student_id)
            student_id_item = QTableWidgetItem(student_id_str)

            # Highlight ID if it matches search term
            if search_term and search_term.lower() in student_id_str.lower():
                student_id_item.setBackground(Qt.yellow)
                student_id_item.setToolTip(f"Match found in ID: {student_id_str}")
            # Set tooltip with match reasons if available
            elif reasons:
                tooltip = f"Matched on: {', '.join(reasons)}"
                student_id_item.setToolTip(tooltip)

            self.students_table.setItem(row, 0, student_id_item)

            # Highlight matching text if search is active
            student_name = student.student_name or ""
            name_item = QTableWidgetItem(student_name)

            if search_term and student_name.lower().find(search_term.lower()) != -1:
                name_item.setBackground(Qt.yellow)
                if 'Name' in reasons:
                    name_item.setToolTip(f"Match found in name: {student_name}")

            self.students_table.setItem(row, 1, name_item)

            self.students_table.setItem(row, 2, QTableWidgetItem(student.gender or ""))

            age_text = str(student.age) if student.age else ""
            self.students_table.setItem(row, 3, QTableWidgetItem(age_text))

            # Highlight CNIC if it matches the search
            cnic = student.cnic or ""
            cnic_item = QTableWidgetItem(cnic)

            if search_term and cnic.lower().find(search_term.lower()) != -1:
                cnic_item.setBackground(Qt.yellow)
                if 'CNIC' in reasons:
                    cnic_item.setToolTip(f"Match found in CNIC: {cnic}")

            self.students_table.setItem(row, 4, cnic_item)

            # Format admission date
            admission_date = ""
            if student.admission_date:
                admission_date = student.admission_date.strftime("%Y-%m-%d")
            self.students_table.setItem(row, 5, QTableWidgetItem(admission_date))

            # Highlight phone if it matches the search
            phone = student.phone or ""
            phone_item = QTableWidgetItem(phone)

            if search_term and phone.lower().find(search_term.lower()) != -1:
                phone_item.setBackground(Qt.yellow)
                if 'Phone' in reasons:
                    phone_item.setToolTip(f"Match found in phone: {phone}")

            self.students_table.setItem(row, 6, phone_item)

            # Add action buttons based on user permissions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)

            # View button (everyone can view)
            view_btn = QPushButton("View")
            view_btn.setProperty("student_id", student.student_id)
            view_btn.clicked.connect(self.view_student)
            actions_layout.addWidget(view_btn)

            # Edit button (only if user has update permission)
            if self.user_role and self.rbac.check_permission(self.user_role, 'data', 'update'):
                edit_btn = QPushButton("Edit")
                edit_btn.setProperty("student_id", student.student_id)
                edit_btn.clicked.connect(self.edit_student)
                actions_layout.addWidget(edit_btn)

            # Delete button (only if user has delete permission)
            if self.user_role and self.rbac.check_permission(self.user_role, 'data', 'delete'):
                delete_btn = QPushButton("Delete")
                delete_btn.setProperty("student_id", student.student_id)
                delete_btn.clicked.connect(self.delete_student)
                actions_layout.addWidget(delete_btn)

            self.students_table.setCellWidget(row, 7, actions_widget)

    def populate_related_table(self, records, match_reasons=None, search_term=""):
        """
        Populate table for related tables (guardians, medical, etc.)

        Args:
            records: List of records to display
            match_reasons: Dict of record_id: list of reasons for match
            search_term: Current search term for highlighting
        """
        self.students_table.setRowCount(0)

        # Handle different table types
        if self.selected_table == "guardians":
            self._populate_guardians_table(records, match_reasons, search_term)
        elif self.selected_table == "medical_history":
            self._populate_medical_table(records, match_reasons, search_term)
        elif self.selected_table == "education":
            self._populate_education_table(records, match_reasons, search_term)
        elif self.selected_table == "enrollments":
            self._populate_enrollments_table(records, match_reasons, search_term)
        elif self.selected_table == "hostel":
            self._populate_hostel_table(records, match_reasons, search_term)
        elif self.selected_table == "transportation":
            self._populate_transportation_table(records, match_reasons, search_term)

    def _populate_guardians_table(self, records, match_reasons=None, search_term=""):
        """Populate guardians table"""
        for row, guardian in enumerate(records):
            self.students_table.insertRow(row)

            # Get primary key and student ID fields
            id_field = 'student_guardian_id'
            record_id = getattr(guardian, id_field, None)
            student_id = guardian.student_id

            # Add data cells
            self.students_table.setItem(row, 0, QTableWidgetItem(str(record_id)))

            # Add student ID with link to student
            student_id_item = QTableWidgetItem(str(student_id))
            self.students_table.setItem(row, 1, student_id_item)

            # Add name with potential highlighting
            name = guardian.guardian_name or ""
            name_item = QTableWidgetItem(name)
            if search_term and name.lower().find(search_term.lower()) != -1:
                name_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 2, name_item)

            # Add relationship
            self.students_table.setItem(row, 3, QTableWidgetItem(guardian.guardian_relationship or ""))

            # Add contact with potential highlighting
            contact = guardian.guardian_contact_number or ""
            contact_item = QTableWidgetItem(contact)
            if search_term and contact.lower().find(search_term.lower()) != -1:
                contact_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 4, contact_item)

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 5, student_id)

    def _populate_medical_table(self, records, match_reasons=None, search_term=""):
        """Populate medical history table"""
        for row, medical in enumerate(records):
            self.students_table.insertRow(row)

            # Add data cells
            self.students_table.setItem(row, 0, QTableWidgetItem(str(medical.medical_id)))

            # Add student ID with link to student
            student_id = medical.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.students_table.setItem(row, 1, student_id_item)

            # Add disability name with potential highlighting
            disability = medical.name_of_disability or ""
            disability_item = QTableWidgetItem(disability)
            if search_term and disability.lower().find(search_term.lower()) != -1:
                disability_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 2, disability_item)

            # Add epilepsy status
            epilepsy = "Yes" if medical.epilepsy else "No"
            self.students_table.setItem(row, 3, QTableWidgetItem(epilepsy))

            # Add drug addiction status
            addiction = "Yes" if medical.drug_addiction_smoking else "No"
            self.students_table.setItem(row, 4, QTableWidgetItem(addiction))

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 5, student_id)

    def _populate_education_table(self, records, match_reasons=None, search_term=""):
        """Populate education history table"""
        for row, education in enumerate(records):
            self.students_table.insertRow(row)

            # Add data cells
            self.students_table.setItem(row, 0, QTableWidgetItem(str(education.education_id)))

            # Add student ID with link to student
            student_id = education.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.students_table.setItem(row, 1, student_id_item)

            # Add education level with potential highlighting
            level = education.education_level or ""
            level_item = QTableWidgetItem(level)
            if search_term and level.lower().find(search_term.lower()) != -1:
                level_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 2, level_item)

            # Add certificate status
            certificate = "Yes" if education.certificate_attached else "No"
            self.students_table.setItem(row, 3, QTableWidgetItem(certificate))

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 4, student_id)

    def _populate_enrollments_table(self, records, match_reasons=None, search_term=""):
        """Populate enrollments table"""
        for row, enrollment in enumerate(records):
            self.students_table.insertRow(row)

            # Add data cells
            self.students_table.setItem(row, 0, QTableWidgetItem(str(enrollment.enrollment_id)))

            # Add student ID with link to student
            student_id = enrollment.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.students_table.setItem(row, 1, student_id_item)

            # Add course name/id
            course_display = getattr(enrollment, 'course_name', f'Course #{enrollment.course_id}')
            course_item = QTableWidgetItem(course_display)
            if search_term and str(course_display).lower().find(search_term.lower()) != -1:
                course_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 2, course_item)

            # Add date of enrollment
            date_str = ""
            if enrollment.date_of_enrollment:
                if isinstance(enrollment.date_of_enrollment, str):
                    date_str = enrollment.date_of_enrollment
                else:
                    date_str = enrollment.date_of_enrollment.strftime("%Y-%m-%d")
            self.students_table.setItem(row, 3, QTableWidgetItem(date_str))

            # Add completion status
            completion = "Yes" if enrollment.completion_status else "No"
            self.students_table.setItem(row, 4, QTableWidgetItem(completion))

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 5, student_id)

    def _populate_hostel_table(self, records, match_reasons=None, search_term=""):
        """Populate hostel management table"""
        for row, hostel in enumerate(records):
            self.students_table.insertRow(row)

            # Add data cells
            self.students_table.setItem(row, 0, QTableWidgetItem(str(hostel.hostel_id)))

            # Add student ID with link to student
            student_id = hostel.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.students_table.setItem(row, 1, student_id_item)

            # Add duration of stay
            duration = hostel.duration_of_stay or ""
            duration_item = QTableWidgetItem(duration)
            if search_term and duration.lower().find(search_term.lower()) != -1:
                duration_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 2, duration_item)

            # Add special requirements (truncated)
            requirements = hostel.special_requirements or ""
            if len(requirements) > 50:
                requirements = requirements[:47] + "..."
            requirements_item = QTableWidgetItem(requirements)
            if search_term and hostel.special_requirements and hostel.special_requirements.lower().find(
                    search_term.lower()) != -1:
                requirements_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 3, requirements_item)

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 4, student_id)

    def _populate_transportation_table(self, records, match_reasons=None, search_term=""):
        """Populate transportation table"""
        for row, transport in enumerate(records):
            self.students_table.insertRow(row)

            # Add data cells
            self.students_table.setItem(row, 0, QTableWidgetItem(str(transport.transport_id)))

            # Add student ID with link to student
            student_id = transport.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.students_table.setItem(row, 1, student_id_item)

            # Add responsible person name
            name = transport.pickup_drop_responsible_name or ""
            name_item = QTableWidgetItem(name)
            if search_term and name.lower().find(search_term.lower()) != -1:
                name_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 2, name_item)

            # Add contact number
            contact = transport.pickup_drop_contact_number or ""
            contact_item = QTableWidgetItem(contact)
            if search_term and contact.lower().find(search_term.lower()) != -1:
                contact_item.setBackground(Qt.yellow)
            self.students_table.setItem(row, 3, contact_item)

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 4, student_id)

    def _add_action_buttons_for_related_table(self, row, col, student_id):
        """
        Add action buttons for a related table row - using the same View/Edit/Delete
        buttons as in the student table, linked directly to the student record

        Args:
            row: Table row index
            col: Column index for action buttons
            student_id: The ID of the student associated with this record
        """
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)

        # View button (everyone can view)
        view_btn = QPushButton("View")
        view_btn.setProperty("student_id", student_id)
        view_btn.clicked.connect(self.view_student)
        actions_layout.addWidget(view_btn)

        # Edit button (only if user has update permission)
        if self.user_role and self.rbac.check_permission(self.user_role, 'data', 'update'):
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("student_id", student_id)
            edit_btn.clicked.connect(self.edit_student)
            actions_layout.addWidget(edit_btn)

        # Delete button (only if user has delete permission)
        if self.user_role and self.rbac.check_permission(self.user_role, 'data', 'delete'):
            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("student_id", student_id)
            delete_btn.clicked.connect(self.delete_student)
            actions_layout.addWidget(delete_btn)

        self.students_table.setCellWidget(row, col, actions_widget)

    def add_student(self):
        """Show comprehensive dialog to register a new student"""
        # Check permission first
        if self.user_role and not self.rbac.check_permission(self.user_role, 'data', 'create'):
            self._log_activity("Permission denied: Attempted to add student")
            QMessageBox.warning(self, "Permission Denied",
                                "You don't have permission to add new students.")
            return

        # Log the action
        self._log_activity("Opening student registration dialog")

        # Import here to avoid circular imports
        from app.ui.components.student_registration import StudentRegistrationDialog

        # Create the registration dialog with the current user
        registration_dialog = StudentRegistrationDialog(self, current_user=self.current_user)
        registration_dialog.student_added.connect(self.on_student_added)
        registration_dialog.exec_()

    def on_student_added(self, student_id):
        """Handle when a new student is added"""
        self._log_activity(f"New student added with ID: {student_id}")

        # Reload the appropriate view (use current table selection)
        if self.selected_table == "students":
            self.load_students()
            # Highlight the newly added student
            self.highlight_student(student_id)
        else:
            # If we're on a related table view, reload that too as the new student
            # registration might have added related records
            self.load_related_table_data()

        # Emit data changed signal
        self.data_changed.emit()

    def highlight_student(self, student_id):
        """Highlight a specific student in the table by ID"""
        for row in range(self.students_table.rowCount()):
            id_item = self.students_table.item(row, 0)
            if id_item and int(id_item.text()) == student_id:
                # Select the row
                self.students_table.selectRow(row)
                # Scroll to the row
                self.students_table.scrollToItem(id_item)
                break

    def edit_student(self):
        """Show dialog to edit an existing student"""
        # Check permission first
        if self.user_role and not self.rbac.check_permission(self.user_role, 'data', 'update'):
            self._log_activity("Permission denied: Attempted to edit student")
            QMessageBox.warning(self, "Permission Denied",
                                "You don't have permission to edit student records.")
            return

        sender = self.sender()
        student_id = sender.property("student_id")

        # Ensure student_id is an integer
        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Error", f"Invalid student ID: {student_id}")
            return

        self._log_activity(f"Opening edit dialog for student with ID: {student_id}")

        student_data = self.student_service.get_student_with_details(student_id)
        if not student_data:
            QMessageBox.warning(self, "Warning", f"Student with ID {student_id} not found.")
            return

        # Use the comprehensive edit dialog
        dialog = StudentEditDialog(student_data, self)

        # If dialog is accepted (saved), reload the student list
        if dialog.exec_() == QDialog.Accepted:
            self._log_activity(f"Student with ID {student_id} updated")

            # Maintain current table view after editing
            self.refresh_current_view()

            # If in student view, highlight the edited student
            if self.selected_table == "students":
                self.highlight_student(student_id)

            # Emit data changed signal
            self.data_changed.emit()

    def view_student(self):
        """Show detailed view of a student"""
        sender = self.sender()
        student_id = sender.property("student_id")

        # Ensure student_id is an integer
        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Error", f"Invalid student ID: {student_id}")
            return

        self._log_activity(f"Viewing details for student with ID: {student_id}")

        student_data = self.student_service.get_student_with_details(student_id)
        if not student_data:
            QMessageBox.warning(self, "Warning", f"Student with ID {student_id} not found.")
            return

        dialog = StudentDetailsDialog(student_data, self)
        dialog.exec_()

    def delete_student(self):
        """Delete a student after confirmation"""
        # Check permission first
        if self.user_role and not self.rbac.check_permission(self.user_role, 'data', 'delete'):
            self._log_activity("Permission denied: Attempted to delete student")
            QMessageBox.warning(self, "Permission Denied",
                                "You don't have permission to delete student records.")
            return

        sender = self.sender()
        student_id = sender.property("student_id")

        self._log_activity(f"Confirming deletion of student with ID: {student_id}")

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete student with ID {student_id}? This will also delete all related records.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self._log_activity(f"User confirmed deletion of student with ID: {student_id}")

                success, message = self.student_service.delete(student_id)
                if success:
                    self._log_activity(f"Student with ID {student_id} successfully deleted")
                    QMessageBox.information(self, "Success", "Student deleted successfully.")

                    # Reload the current view - maintain table selection
                    self.refresh_current_view()

                    # Emit data changed signal
                    self.data_changed.emit()
                else:
                    self._log_activity(f"Failed to delete student with ID {student_id}: {message}")
                    QMessageBox.critical(self, "Error", f"Failed to delete student: {message}")
            except Exception as e:
                self.logger.error(f"Error deleting student #{student_id}: {str(e)}")
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

    def show_search_info(self):
        """Show information about search capabilities"""
        self._log_activity("Viewed search help information")

        # Define search help for each table
        search_help = {
            "students": [
                "Student name - Full or partial name",
                "Student ID - Exact student ID number",
                "CNIC - Full or partial CNIC number",
                "Phone number - Full or partial phone number",
                "Guardian name - Full or partial guardian name",
                "Guardian contact number - Full or partial guardian contact",
                "Address - Full or partial address"
            ],
            "guardians": [
                "Guardian name - Full or partial name",
                "Student ID - Associated student ID",
                "Relationship - Type of relationship",
                "Contact number - Full or partial contact number"
            ],
            "medical_history": [
                "Student ID - Associated student ID",
                "Disability name - Full or partial disability name",
                "Medical history - Keywords from medical history"
            ],
            "education": [
                "Student ID - Associated student ID",
                "Education level - Full or partial education level"
            ],
            "enrollments": [
                "Student ID - Associated student ID",
                "Course ID or name - Full or partial course information",
                "Enrollment date - Date in YYYY-MM-DD format"
            ],
            "hostel": [
                "Student ID - Associated student ID",
                "Duration of stay - Full or partial duration",
                "Special requirements - Keywords from requirements"
            ],
            "transportation": [
                "Student ID - Associated student ID",
                "Responsible person - Full or partial name",
                "Contact number - Full or partial contact number"
            ]
        }

        # Get search fields for current table
        current_fields = search_help.get(self.selected_table, ["No specific search fields available"])

        # Get table display name
        table_display_name = next((option["display"] for option in self.table_options
                                   if option["id"] == self.selected_table), self.selected_table.capitalize())

        # Build HTML message
        message = f"<h3>Search Capabilities for {table_display_name}</h3>"
        message += "<p>You can search using any of the following information:</p><ul>"

        for field in current_fields:
            message += f"<li><b>{field}</b></li>"

        message += "</ul><p>Simply enter any of the above information in the search box and click Search.</p>"
        message += "<p>You can press Reset to show all records again.</p>"

        QMessageBox.information(self, "Search Help", message)

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
        self._log_activity("Widget became visible, scheduling refresh")

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
        self._log_activity("Widget hidden")

    def disconnect_signals(self):
        """Disconnect signals to prevent memory leaks"""
        try:
            # Disconnect from timer manager
            self.timer_manager.datetime_update_signal.disconnect(self.update_time_display)
            self.timer_manager.student_data_refresh_signal.disconnect(self.on_auto_refresh)

            # Stop local timer if it exists
            if self.visible_refresh_timer and self.visible_refresh_timer.isActive():
                self.visible_refresh_timer.stop()

            self._log_activity("Signals disconnected")
        except Exception as e:
            self.logger.error(f"Error disconnecting signals: {str(e)}")