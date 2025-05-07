from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox,
                             QDateEdit, QComboBox, QCheckBox, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QScrollArea, QTextEdit, QWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIntValidator
from app.services.student_service import StudentService
from app.services.medical_service import MedicalService
from app.services.education_service import EducationService
from app.services.guardian_service import GuardianService
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService
from app.services.hostel_service import HostelService
from app.services.transportation_service import TransportationService
from app.ui.components.student_form import StudentForm
from app.utils.logger import Logger
import datetime


class StudentEditDialog(QDialog):
    """Dialog for editing all student information"""

    def __init__(self, student_data, parent=None):
        super().__init__(parent)
        self.student_data = student_data
        self.student_service = StudentService()
        self.medical_service = MedicalService()
        self.education_service = EducationService()
        self.guardian_service = GuardianService()
        self.course_service = CourseService()
        self.enrollment_service = EnrollmentService()
        self.hostel_service = HostelService()
        self.transportation_service = TransportationService()
        self.logger = Logger()

        self.setWindowTitle(f"Edit Student: {student_data.get('student_name', 'Unknown')}")
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)

        # Create tabs for different sections of student data
        tab_widget = QTabWidget()

        # Personal information tab
        self.personal_tab = QWidget()
        self.personal_form = StudentForm(self.personal_tab, self.student_data)
        personal_layout = QVBoxLayout(self.personal_tab)
        personal_layout.addWidget(self.personal_form)
        tab_widget.addTab(self.personal_tab, "Personal Information")

        # Education history tab (if available)
        if 'education_history' in self.student_data:
            self.education_tab = QWidget()
            education_layout = QVBoxLayout(self.education_tab)
            self.init_education_form(education_layout)
            tab_widget.addTab(self.education_tab, "Education")

        # Enrollments tab (if available)
        self.enrollment_tab = QWidget()
        enrollment_layout = QVBoxLayout(self.enrollment_tab)
        self.init_enrollment_form(enrollment_layout)
        tab_widget.addTab(self.enrollment_tab, "Enrollments")

        # Medical history tab (if available)
        if 'medical_history' in self.student_data:
            self.medical_tab = QWidget()
            medical_layout = QVBoxLayout(self.medical_tab)
            self.init_medical_form(medical_layout)
            tab_widget.addTab(self.medical_tab, "Medical History")

        # Guardians tab (if available)
        self.guardian_tab = QWidget()
        guardian_layout = QVBoxLayout(self.guardian_tab)
        self.init_guardian_form(guardian_layout)
        tab_widget.addTab(self.guardian_tab, "Guardians")

        # Hostel tab (if available)
        if 'hostel_info' in self.student_data:
            self.hostel_tab = QWidget()
            hostel_layout = QVBoxLayout(self.hostel_tab)
            self.init_hostel_form(hostel_layout)
            tab_widget.addTab(self.hostel_tab, "Hostel")

        # Transportation tab (if available)
        if 'transportation' in self.student_data:
            self.transport_tab = QWidget()
            transport_layout = QVBoxLayout(self.transport_tab)
            self.init_transport_form(transport_layout)
            tab_widget.addTab(self.transport_tab, "Transportation")

        main_layout.addWidget(tab_widget)

        # Button layout
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save All Changes")
        self.save_btn.clicked.connect(self.save_all_changes)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def init_education_form(self, layout):
        """Initialize education history edit form"""
        # Create form group
        form_group = QGroupBox("Education History")
        form_layout = QFormLayout(form_group)

        # Education level
        self.education_level_input = QLineEdit()
        form_layout.addRow("Education Level:", self.education_level_input)

        # Certificate attached
        self.certificate_check = QCheckBox()
        form_layout.addRow("Certificate Attached:", self.certificate_check)

        # Populate with existing data if available
        if self.student_data['education_history']:
            education = self.student_data['education_history'][0]  # Get the first record
            self.education_level_input.setText(education.get('education_level', ''))
            self.certificate_check.setChecked(education.get('certificate_attached', False))

            # Store the education ID if it exists
            self.education_id = education.get('education_id')
        else:
            self.education_id = None

        layout.addWidget(form_group)

    def init_enrollment_form(self, layout):
        """Initialize enrollment edit form"""
        # Create form group
        form_group = QGroupBox("Course Enrollment")
        form_layout = QFormLayout(form_group)

        # Course selection
        self.course_combo = QComboBox()
        # Add empty option
        self.course_combo.addItem("-- Select Course --", "")
        # Add courses from database
        try:
            courses = self.course_service.get_all_courses()
            for course in courses:
                self.course_combo.addItem(course.course_name, course.course_id)
        except Exception as e:
            self.logger.error(f"Error loading courses: {str(e)}")

        form_layout.addRow("Course:", self.course_combo)

        # Date of enrollment
        self.enrollment_date_edit = QDateEdit(calendarPopup=True)
        self.enrollment_date_edit.setDate(QDate.currentDate())
        self.enrollment_date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date of Enrollment:", self.enrollment_date_edit)

        # Completion status
        self.completion_check = QCheckBox()
        form_layout.addRow("Completed:", self.completion_check)

        # Populate with existing data if available
        if 'enrollments' in self.student_data and self.student_data['enrollments']:
            enrollment = self.student_data['enrollments'][0]  # Get the first record

            # Set the course
            course_id = enrollment.get('course_id')
            if course_id:
                index = self.course_combo.findData(course_id)
                if index >= 0:
                    self.course_combo.setCurrentIndex(index)

            # Set the date
            date_str = enrollment.get('date_of_enrollment')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                        self.enrollment_date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                    elif isinstance(date_str, datetime.date):
                        self.enrollment_date_edit.setDate(QDate(date_str.year, date_str.month, date_str.day))
                except Exception as e:
                    self.logger.error(f"Error parsing date: {str(e)}")

            # Set completion status
            self.completion_check.setChecked(enrollment.get('completion_status', False))

            # Store the enrollment ID if it exists
            self.enrollment_id = enrollment.get('enrollment_id')
        else:
            self.enrollment_id = None

        layout.addWidget(form_group)

    def init_medical_form(self, layout):
        """Initialize medical history edit form"""
        # Create form group
        form_group = QGroupBox("Medical History")
        form_layout = QFormLayout(form_group)

        # Name of disability
        self.disability_input = QLineEdit()
        form_layout.addRow("Name of Disability:", self.disability_input)

        # Brief medical history
        self.medical_history_input = QTextEdit()
        form_layout.addRow("Brief Medical History:", self.medical_history_input)

        # Regular medication
        self.medication_input = QTextEdit()
        form_layout.addRow("Regular Medication:", self.medication_input)

        # Epilepsy
        self.epilepsy_check = QCheckBox()
        form_layout.addRow("Epilepsy:", self.epilepsy_check)

        # Communicable disease
        self.disease_input = QTextEdit()
        form_layout.addRow("Communicable Disease:", self.disease_input)

        # Drug addiction/smoking
        self.addiction_check = QCheckBox()
        form_layout.addRow("Drug Addiction/Smoking:", self.addiction_check)

        # Assistive device
        self.device_input = QLineEdit()
        form_layout.addRow("Assistive Device Used:", self.device_input)

        # Populate with existing data if available
        if self.student_data['medical_history']:
            medical = self.student_data['medical_history'][0]  # Get the first record
            self.disability_input.setText(medical.get('name_of_disability', ''))
            self.medical_history_input.setPlainText(medical.get('brief_medical_history', ''))
            self.medication_input.setPlainText(medical.get('regular_medication', ''))
            self.epilepsy_check.setChecked(medical.get('epilepsy', False))
            self.disease_input.setPlainText(medical.get('communicable_disease', ''))
            self.addiction_check.setChecked(medical.get('drug_addiction_smoking', False))
            self.device_input.setText(medical.get('assistive_device_used', ''))

            # Store the medical ID if it exists
            self.medical_id = medical.get('medical_id')
        else:
            self.medical_id = None

        layout.addWidget(form_group)

    # In the init_guardian_form method in student_edit_dialog.py
    def init_guardian_form(self, layout):
        """Initialize guardian edit form"""
        # Create form group
        form_group = QGroupBox("Guardian Information")
        form_layout = QFormLayout(form_group)

        # Guardian name
        self.guardian_name_input = QLineEdit()
        form_layout.addRow("Guardian Name:", self.guardian_name_input)

        # Relationship
        self.guardian_relationship_input = QLineEdit()
        form_layout.addRow("Relationship:", self.guardian_relationship_input)

        # Contact number
        self.guardian_contact_input = QLineEdit()
        form_layout.addRow("Contact Number:", self.guardian_contact_input)

        # Populate with existing data if available
        if 'guardians' in self.student_data and self.student_data['guardians']:
            guardian = self.student_data['guardians'][0]  # Get the first record
            self.guardian_name_input.setText(guardian.get('guardian_name', ''))
            self.guardian_relationship_input.setText(guardian.get('guardian_relationship', ''))
            self.guardian_contact_input.setText(guardian.get('guardian_contact_number', ''))

            # Store the guardian ID using the correct field name
            self.guardian_id = guardian.get('student_guardian_id')

            # Add a label showing this is an existing record
            if self.guardian_id:
                note_label = QLabel(f"Editing existing guardian record (ID: {self.guardian_id})")
                note_label.setStyleSheet("color: blue;")
                form_layout.addRow(note_label)
        else:
            self.guardian_id = None

        layout.addWidget(form_group)

    def init_hostel_form(self, layout):
        """Initialize hostel edit form"""
        # Create form group
        form_group = QGroupBox("Hostel Information")
        form_layout = QFormLayout(form_group)

        # Duration of stay
        self.duration_input = QLineEdit()
        form_layout.addRow("Duration of Stay:", self.duration_input)

        # Special requirements
        self.requirements_input = QTextEdit()
        form_layout.addRow("Special Requirements:", self.requirements_input)

        # Populate with existing data if available
        if self.student_data['hostel_info']:
            hostel = self.student_data['hostel_info'][0]  # Get the first record
            self.duration_input.setText(hostel.get('duration_of_stay', ''))
            self.requirements_input.setPlainText(hostel.get('special_requirements', ''))

            # Store the hostel ID if it exists
            self.hostel_id = hostel.get('hostel_id')
        else:
            self.hostel_id = None

        layout.addWidget(form_group)

    # In the init_transport_form method in student_edit_dialog.py
    def init_transport_form(self, layout):
        """Initialize transportation edit form"""
        # Create form group
        form_group = QGroupBox("Transportation Information")
        form_layout = QFormLayout(form_group)

        # Responsible person name
        self.responsible_name_input = QLineEdit()
        form_layout.addRow("Responsible Person Name:", self.responsible_name_input)

        # Contact number
        self.transport_contact_input = QLineEdit()
        form_layout.addRow("Contact Number:", self.transport_contact_input)

        # Populate with existing data if available
        if 'transportation' in self.student_data and self.student_data['transportation']:
            transport = self.student_data['transportation'][0]  # Get the first record
            self.responsible_name_input.setText(transport.get('pickup_drop_responsible_name', ''))
            self.transport_contact_input.setText(transport.get('pickup_drop_contact_number', ''))

            # Store the transport ID using the correct field name (assuming it's transportation_id)
            # If the field name is different, replace with the correct one
            self.transport_id = transport.get('transportation_id')

            # Add a label showing this is an existing record
            if self.transport_id:
                note_label = QLabel(f"Editing existing transportation record (ID: {self.transport_id})")
                note_label.setStyleSheet("color: blue;")
                form_layout.addRow(note_label)
        else:
            self.transport_id = None

        layout.addWidget(form_group)

    def save_all_changes(self):
        """Save all changes to the database"""
        try:
            # Get student ID
            student_id = self.student_data['student_id']
            self.logger.info(f"Saving changes for student ID: {student_id}")

            # 1. Save personal information
            personal_data = self.personal_form.get_form_data()
            success, result = self.student_service.update(student_id, personal_data)
            if not success:
                QMessageBox.critical(self, "Error", f"Failed to update personal information: {result}")
                return

            # 2. Save education information if form was initialized
            if hasattr(self, 'education_level_input'):
                education_data = {
                    'education_level': self.education_level_input.text(),
                    'certificate_attached': self.certificate_check.isChecked(),
                    'student_id': student_id
                }

                if 'education_history' in self.student_data and self.student_data['education_history']:
                    education_id = self.student_data['education_history'][0].get('education_id')
                    if education_id:
                        # Update existing record
                        success, result = self.education_service.update(education_id, education_data)
                    else:
                        # Create new record if ID is missing
                        success, result = self.education_service.create_education_record(education_data)
                else:
                    # Create new record if no education history
                    success, result = self.education_service.create_education_record(education_data)

                if not success:
                    QMessageBox.warning(self, "Warning", f"Education information update failed: {result}")

            # 3. Save enrollment information if form was initialized
            if hasattr(self, 'course_combo'):
                course_id = self.course_combo.currentData()
                if course_id:  # Only save if a course is selected
                    enrollment_data = {
                        'course_id': course_id,
                        'date_of_enrollment': self.enrollment_date_edit.date().toString('yyyy-MM-dd'),
                        'completion_status': self.completion_check.isChecked(),
                        'student_id': student_id
                    }

                    if 'enrollments' in self.student_data and self.student_data['enrollments']:
                        enrollment_id = self.student_data['enrollments'][0].get('enrollment_id')
                        if enrollment_id:
                            # Update existing record
                            success, result = self.enrollment_service.update(enrollment_id, enrollment_data)
                        else:
                            # Create new record if ID is missing
                            success, result = self.enrollment_service.create_enrollment(enrollment_data)
                    else:
                        # Create new record if no enrollments
                        success, result = self.enrollment_service.create_enrollment(enrollment_data)

                    if not success:
                        QMessageBox.warning(self, "Warning", f"Enrollment information update failed: {result}")

            # 4. Save medical information if form was initialized
            if hasattr(self, 'disability_input'):
                medical_data = {
                    'name_of_disability': self.disability_input.text(),
                    'brief_medical_history': self.medical_history_input.toPlainText(),
                    'regular_medication': self.medication_input.toPlainText(),
                    'epilepsy': self.epilepsy_check.isChecked(),
                    'communicable_disease': self.disease_input.toPlainText(),
                    'drug_addiction_smoking': self.addiction_check.isChecked(),
                    'assistive_device_used': self.device_input.text(),
                    'student_id': student_id
                }

                if 'medical_history' in self.student_data and self.student_data['medical_history']:
                    medical_id = self.student_data['medical_history'][0].get('medical_id')
                    if medical_id:
                        # Update existing record
                        success, result = self.medical_service.update(medical_id, medical_data)
                    else:
                        # Create new record if ID is missing
                        success, result = self.medical_service.create_medical_record(medical_data)
                else:
                    # Create new record if no medical history
                    success, result = self.medical_service.create_medical_record(medical_data)

                if not success:
                    QMessageBox.warning(self, "Warning", f"Medical information update failed: {result}")

            # For guardian information (section #5 in save_all_changes method)
            if hasattr(self, 'guardian_name_input'):
                guardian_name = self.guardian_name_input.text().strip()
                if guardian_name:  # Only save if name is provided
                    guardian_data = {
                        'guardian_name': guardian_name,
                        'guardian_relationship': self.guardian_relationship_input.text(),
                        'guardian_contact_number': self.guardian_contact_input.text(),
                        'student_id': student_id
                    }

                    self.logger.info(f"Processing guardian data for student {student_id}: {guardian_data}")

                    try:
                        # Get existing guardians for this student
                        existing_guardians = self.guardian_service.get_by_student(student_id)

                        # If we have an existing guardian, update it
                        if existing_guardians and isinstance(existing_guardians, list) and len(existing_guardians) > 0:
                            guardian = existing_guardians[0]  # Take the first guardian
                            guardian_id = guardian.student_guardian_id  # Use the correct field name
                            self.logger.info(f"Updating guardian ID {guardian_id}")
                            success, result = self.guardian_service.update(guardian_id, guardian_data)
                            if not success:
                                QMessageBox.warning(self, "Warning", f"Guardian information update failed: {result}")
                        # If it's a single object (not a list)
                        elif existing_guardians and not isinstance(existing_guardians, list):
                            guardian_id = existing_guardians.student_guardian_id  # Use the correct field name
                            self.logger.info(f"Updating guardian ID {guardian_id}")
                            success, result = self.guardian_service.update(guardian_id, guardian_data)
                            if not success:
                                QMessageBox.warning(self, "Warning", f"Guardian information update failed: {result}")
                        else:
                            # Create new guardian record if none exists
                            self.logger.info(f"Creating new guardian for student {student_id}")
                            success, result = self.guardian_service.create_guardian(guardian_data)
                            if not success:
                                QMessageBox.warning(self, "Warning", f"Guardian information creation failed: {result}")
                    except Exception as e:
                        self.logger.error(f"Error handling guardian data: {str(e)}")
                        QMessageBox.warning(self, "Warning", f"Guardian processing error: {str(e)}")

            # 6. Save hostel information if form was initialized
            if hasattr(self, 'duration_input'):
                hostel_data = {
                    'duration_of_stay': self.duration_input.text(),
                    'special_requirements': self.requirements_input.toPlainText(),
                    'student_id': student_id
                }

                if 'hostel_info' in self.student_data and self.student_data['hostel_info']:
                    hostel_id = self.student_data['hostel_info'][0].get('hostel_id')
                    if hostel_id:
                        # Update existing record
                        success, result = self.hostel_service.update(hostel_id, hostel_data)
                    else:
                        # Create new record if ID is missing
                        success, result = self.hostel_service.create_hostel_record(hostel_data)
                else:
                    # Create new record if no hostel info
                    success, result = self.hostel_service.create_hostel_record(hostel_data)

                if not success:
                    QMessageBox.warning(self, "Warning", f"Hostel information update failed: {result}")

            # For transportation information (section #7 in save_all_changes method)
            if hasattr(self, 'responsible_name_input'):
                transport_data = {
                    'pickup_drop_responsible_name': self.responsible_name_input.text(),
                    'pickup_drop_contact_number': self.transport_contact_input.text(),
                    'student_id': student_id
                }

                self.logger.info(f"Processing transportation data for student {student_id}: {transport_data}")

                try:
                    existing_transport = self.transportation_service.get_by_student(student_id)

                    # If we have existing transportation data, update it
                    if existing_transport and isinstance(existing_transport, list) and len(existing_transport) > 0:
                        transport = existing_transport[0]  # Take the first record
                        transport_id = transport.transport_id  # Use the correct field name
                        self.logger.info(f"Updating transportation ID {transport_id}")
                        success, result = self.transportation_service.update(transport_id, transport_data)
                        if not success:
                            QMessageBox.warning(self, "Warning", f"Transportation information update failed: {result}")
                    # If it's a single object (not a list)
                    elif existing_transport and not isinstance(existing_transport, list):
                        transport_id = existing_transport.transport_id  # Use the correct field name
                        self.logger.info(f"Updating transportation ID {transport_id}")
                        success, result = self.transportation_service.update(transport_id, transport_data)
                        if not success:
                            QMessageBox.warning(self, "Warning", f"Transportation information update failed: {result}")
                    else:
                        # Create new transportation record if none exists
                        self.logger.info(f"Creating new transportation for student {student_id}")
                        success, result = self.transportation_service.create_transport_record(transport_data)
                        if not success:
                            QMessageBox.warning(self, "Warning",
                                                f"Transportation information creation failed: {result}")
                except Exception as e:
                    self.logger.error(f"Error handling transportation data: {str(e)}")
                    QMessageBox.warning(self, "Warning", f"Transportation processing error: {str(e)}")

            # Show success message and close dialog
            QMessageBox.information(self, "Success", "All student information updated successfully!")
            self.accept()

        except Exception as e:
            self.logger.error(f"Error saving student data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")