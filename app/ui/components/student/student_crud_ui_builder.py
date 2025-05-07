from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QComboBox)
from PyQt5.QtGui import QFont

class StudentCrudUIBuilder:
    """Responsible for building and updating the UI elements of the StudentCrudWidget"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        
    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self.parent)

        # Header with title, table selector, and actions
        header_layout = QHBoxLayout()

        # Add table selector dropdown
        table_selector_layout = QHBoxLayout()
        table_selector_label = QLabel("View:")
        self.parent.table_selector = QComboBox()

        # Populate table selector dynamically
        for option in self.parent.table_options:
            self.parent.table_selector.addItem(option["display"], option["id"])

        # Connect table selector to change handler
        self.parent.table_selector.currentIndexChanged.connect(self.parent.on_table_changed)

        table_selector_layout.addWidget(table_selector_label)
        table_selector_layout.addWidget(self.parent.table_selector)

        # Title label
        self.parent.title_label = QLabel("Student Management")
        self.parent.title_label.setFont(QFont("Arial", 14, QFont.Bold))

        # Show current user and time
        self.parent.user_time_label = QLabel(f"User: {self.parent.current_user} | {self.parent.utils._get_current_time_utc()}")

        # Connect to datetime update signal to keep time current
        self.parent.timer_manager.datetime_update_signal.connect(self.parent.update_time_display)

        # Add Student button - only show if user has permission
        self.parent.add_btn = QPushButton("Add Student")
        self.parent.add_btn.clicked.connect(self.parent.add_student)

        # Hide button if user doesn't have create permission
        if self.parent.user_role and not self.parent.rbac.check_permission(self.parent.user_role, 'data', 'create'):
            self.parent.add_btn.setVisible(False)

        header_layout.addLayout(table_selector_layout)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.parent.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.parent.user_time_label)
        header_layout.addWidget(self.parent.add_btn)

        main_layout.addLayout(header_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.parent.search_input = QLineEdit()
        self.parent.search_input.setPlaceholderText("Search by name, ID, CNIC, phone or guardian...")
        self.parent.search_input.returnPressed.connect(self.parent.search_students)

        # Add search help button
        search_info_btn = QPushButton("?")
        search_info_btn.setMaximumWidth(25)
        search_info_btn.clicked.connect(self.parent.show_search_info)

        self.parent.search_btn = QPushButton("Search")
        self.parent.search_btn.clicked.connect(self.parent.search_students)

        self.parent.reset_btn = QPushButton("Reset")
        self.parent.reset_btn.clicked.connect(self.parent.on_reset_clicked)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.parent.search_input, 1)
        search_layout.addWidget(search_info_btn)
        search_layout.addWidget(self.parent.search_btn)
        search_layout.addWidget(self.parent.reset_btn)

        main_layout.addLayout(search_layout)

        # Students table
        self.parent.students_table = QTableWidget()
        self.parent.students_table.setColumnCount(8)
        self.parent.students_table.setHorizontalHeaderLabels([
            "ID", "Name", "Gender", "Age", "CNIC",
            "Admission Date", "Phone", "Actions"
        ])
        self.parent.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.parent.students_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.parent.students_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.parent.students_table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.parent.students_table)

        # Status bar
        self.parent.status_label = QLabel("Ready")
        main_layout.addWidget(self.parent.status_label)

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

        self.parent.title_label.setText(titles.get(self.parent.selected_table, "Student Management"))

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

        self.parent.search_input.setPlaceholderText(placeholders.get(self.parent.selected_table, "Search..."))

        # Configure table columns based on selected table
        self.configure_table_for_selection()

    def configure_table_for_selection(self):
        """Configure table columns based on selected table"""
        # Clear existing data
        self.parent.students_table.clearContents()
        self.parent.students_table.setRowCount(0)

        # Configure columns based on table selection
        if self.parent.selected_table == "students":
            self.parent.students_table.setColumnCount(8)
            self.parent.students_table.setHorizontalHeaderLabels([
                "ID", "Name", "Gender", "Age", "CNIC",
                "Admission Date", "Phone", "Actions"
            ])
            self.parent.students_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        elif self.parent.selected_table == "guardians":
            self.parent.students_table.setColumnCount(6)  # 5 data columns + Actions
            self.parent.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Name", "Relationship", "Contact", "Actions"
            ])
            self.parent.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.parent.selected_table == "medical_history":
            self.parent.students_table.setColumnCount(6)  # 5 data columns + Actions
            self.parent.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Disability Name", "Epilepsy", "Drug Addiction", "Actions"
            ])
            self.parent.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.parent.selected_table == "education":
            self.parent.students_table.setColumnCount(5)  # 4 data columns + Actions
            self.parent.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Education Level", "Certificate", "Actions"
            ])
            self.parent.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.parent.selected_table == "enrollments":
            self.parent.students_table.setColumnCount(6)  # 5 data columns + Actions
            self.parent.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Course", "Enrollment Date", "Completed", "Actions"
            ])
            self.parent.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.parent.selected_table == "hostel":
            self.parent.students_table.setColumnCount(5)  # 4 data columns + Actions
            self.parent.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Duration of Stay", "Requirements", "Actions"
            ])
            self.parent.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        elif self.parent.selected_table == "transportation":
            self.parent.students_table.setColumnCount(5)  # 4 data columns + Actions
            self.parent.students_table.setHorizontalHeaderLabels([
                "ID", "Student ID", "Responsible Person", "Contact", "Actions"
            ])
            self.parent.students_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)