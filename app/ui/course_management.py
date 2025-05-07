from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
                             QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from app.services.course_service import CourseService
from app.utils.logger import Logger


class CourseManagement(QWidget):
    """Course management widget for managing courses"""

    def __init__(self, current_user=None):
        """Initialize the course management widget"""
        super().__init__()

        # Store current user
        self.current_user = current_user

        # Initialize services
        self.course_service = CourseService()

        # Initialize logger
        self.logger = Logger()

        # Set up UI
        self.init_ui()

        # Load courses
        self.load_courses()

    def init_ui(self):
        """Set up the user interface"""
        # Main layout
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Course Management")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        # Search and actions bar
        actions_layout = QHBoxLayout()

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search courses...")
        self.search_input.textChanged.connect(self.search_courses)
        actions_layout.addWidget(self.search_input)

        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Courses", "Active Courses", "Inactive Courses"])
        self.filter_combo.currentIndexChanged.connect(self.filter_courses)
        actions_layout.addWidget(self.filter_combo)

        # Add course button
        add_btn = QPushButton("Add Course")
        add_btn.clicked.connect(self.add_course)
        actions_layout.addWidget(add_btn)

        layout.addLayout(actions_layout)

        # Courses table
        self.courses_table = QTableWidget(0, 5)  # Rows, columns
        self.courses_table.setHorizontalHeaderLabels([
            "ID", "Course Name", "Duration", "Status", "Actions"
        ])

        # Set column widths
        header = self.courses_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Duration
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Actions

        layout.addWidget(self.courses_table)

    def load_courses(self):
        """Load courses from database"""
        try:
            # Clear table
            self.courses_table.setRowCount(0)

            # Fetch courses
            courses = self.course_service.read_all()

            # Populate table
            for row, course in enumerate(courses):
                self.courses_table.insertRow(row)

                # ID
                id_item = QTableWidgetItem(str(course.course_id))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.courses_table.setItem(row, 0, id_item)

                # Name
                name_item = QTableWidgetItem(course.course_name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.courses_table.setItem(row, 1, name_item)

                # Duration
                duration_item = QTableWidgetItem(str(course.duration))
                duration_item.setFlags(duration_item.flags() & ~Qt.ItemIsEditable)
                self.courses_table.setItem(row, 2, duration_item)

                # Status
                status_text = "Active" if course.is_active else "Inactive"
                status_item = QTableWidgetItem(status_text)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.courses_table.setItem(row, 3, status_item)

                # Actions cell with buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 2, 2, 2)

                # Edit button
                edit_btn = QPushButton("Edit")
                edit_btn.setProperty("course_id", course.course_id)
                edit_btn.clicked.connect(self.edit_course)
                actions_layout.addWidget(edit_btn)

                # Delete button
                delete_btn = QPushButton("Delete")
                delete_btn.setProperty("course_id", course.course_id)
                delete_btn.clicked.connect(self.delete_course)
                actions_layout.addWidget(delete_btn)

                self.courses_table.setCellWidget(row, 4, actions_widget)

            self.logger.info(f"Loaded {len(courses)} courses")

        except Exception as e:
            self.logger.error(f"Error loading courses: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load courses: {str(e)}")

    def search_courses(self):
        """Filter courses based on search text"""
        search_text = self.search_input.text().lower()

        # Show/hide rows based on search text
        for row in range(self.courses_table.rowCount()):
            show_row = False

            # Check course name column
            name_item = self.courses_table.item(row, 1)
            if name_item and search_text in name_item.text().lower():
                show_row = True

            self.courses_table.setRowHidden(row, not show_row)

    def filter_courses(self):
        """Filter courses based on selected filter"""
        filter_option = self.filter_combo.currentText()

        # Show/hide rows based on filter option
        for row in range(self.courses_table.rowCount()):
            show_row = True

            # Check status column
            status_item = self.courses_table.item(row, 3)
            if status_item:
                status_text = status_item.text()

                if filter_option == "Active Courses" and status_text != "Active":
                    show_row = False
                elif filter_option == "Inactive Courses" and status_text != "Inactive":
                    show_row = False

            self.courses_table.setRowHidden(row, not show_row)

    def add_course(self):
        """Open dialog to add a new course"""
        self.logger.info("Opening dialog to add new course")
        # TODO: Implement course dialog
        # You can create a CourseDialog class similar to StudentRegistrationDialog

    def edit_course(self):
        """Open dialog to edit an existing course"""
        sender = self.sender()
        course_id = sender.property("course_id")
        self.logger.info(f"Opening dialog to edit course ID: {course_id}")
        # TODO: Implement course editing dialog

    def delete_course(self):
        """Delete a course after confirmation"""
        sender = self.sender()
        course_id = sender.property("course_id")

        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the course with ID {course_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.logger.info(f"Deleting course ID: {course_id}")

            # Delete course
            success, message = self.course_service.delete(course_id)

            if success:
                QMessageBox.information(self, "Success", "Course deleted successfully")
                self.load_courses()  # Refresh table
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete course: {message}")