from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox,
                             QDateEdit, QComboBox, QCheckBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIntValidator
from app.services.student_service import StudentService
from app.utils.logger import Logger
import datetime


class StudentForm(QWidget):
    """Form for adding/editing student personal information"""

    def __init__(self, parent=None, student_data=None):
        """
        Initialize the form

        Args:
            parent: Parent widget
            student_data: Dictionary with student data for editing (optional)
        """
        super().__init__(parent)
        self.student_data = student_data
        self.student_service = StudentService()
        self.logger = Logger()

        self.init_ui()

        # If student data is provided, populate form for editing
        if self.student_data:
            self.populate_form()

    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)

        # Create scroll area for form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)

        # Personal Information Group
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout(personal_group)

        # Student name
        self.name_input = QLineEdit()
        personal_layout.addRow("Student Name*:", self.name_input)

        # CNIC
        self.cnic_input = QLineEdit()
        personal_layout.addRow("CNIC:", self.cnic_input)

        # Gender
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "M", "F", "O"])
        personal_layout.addRow("Gender:", self.gender_combo)

        # Age
        self.age_input = QLineEdit()
        self.age_input.setValidator(QIntValidator(0, 150))
        personal_layout.addRow("Age:", self.age_input)

        # Date of birth
        self.dob_edit = QDateEdit(calendarPopup=True)
        self.dob_edit.setDate(QDate.currentDate().addYears(-20))
        self.dob_edit.setDisplayFormat("yyyy-MM-dd")
        personal_layout.addRow("Date of Birth:", self.dob_edit)

        # Phone
        self.phone_input = QLineEdit()
        personal_layout.addRow("Phone:", self.phone_input)

        # Address
        self.address_input = QLineEdit()
        personal_layout.addRow("Address:", self.address_input)

        # Contact number
        self.contact_input = QLineEdit()
        personal_layout.addRow("Contact Number:", self.contact_input)

        # Occupation
        self.occupation_input = QLineEdit()
        personal_layout.addRow("Occupation:", self.occupation_input)

        # Add personal group to form
        form_layout.addRow(personal_group)

        # Admission Information Group
        admission_group = QGroupBox("Admission Information")
        admission_layout = QFormLayout(admission_group)

        # Admission type
        self.admission_type_combo = QComboBox()
        self.admission_type_combo.addItems(["", "Regular", "Special", "Transfer"])
        admission_layout.addRow("Admission Type:", self.admission_type_combo)

        # Admission date
        self.admission_date_edit = QDateEdit(calendarPopup=True)
        self.admission_date_edit.setDate(QDate.currentDate())
        self.admission_date_edit.setDisplayFormat("yyyy-MM-dd")
        admission_layout.addRow("Admission Date:", self.admission_date_edit)

        # Accompanied by assistant
        self.assistant_check = QCheckBox()
        admission_layout.addRow("Accompanied by Assistant:", self.assistant_check)

        # Affidavit attached
        self.affidavit_check = QCheckBox()
        admission_layout.addRow("Affidavit Attached:", self.affidavit_check)

        # Add admission group to form
        form_layout.addRow(admission_group)

        # Add note about required fields
        form_layout.addRow("* Required fields", QLabel())

        # Set the scroll widget and add to main layout
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

    def populate_form(self):
        """Populate the form with existing student data"""
        if not self.student_data:
            print("Error: No student data provided to form")
            return

        print(f"Populating form with student data: {self.student_data}")
        print(f"Student ID: {self.student_data.get('student_id')}")

        # Set values from student data
        self.name_input.setText(self.student_data.get('student_name', ''))
        self.cnic_input.setText(self.student_data.get('cnic', ''))

        # Set gender
        gender_index = self.gender_combo.findText(self.student_data.get('gender', ''))
        if gender_index >= 0:
            self.gender_combo.setCurrentIndex(gender_index)

        # Set age
        age = self.student_data.get('age')
        if age is not None:
            self.age_input.setText(str(age))

        # Set date of birth
        dob = self.student_data.get('date_of_birth')
        if dob:
            if isinstance(dob, str):
                try:
                    dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
                    self.dob_edit.setDate(QDate(dob_date.year, dob_date.month, dob_date.day))
                except ValueError:
                    pass
            elif isinstance(dob, datetime.date):
                self.dob_edit.setDate(QDate(dob.year, dob.month, dob.day))

        # Set other fields
        self.phone_input.setText(self.student_data.get('phone', ''))
        self.address_input.setText(self.student_data.get('address', ''))
        self.contact_input.setText(self.student_data.get('student_contact_no', ''))
        self.occupation_input.setText(self.student_data.get('student_occupation', ''))

        # Set admission type
        admission_index = self.admission_type_combo.findText(self.student_data.get('admission_type', ''))
        if admission_index >= 0:
            self.admission_type_combo.setCurrentIndex(admission_index)

        # Set admission date
        admission_date = self.student_data.get('admission_date')
        if admission_date:
            if isinstance(admission_date, str):
                try:
                    ad_date = datetime.datetime.strptime(admission_date, '%Y-%m-%d').date()
                    self.admission_date_edit.setDate(QDate(ad_date.year, ad_date.month, ad_date.day))
                except ValueError:
                    pass
            elif isinstance(admission_date, datetime.date):
                self.admission_date_edit.setDate(QDate(admission_date.year, admission_date.month, admission_date.day))

        # Set checkboxes
        self.assistant_check.setChecked(bool(self.student_data.get('accompanied_by_assistant')))
        self.affidavit_check.setChecked(bool(self.student_data.get('affidavit_attached')))

    def get_form_data(self):
        """Get data from form fields"""
        data = {
            'student_name': self.name_input.text(),
            'cnic': self.cnic_input.text(),
            'gender': self.gender_combo.currentText(),
            'age': int(self.age_input.text()) if self.age_input.text() else None,
            'date_of_birth': self.dob_edit.date().toString('yyyy-MM-dd'),
            'phone': self.phone_input.text(),
            'address': self.address_input.text(),
            'student_contact_no': self.contact_input.text(),
            'student_occupation': self.occupation_input.text(),
            'admission_type': self.admission_type_combo.currentText(),
            'admission_date': self.admission_date_edit.date().toString('yyyy-MM-dd'),
            'accompanied_by_assistant': self.assistant_check.isChecked(),
            'affidavit_attached': self.affidavit_check.isChecked()
        }

        return data

    def save_student(self):
        """Save the student data"""
        # Get data from form
        form_data = self.get_form_data()

        # Validate required fields
        if not form_data['student_name']:
            QMessageBox.warning(self, "Validation Error", "Student name is required.")
            return

        try:
            if self.student_data and 'student_id' in self.student_data:
                # Update existing student
                success, result = self.student_service.update(self.student_data['student_id'], form_data)
                if success:
                    QMessageBox.information(self, "Success", "Student updated successfully.")
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to update student: {result}")
            else:
                # Create new student
                success, result = self.student_service.create_student(form_data)
                if success:
                    QMessageBox.information(self, "Success", "Student added successfully.")
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to add student: {result}")
        except Exception as e:
            self.logger.error(f"Error saving student: {str(e)}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")