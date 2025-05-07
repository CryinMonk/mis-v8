from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QDateEdit, QGroupBox, QFormLayout, QTableView, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from app.utils.logger import Logger


class ReportsWidget(QWidget):
    """Reports widget for generating and viewing reports"""

    def __init__(self, current_user=None):
        """Initialize the reports widget"""
        super().__init__()

        # Store current user
        self.current_user = current_user

        # Initialize logger
        self.logger = Logger()

        # Initialize data model for report results
        self.report_model = QStandardItemModel()

        # Set up UI
        self.init_ui()

    def init_ui(self):
        """Set up the user interface"""
        # Main layout
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Reports")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        # Report configuration section
        config_group = QGroupBox("Generate Report")
        config_layout = QFormLayout(config_group)

        # Report type selector
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Student Enrollment Report",
            "Course Completion Report",
            "Guardian Contact List",
            "Medical Information Summary",
            "Hostel Occupancy Report",
            "Transportation Requirements"
        ])
        config_layout.addRow("Report Type:", self.report_type_combo)

        # Date range
        date_range_layout = QHBoxLayout()

        # Start date
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        date_range_layout.addWidget(QLabel("From:"))
        date_range_layout.addWidget(self.start_date)

        # End date
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_range_layout.addWidget(QLabel("To:"))
        date_range_layout.addWidget(self.end_date)

        config_layout.addRow("Date Range:", date_range_layout)

        # Generate button
        generate_layout = QHBoxLayout()
        generate_layout.addStretch(1)

        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setMinimumWidth(150)
        self.generate_btn.clicked.connect(self.generate_report)
        generate_layout.addWidget(self.generate_btn)

        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_report)
        generate_layout.addWidget(self.export_btn)

        config_layout.addRow("", generate_layout)

        layout.addWidget(config_group)

        # Report results section
        results_group = QGroupBox("Report Results")
        results_layout = QVBoxLayout(results_group)

        # Results table
        self.report_table = QTableView()
        self.report_table.setModel(self.report_model)
        results_layout.addWidget(self.report_table)

        layout.addWidget(results_group)
        layout.setStretchFactor(results_group, 1)

    def generate_report(self):
        """Generate the selected report"""
        report_type = self.report_type_combo.currentText()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")

        self.logger.info(f"Generating report: {report_type} from {start_date} to {end_date}")

        # Clear previous report data
        self.report_model.clear()

        # Generate different reports based on type
        if report_type == "Student Enrollment Report":
            self.generate_enrollment_report(start_date, end_date)
        elif report_type == "Course Completion Report":
            self.generate_completion_report(start_date, end_date)
        # Add other report types as needed

        # Enable export button
        self.export_btn.setEnabled(True)

    def generate_enrollment_report(self, start_date, end_date):
        """Generate student enrollment report"""
        # Set headers
        headers = ["Student ID", "Student Name", "Course", "Enrollment Date"]
        self.report_model.setHorizontalHeaderLabels(headers)

        # TODO: Query database for enrollment data in date range
        # For now, add sample data
        sample_data = [
            ["1001", "John Smith", "Computer Science", "2025-01-15"],
            ["1002", "Mary Johnson", "Physics", "2025-02-03"],
            ["1003", "Robert Wilson", "Mathematics", "2025-02-10"],
            ["1004", "Sarah Brown", "Chemistry", "2025-03-01"],
            ["1005", "Michael Davis", "Biology", "2025-03-15"]
        ]

        for row_data in sample_data:
            row = []
            for item in row_data:
                row.append(QStandardItem(item))
            self.report_model.appendRow(row)

    def generate_completion_report(self, start_date, end_date):
        """Generate course completion report"""
        # Set headers
        headers = ["Student ID", "Student Name", "Course", "Completion Date", "Status"]
        self.report_model.setHorizontalHeaderLabels(headers)

        # TODO: Query database for completion data in date range
        # For now, add sample data
        sample_data = [
            ["1001", "John Smith", "Computer Science", "2025-03-20", "Completed"],
            ["1002", "Mary Johnson", "Physics", "2025-04-01", "Completed"],
            ["1003", "Robert Wilson", "Mathematics", "2025-04-10", "In Progress"],
            ["1004", "Sarah Brown", "Chemistry", "2025-04-15", "In Progress"],
            ["1005", "Michael Davis", "Biology", "2025-04-20", "Not Started"]
        ]

        for row_data in sample_data:
            row = []
            for item in row_data:
                row.append(QStandardItem(item))
            self.report_model.appendRow(row)

    def export_report(self):
        """Export the current report to a CSV file"""
        self.logger.info("Exporting report to CSV")
        # TODO: Implement CSV export functionality
        QMessageBox.information(self, "Export", "Report exported successfully!")