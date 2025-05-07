from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QPushButton, QTabWidget, QWidget, QFrame)
from PyQt5.QtCore import Qt

class StudentDetailsDialog(QDialog):
    """Dialog to display detailed student information"""

    def __init__(self, student_data, parent=None):
        super().__init__(parent)
        self.student_data = student_data
        self.setWindowTitle(f"Student Details: {student_data.get('student_name', 'Unknown')}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)

        # Create tabs for different sections of student data
        tab_widget = QTabWidget()

        # Personal information tab
        personal_tab = QWidget()
        personal_layout = QFormLayout(personal_tab)
        self.populate_personal_info(personal_layout)
        tab_widget.addTab(personal_tab, "Personal Information")

        # Education history tab (if available)
        if 'education_history' in self.student_data and self.student_data['education_history']:
            education_tab = QWidget()
            education_layout = QFormLayout(education_tab)
            self.populate_education_info(education_layout)
            tab_widget.addTab(education_tab, "Education")

        # Enrollments tab (if available)
        if 'enrollments' in self.student_data and self.student_data['enrollments']:
            enrollments_tab = QWidget()
            enrollments_layout = QFormLayout(enrollments_tab)
            self.populate_enrollments_info(enrollments_layout)
            tab_widget.addTab(enrollments_tab, "Enrollments")

        # Medical history tab (if available)
        if 'medical_history' in self.student_data and self.student_data['medical_history']:
            medical_tab = QWidget()
            medical_layout = QFormLayout(medical_tab)
            self.populate_medical_info(medical_layout)
            tab_widget.addTab(medical_tab, "Medical History")

        # Guardians tab (if available)
        if 'guardians' in self.student_data and self.student_data['guardians']:
            guardians_tab = QWidget()
            guardians_layout = QFormLayout(guardians_tab)
            self.populate_guardians_info(guardians_layout)
            tab_widget.addTab(guardians_tab, "Guardians")

        # Hostel tab (if available)
        if 'hostel_info' in self.student_data and self.student_data['hostel_info']:
            hostel_tab = QWidget()
            hostel_layout = QFormLayout(hostel_tab)
            self.populate_hostel_info(hostel_layout)
            tab_widget.addTab(hostel_tab, "Hostel")

        # Transportation tab (if available)
        if 'transportation' in self.student_data and self.student_data['transportation']:
            transport_tab = QWidget()
            transport_layout = QFormLayout(transport_tab)
            self.populate_transport_info(transport_layout)
            tab_widget.addTab(transport_tab, "Transportation")

        main_layout.addWidget(tab_widget)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

    def populate_personal_info(self, layout):
        """Populate personal information tab"""
        # Student ID
        layout.addRow("Student ID:", QLabel(str(self.student_data['student_id'])))

        # Student name
        layout.addRow("Name:", QLabel(self.student_data['student_name'] or ""))

        # CNIC
        layout.addRow("CNIC:", QLabel(self.student_data['cnic'] or ""))

        # Gender
        layout.addRow("Gender:", QLabel(self.student_data['gender'] or ""))

        # Age
        layout.addRow("Age:", QLabel(str(self.student_data['age']) if self.student_data['age'] else ""))

        # Date of birth
        dob = self.student_data['date_of_birth'] or ""
        layout.addRow("Date of Birth:", QLabel(dob))

        # Phone
        layout.addRow("Phone:", QLabel(self.student_data['phone'] or ""))

        # Address
        layout.addRow("Address:", QLabel(self.student_data['address'] or ""))

        # Contact number
        layout.addRow("Contact Number:", QLabel(self.student_data['student_contact_no'] or ""))

        # Occupation
        layout.addRow("Occupation:", QLabel(self.student_data['student_occupation'] or ""))

        # Admission type
        layout.addRow("Admission Type:", QLabel(self.student_data['admission_type'] or ""))

        # Admission date
        admission_date = self.student_data['admission_date'] or ""
        layout.addRow("Admission Date:", QLabel(admission_date))

        # Accompanied by assistant
        accompanied = "Yes" if self.student_data['accompanied_by_assistant'] else "No"
        layout.addRow("Accompanied by Assistant:", QLabel(accompanied))

        # Affidavit attached
        affidavit = "Yes" if self.student_data['affidavit_attached'] else "No"
        layout.addRow("Affidavit Attached:", QLabel(affidavit))

    def populate_education_info(self, layout):
        """Populate education history tab"""
        if not self.student_data['education_history']:
            layout.addWidget(QLabel("No education history records found."))
            return

        for education in self.student_data['education_history']:
            # Add details
            layout.addRow("Education Level:", QLabel(education['education_level'] or ""))

            certificate = "Yes" if education['certificate_attached'] else "No"
            layout.addRow("Certificate Attached:", QLabel(certificate))

            # Add separator
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addRow(line)

    def populate_enrollments_info(self, layout):
        """Populate enrollments tab"""
        if not self.student_data['enrollments']:
            layout.addWidget(QLabel("No enrollment records found."))
            return

        for enrollment in self.student_data['enrollments']:
            # Use course_name if available, otherwise use course_id
            course_display = enrollment.get('course_name', 'Unknown Course')
            if 'course_id' in enrollment:
                course_display = f"{course_display} (ID: {enrollment['course_id']})"
            layout.addRow("Course:", QLabel(course_display))

            # Date of enrollment
            date_str = enrollment['date_of_enrollment'] or ""
            layout.addRow("Date of Enrollment:", QLabel(str(date_str)))

            # Completion status
            completion = "Completed" if enrollment['completion_status'] else "Incomplete"
            layout.addRow("Completion Status:", QLabel(completion))

            # Add separator
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addRow(line)

    def populate_medical_info(self, layout):
        """Populate medical history tab"""
        if not self.student_data['medical_history']:
            layout.addWidget(QLabel("No medical history records found."))
            return

        for med_record in self.student_data['medical_history']:
            # Name of disability
            layout.addRow("Disability:", QLabel(med_record['name_of_disability'] or ""))

            # Brief medical history
            history_label = QLabel(med_record['brief_medical_history'] or "")
            history_label.setWordWrap(True)
            layout.addRow("Medical History:", history_label)

            # Regular medication
            medication_label = QLabel(med_record['regular_medication'] or "")
            medication_label.setWordWrap(True)
            layout.addRow("Regular Medication:", medication_label)

            # Epilepsy
            epilepsy = "Yes" if med_record['epilepsy'] else "No"
            layout.addRow("Epilepsy:", QLabel(epilepsy))

            # Communicable disease
            disease_label = QLabel(med_record['communicable_disease'] or "")
            disease_label.setWordWrap(True)
            layout.addRow("Communicable Disease:", disease_label)

            # Drug addiction/smoking
            addiction = "Yes" if med_record['drug_addiction_smoking'] else "No"
            layout.addRow("Drug Addiction/Smoking:", QLabel(addiction))

            # Assistive device
            layout.addRow("Assistive Device Used:", QLabel(med_record['assistive_device_used'] or ""))

            # Add separator
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addRow(line)

    def populate_guardians_info(self, layout):
        """Populate guardians tab"""
        if not self.student_data['guardians']:
            layout.addWidget(QLabel("No guardian records found."))
            return

        for guardian in self.student_data['guardians']:
            # Add details
            layout.addRow("Name:", QLabel(guardian['guardian_name'] or ""))
            layout.addRow("Relationship:", QLabel(guardian['guardian_relationship'] or ""))
            layout.addRow("Contact Number:", QLabel(guardian['guardian_contact_number'] or ""))

            # Add separator
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addRow(line)

    def populate_hostel_info(self, layout):
        """Populate hostel information tab"""
        if not self.student_data['hostel_info']:
            layout.addWidget(QLabel("No hostel information found."))
            return

        for hostel in self.student_data['hostel_info']:
            # Duration of stay
            layout.addRow("Duration of Stay:", QLabel(hostel['duration_of_stay'] or ""))

            # Special requirements
            requirements_label = QLabel(hostel['special_requirements'] or "")
            requirements_label.setWordWrap(True)
            layout.addRow("Special Requirements:", requirements_label)

            # Add separator
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addRow(line)

    def populate_transport_info(self, layout):
        """Populate transportation tab"""
        if not self.student_data['transportation']:
            layout.addWidget(QLabel("No transportation information found."))
            return

        for transport in self.student_data['transportation']:
            # Pickup/drop responsible name
            layout.addRow("Responsible Person:", QLabel(transport['pickup_drop_responsible_name'] or ""))

            # Contact number
            layout.addRow("Contact Number:", QLabel(transport['pickup_drop_contact_number'] or ""))

            # Add separator
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addRow(line)