from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QLabel, QMessageBox, QFormLayout, QLineEdit,
                             QDateEdit, QComboBox, QCheckBox, QGroupBox, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox,
                             QTextEdit, QApplication, QStyle)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator
from app.services.student_service import StudentService
from app.services.medical_service import MedicalService
from app.services.education_service import EducationService
from app.services.guardian_service import GuardianService
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService
from app.services.hostel_service import HostelService
from app.services.transportation_service import TransportationService
from app.utils.logger import Logger
from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtGui import QTextDocument
from app.config.config import Config
import datetime


class StudentRegistrationDialog(QDialog):
    """Dialog for registering a new student with all related information"""

    student_added = pyqtSignal(int)  # Signal emitted when student is added successfully

    def __init__(self, parent=None, current_user=None):
        """
        Initialize the student registration dialog

        Args:
            parent: Parent widget
            current_user: Username of the current user
        """
        super().__init__(parent)
        self.setWindowTitle("Student Registration")
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)

        # Initialize services
        self.student_service = StudentService()
        self.medical_service = MedicalService()
        self.education_service = EducationService()
        self.guardian_service = GuardianService()
        self.course_service = CourseService()
        self.enrollment_service = EnrollmentService()
        self.hostel_service = HostelService()
        self.transportation_service = TransportationService()
        self.logger = Logger()

        # Get current date/time and user
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Use passed in user name
        self.current_user = current_user if current_user else "Unknown User"

        # State tracking
        self.current_student_id = None
        self.form_data = {
            'personal': {},
            'guardians': [],
            'medical': {},
            'education': [],
            'enrollments': [],
            'hostel': {},
            'transportation': {},
            'created_by': self.current_user,
            'created_at': current_datetime
        }

        # Flag to track if data has been collected for each tab
        self.data_collected = {
            'personal': False,
            'guardians': False,
            'medical': False,
            'education': False,
            'enrollments': False,
            'hostel': False,
            'transportation': False
        }

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Student Registration Form")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(header_label)

        # Description
        description = QLabel(
            "Please fill out the student information in each tab. "
            "Start with Personal Information and proceed through each tab using the Next button. "
            "Required fields are marked with *"
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description)

        # Current date and time
        date_time_label = QLabel(
            f"Registration Date: {self.form_data['created_at']} | User: {self.form_data['created_by']}")
        date_time_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(date_time_label)

        # Progress status
        self.status_label = QLabel("Status: Please complete Personal Information")
        self.status_label.setStyleSheet("font-weight: bold; color: blue;")
        main_layout.addWidget(self.status_label)

        # Tabs for different information sections
        self.tabs = QTabWidget()

        # Tab 1: Personal Information
        self.personal_tab = QWidget()
        self.init_personal_tab()
        self.tabs.addTab(self.personal_tab, "1. Personal Information")

        # Tab 2: Guardian & Transportation
        self.guardian_transport_tab = QWidget()
        self.init_guardian_transport_tab()
        self.tabs.addTab(self.guardian_transport_tab, "2. Guardian, Transport")

        # Tab 3: Medical History
        self.medical_tab = QWidget()
        self.init_medical_tab()
        self.tabs.addTab(self.medical_tab, "3. Medical History")

        # Tab 4: Education, Course & Hostel
        self.education_course_hostel_tab = QWidget()
        self.init_education_course_hostel_tab()
        self.tabs.addTab(self.education_course_hostel_tab, "4. Education, Course & Hostel")

        # Tab 5: Summary
        self.summary_tab = QWidget()
        self.init_summary_tab()
        self.tabs.addTab(self.summary_tab, "5. Summary")

        # Connect tab change signal
        self.tabs.currentChanged.connect(self.tab_changed)

        # Disable all tabs except the first one initially
        for i in range(1, self.tabs.count()):
            self.tabs.setTabEnabled(i, False)

        main_layout.addWidget(self.tabs)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.previous_tab)
        self.prev_btn.setEnabled(False)

        # Next/Finish button - will change text based on tab
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_tab)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        nav_layout.addWidget(self.cancel_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)

        main_layout.addLayout(nav_layout)

    def init_personal_tab(self):
        """Initialize the personal information tab"""
        layout = QVBoxLayout(self.personal_tab)

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
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        personal_layout.addRow("Address:", self.address_input)

        # Contact number
        self.contact_input = QLineEdit()
        personal_layout.addRow("Contact Number:", self.contact_input)

        # Occupation
        self.occupation_input = QLineEdit()
        personal_layout.addRow("Occupation:", self.occupation_input)

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

        form_layout.addRow(admission_group)

        # Add note about required fields
        form_layout.addRow("* Required fields", QLabel())

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

    def init_guardian_transport_tab(self):
        """Initialize the combined guardian and transportation tab"""
        layout = QVBoxLayout(self.guardian_transport_tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Guardian Information Group
        guardian_group = QGroupBox("Guardian Information")
        guardian_layout = QFormLayout(guardian_group)

        # Guardian name
        self.guardian_name_input = QLineEdit()
        guardian_layout.addRow("Guardian Name:", self.guardian_name_input)

        # Relationship
        self.guardian_relationship_input = QLineEdit()
        guardian_layout.addRow("Relationship:", self.guardian_relationship_input)

        # Contact number
        self.guardian_contact_input = QLineEdit()
        guardian_layout.addRow("Contact Number:", self.guardian_contact_input)

        scroll_layout.addWidget(guardian_group)

        # Transportation Information Group
        transport_group = QGroupBox("Transportation Information")
        transport_layout = QFormLayout(transport_group)

        # Responsible person name
        self.responsible_name_input = QLineEdit()
        transport_layout.addRow("Responsible Person Name:", self.responsible_name_input)

        # Contact number
        self.transport_contact_input = QLineEdit()
        transport_layout.addRow("Contact Number:", self.transport_contact_input)

        scroll_layout.addWidget(transport_group)

        # Add blank space at bottom
        scroll_layout.addStretch()

        # Add to scroll area
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

    def init_medical_tab(self):
        """Initialize the medical history tab"""
        layout = QVBoxLayout(self.medical_tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)

        # Medical Information Group
        medical_group = QGroupBox("Medical History")
        medical_layout = QFormLayout(medical_group)

        # Name of disability
        self.disability_input = QLineEdit()
        medical_layout.addRow("Name of Disability:", self.disability_input)

        # Brief medical history
        self.medical_history_input = QTextEdit()
        medical_layout.addRow("Brief Medical History:", self.medical_history_input)

        # Regular medication
        self.medication_input = QTextEdit()
        medical_layout.addRow("Regular Medication:", self.medication_input)

        # Epilepsy
        self.epilepsy_check = QCheckBox()
        medical_layout.addRow("Epilepsy:", self.epilepsy_check)

        # Communicable disease
        self.disease_input = QTextEdit()
        medical_layout.addRow("Communicable Disease:", self.disease_input)

        # Drug addiction/smoking
        self.addiction_check = QCheckBox()
        medical_layout.addRow("Drug Addiction/Smoking:", self.addiction_check)

        # Assistive device
        self.device_input = QLineEdit()
        medical_layout.addRow("Assistive Device Used:", self.device_input)

        form_layout.addRow(medical_group)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

    def init_education_course_hostel_tab(self):
        """Initialize the education, course, and hostel tab"""
        layout = QVBoxLayout(self.education_course_hostel_tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Education Information Group
        edu_group = QGroupBox("Education Information")
        edu_form = QFormLayout(edu_group)

        # Education level
        self.education_level_input = QLineEdit()
        edu_form.addRow("Education Level:", self.education_level_input)

        # Certificate attached
        self.certificate_check = QCheckBox()
        edu_form.addRow("Certificate Attached:", self.certificate_check)

        scroll_layout.addWidget(edu_group)

        # Course Enrollment Group
        course_group = QGroupBox("Course Enrollment")
        course_form = QFormLayout(course_group)

        # Course selection
        self.course_combo = QComboBox()
        # Add empty option
        self.course_combo.addItem("-- Select Course --", "")
        # Add courses from database
        courses = self.course_service.get_all_courses()
        for course in courses:
            self.course_combo.addItem(course.course_name, course.course_id)
        course_form.addRow("Course:", self.course_combo)

        # Date of enrollment
        self.enrollment_date_edit = QDateEdit(calendarPopup=True)
        self.enrollment_date_edit.setDate(QDate.currentDate())
        self.enrollment_date_edit.setDisplayFormat("yyyy-MM-dd")
        course_form.addRow("Date of Enrollment:", self.enrollment_date_edit)

        # Completion status
        self.completion_check = QCheckBox()
        course_form.addRow("Completed:", self.completion_check)

        scroll_layout.addWidget(course_group)

        # Hostel Information Group
        hostel_group = QGroupBox("Hostel Information")
        hostel_layout = QFormLayout(hostel_group)

        # Duration of stay
        self.duration_input = QLineEdit()
        hostel_layout.addRow("Duration of Stay:", self.duration_input)

        # Special requirements
        self.requirements_input = QTextEdit()
        hostel_layout.addRow("Special Requirements:", self.requirements_input)

        scroll_layout.addWidget(hostel_group)

        # Add blank space at bottom
        scroll_layout.addStretch()

        # Add to scroll area
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

    def init_summary_tab(self):
        """Initialize the summary tab"""
        layout = QVBoxLayout(self.summary_tab)

        # Instructions
        instructions = QLabel("Review the student information below and click 'Finish' to complete registration.")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Summary display area
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)

    def collect_personal_info(self):
        """Collect the student's personal information without saving to database"""
        # Collect data from form
        personal_data = {
            'student_name': self.name_input.text(),
            'cnic': self.cnic_input.text(),
            'gender': self.gender_combo.currentText(),
            'age': int(self.age_input.text()) if self.age_input.text() else None,
            'date_of_birth': self.dob_edit.date().toString('yyyy-MM-dd'),
            'phone': self.phone_input.text(),
            'address': self.address_input.toPlainText(),
            'student_contact_no': self.contact_input.text(),
            'student_occupation': self.occupation_input.text(),
            'admission_type': self.admission_type_combo.currentText(),
            'admission_date': self.admission_date_edit.date().toString('yyyy-MM-dd'),
            'accompanied_by_assistant': self.assistant_check.isChecked(),
            'affidavit_attached': self.affidavit_check.isChecked()
        }

        # Validate required fields
        if not personal_data['student_name']:
            QMessageBox.warning(self, "Validation Error", "Student name is required.")
            return False

        # Store the data
        self.form_data['personal'] = personal_data
        self.data_collected['personal'] = True

        # Update UI feedback
        self.status_label.setText("Status: Personal information collected. Continue to Guardian & Transportation.")

        # Enable next tab
        self.tabs.setTabEnabled(1, True)  # Enable Guardian & Transportation tab

        return True

    def collect_guardian_transport_info(self):
        """Collect guardian and transportation information"""
        # Clear previous data
        self.form_data['guardians'] = []

        # Collect guardian data
        guardian_name = self.guardian_name_input.text().strip()
        if guardian_name:
            guardian_data = {
                'guardian_name': guardian_name,
                'guardian_relationship': self.guardian_relationship_input.text().strip(),
                'guardian_contact_number': self.guardian_contact_input.text().strip()
            }
            self.form_data['guardians'].append(guardian_data)
            self.data_collected['guardians'] = True
        else:
            self.data_collected['guardians'] = False

        # Collect transportation data
        transport_data = {
            'pickup_drop_responsible_name': self.responsible_name_input.text(),
            'pickup_drop_contact_number': self.transport_contact_input.text()
        }
        self.form_data['transportation'] = transport_data
        self.data_collected['transportation'] = True

        # Update UI
        self.status_label.setText(
            "Status: Guardian and transportation information collected. Continue to Medical History.")

        # Enable next tab
        self.tabs.setTabEnabled(2, True)  # Enable Medical tab
        return True

    def collect_medical_info(self):
        """Collect the student's medical information without saving to database"""
        # Collect medical data
        medical_data = {
            'name_of_disability': self.disability_input.text(),
            'brief_medical_history': self.medical_history_input.toPlainText(),
            'regular_medication': self.medication_input.toPlainText(),
            'epilepsy': self.epilepsy_check.isChecked(),
            'communicable_disease': self.disease_input.toPlainText(),
            'drug_addiction_smoking': self.addiction_check.isChecked(),
            'assistive_device_used': self.device_input.text()
        }

        # Store data
        self.form_data['medical'] = medical_data
        self.data_collected['medical'] = True

        # Update UI
        self.status_label.setText("Status: Medical information collected. Continue to Education, Course & Hostel.")

        # Enable next tab
        self.tabs.setTabEnabled(3, True)  # Enable Education, Course & Hostel tab
        return True

    def collect_education_course_hostel_info(self):
        """Collect education, course enrollment, and hostel information"""
        # Clear previous data
        self.form_data['education'] = []
        self.form_data['enrollments'] = []

        # Collect education data
        education_level = self.education_level_input.text().strip()
        if education_level:
            education_data = {
                'education_level': education_level,
                'certificate_attached': self.certificate_check.isChecked()
            }
            self.form_data['education'].append(education_data)
            self.data_collected['education'] = True
        else:
            self.data_collected['education'] = False

        # Collect enrollment data
        course_id = self.course_combo.currentData()
        if course_id:
            enrollment_data = {
                'course_id': course_id,
                'course_name': self.course_combo.currentText(),
                'date_of_enrollment': self.enrollment_date_edit.date().toString('yyyy-MM-dd'),
                'completion_status': self.completion_check.isChecked()
            }
            self.form_data['enrollments'].append(enrollment_data)
            self.data_collected['enrollments'] = True
        else:
            self.data_collected['enrollments'] = False

        # Collect hostel data
        hostel_data = {
            'duration_of_stay': self.duration_input.text(),
            'special_requirements': self.requirements_input.toPlainText()
        }
        self.form_data['hostel'] = hostel_data
        self.data_collected['hostel'] = True

        # Update UI
        self.status_label.setText("Status: Education, course, and hostel information collected. Continue to Summary.")

        # Enable summary tab
        self.tabs.setTabEnabled(4, True)  # Enable Summary tab

        return True

    def generate_summary_preview(self):
        """Generate a summary preview from collected data"""
        try:
            summary = []
            summary.append("<h2>Student Registration Summary Preview</h2>")
            summary.append("<p><i>Review the information below before saving all data.</i></p>")
            summary.append(f"<p><i>Registration by: {self.form_data.get('created_by', self.current_user)}</i></p>")
            summary.append(f"<p><i>Date: {self.form_data.get('created_at', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</i></p>")

            # Personal Information
            summary.append("<h3>1. Personal Information</h3>")
            personal = self.form_data['personal']
            summary.append(f"<p><b>Name:</b> {personal.get('student_name', 'N/A')}</p>")
            summary.append(f"<p><b>CNIC:</b> {personal.get('cnic', 'N/A')}</p>")
            summary.append(f"<p><b>Gender:</b> {personal.get('gender', 'N/A')}</p>")
            summary.append(f"<p><b>Age:</b> {personal.get('age', 'N/A')}</p>")
            summary.append(f"<p><b>Date of Birth:</b> {personal.get('date_of_birth', 'N/A')}</p>")
            summary.append(f"<p><b>Phone:</b> {personal.get('phone', 'N/A')}</p>")
            summary.append(f"<p><b>Address:</b> {personal.get('address', 'N/A')}</p>")
            summary.append(f"<p><b>Contact No:</b> {personal.get('student_contact_no', 'N/A')}</p>")
            summary.append(f"<p><b>Occupation:</b> {personal.get('student_occupation', 'N/A')}</p>")
            summary.append(f"<p><b>Admission Type:</b> {personal.get('admission_type', 'N/A')}</p>")
            summary.append(f"<p><b>Admission Date:</b> {personal.get('admission_date', 'N/A')}</p>")
            summary.append(
                f"<p><b>Accompanied by Assistant:</b> {'Yes' if personal.get('accompanied_by_assistant') else 'No'}</p>")
            summary.append(f"<p><b>Affidavit Attached:</b> {'Yes' if personal.get('affidavit_attached') else 'No'}</p>")

            # Guardian
            if self.form_data['guardians']:
                summary.append("<h3>2. Guardian Information</h3>")
                guardian = self.form_data['guardians'][0]
                summary.append(f"<p><b>Name:</b> {guardian.get('guardian_name', '')}</p>")
                summary.append(f"<p><b>Relationship:</b> {guardian.get('guardian_relationship', '')}</p>")
                summary.append(f"<p><b>Contact:</b> {guardian.get('guardian_contact_number', '')}</p>")

            # Transportation
            if self.data_collected['transportation']:
                summary.append("<h3>3. Transportation</h3>")
                transport = self.form_data['transportation']
                summary.append(f"<p><b>Responsible Person:</b> {transport.get('pickup_drop_responsible_name', '')}</p>")
                summary.append(f"<p><b>Contact:</b> {transport.get('pickup_drop_contact_number', '')}</p>")

            # Medical History
            if self.data_collected['medical']:
                summary.append("<h3>4. Medical History</h3>")
                med = self.form_data['medical']
                summary.append(f"<p><b>Disability:</b> {med.get('name_of_disability', '')}</p>")
                summary.append(f"<p><b>Medical History:</b> {med.get('brief_medical_history', '')}</p>")
                summary.append(f"<p><b>Regular Medication:</b> {med.get('regular_medication', '')}</p>")
                summary.append(f"<p><b>Epilepsy:</b> {'Yes' if med.get('epilepsy') else 'No'}</p>")
                summary.append(f"<p><b>Communicable Disease:</b> {med.get('communicable_disease', '')}</p>")
                summary.append(f"<p><b>Drug/Smoking:</b> {'Yes' if med.get('drug_addiction_smoking') else 'No'}</p>")
                summary.append(f"<p><b>Assistive Device:</b> {med.get('assistive_device_used', '')}</p>")

            # Education
            if self.form_data['education']:
                summary.append("<h3>5. Education History</h3>")
                education = self.form_data['education'][0]
                summary.append(f"<p><b>Level:</b> {education.get('education_level', '')}</p>")
                summary.append(f"<p><b>Certificate:</b> {'Yes' if education.get('certificate_attached') else 'No'}</p>")

            # Course Enrollment
            if self.form_data['enrollments']:
                summary.append("<h3>6. Course Enrollment</h3>")
                enrollment = self.form_data['enrollments'][0]
                summary.append(
                    f"<p><b>Course:</b> {enrollment.get('course_name', '')} (ID: {enrollment.get('course_id', '')})</p>")
                summary.append(f"<p><b>Date:</b> {enrollment.get('date_of_enrollment', '')}</p>")
                summary.append(f"<p><b>Completed:</b> {'Yes' if enrollment.get('completion_status') else 'No'}</p>")

            # Hostel
            if self.data_collected['hostel']:
                summary.append("<h3>7. Hostel Information</h3>")
                hostel = self.form_data['hostel']
                summary.append(f"<p><b>Duration of Stay:</b> {hostel.get('duration_of_stay', '')}</p>")
                summary.append(f"<p><b>Special Requirements:</b> {hostel.get('special_requirements', '')}</p>")

            # Add instruction for saving
            summary.append("<h3>Ready to Save</h3>")
            summary.append("<p>Click 'Finish' button to save all information to the database.</p>")

            # Set the summary text
            self.summary_text.setHtml("\n".join(summary))

            if not hasattr(self, 'print_button'):
                # Create a print button
                self.print_button = QPushButton("Print Summary")
                self.print_button.setIcon(
                    self.style().standardIcon(getattr(QStyle, 'SP_PrinterIcon', QStyle.SP_ComputerIcon)))
                self.print_button.clicked.connect(self.print_summary)

                # Create a horizontal layout for the button
                button_layout = QHBoxLayout()
                button_layout.addStretch()
                button_layout.addWidget(self.print_button)

                # Add the button layout to wherever your summary_text is placed
                layout = self.summary_text.parent().layout()
                if layout:
                    layout.addLayout(button_layout)
                else:
                    # If there's no layout, you need to find the appropriate parent widget
                    # and set up a layout for it or add to an existing container
                    container = self.findChild(QWidget, "summary_container")
                    if container:
                        if not container.layout():
                            container_layout = QVBoxLayout(container)
                            container_layout.addWidget(self.summary_text)
                        container.layout().addLayout(button_layout)
                    else:
                        # As a last resort, we can add it directly to the dialog
                        # This is not ideal as it might disrupt your layout
                        if not hasattr(self, 'summary_layout'):
                            self.summary_layout = QVBoxLayout()
                            self.layout().addLayout(self.summary_layout)
                        self.summary_layout.addLayout(button_layout)

        except Exception as e:
            self.logger.error(f"Error generating summary preview: {str(e)}")
            self.summary_text.setText(f"Error generating summary preview: {str(e)}")

    def print_summary(self):
        """Handle printing the summary"""
        try:
            # Create a printer
            printer = QPrinter(QPrinter.HighResolution)

            # Show print preview dialog
            preview_dialog = QPrintPreviewDialog(printer, self)
            preview_dialog.paintRequested.connect(self.print_document)
            preview_dialog.exec_()
        except Exception as e:
            self.logger.error(f"Error showing print dialog: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to open print dialog: {str(e)}")

    def print_document(self, printer):
        """Print the document to the specified printer"""
        try:
            # Create a document to print
            document = QTextDocument()

            # Get the HTML content from the summary text widget
            html_content = self.summary_text.toHtml()

            # Set additional styles for printing
            styled_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    h2 {{ color: #333; text-align: center; }}
                    h3 {{ color: #444; margin-top: 15px; }}
                    p {{ margin: 5px 0; }}
                    .footer {{ text-align: center; font-size: 9pt; color: #777; margin-top: 20px; }}
                </style>
            </head>
            <body>
                {html_content}
                <div class="footer">
                    <p>Printed from Student Management System on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </body>
            </html>
            """

            # Set the HTML content with styles
            document.setHtml(styled_html)

            # Print the document
            document.print_(printer)
        except Exception as e:
            self.logger.error(f"Error printing document: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to print document: {str(e)}")

    def generate_final_summary(self, student_data):
        """Generate a final summary with the actual saved data"""
        try:
            summary = []
            summary.append("<h2>Student Registration Complete</h2>")
            summary.append(f"<p><b>Student ID:</b> {student_data['student_id']}</p>")
            summary.append(f"<p><i>Registration by: {self.current_user}</i></p>")
            summary.append(f"<p><i>Date: {self.form_data['created_at']}</i></p>")

            # Personal Information
            summary.append("<h3>Personal Information</h3>")
            summary.append(f"<p><b>Name:</b> {student_data.get('student_name', 'N/A')}</p>")
            summary.append(f"<p><b>CNIC:</b> {student_data.get('cnic', 'N/A')}</p>")
            summary.append(f"<p><b>Gender:</b> {student_data.get('gender', 'N/A')}</p>")
            summary.append(f"<p><b>Age:</b> {student_data.get('age', 'N/A')}</p>")
            summary.append(f"<p><b>Date of Birth:</b> {student_data.get('date_of_birth', 'N/A')}</p>")
            summary.append(f"<p><b>Phone:</b> {student_data.get('phone', 'N/A')}</p>")
            summary.append(f"<p><b>Address:</b> {student_data.get('address', 'N/A')}</p>")
            summary.append(f"<p><b>Admission Type:</b> {student_data.get('admission_type', 'N/A')}</p>")
            summary.append(f"<p><b>Admission Date:</b> {student_data.get('admission_date', 'N/A')}</p>")

            # Guardians
            if 'guardians' in student_data and student_data['guardians']:
                summary.append("<h3>Guardian Information</h3>")
                guardian = student_data['guardians'][0] if student_data['guardians'] else {}
                summary.append(f"<p><b>Name:</b> {guardian.get('guardian_name', '')}</p>")
                summary.append(f"<p><b>Relationship:</b> {guardian.get('guardian_relationship', '')}</p>")
                summary.append(f"<p><b>Contact:</b> {guardian.get('guardian_contact_number', '')}</p>")

            # Transportation
            if 'transportation' in student_data and student_data['transportation']:
                summary.append("<h3>Transportation</h3>")
                transport = student_data['transportation'][0] if student_data['transportation'] else {}
                summary.append(f"<p><b>Responsible Person:</b> {transport.get('pickup_drop_responsible_name', '')}</p>")
                summary.append(f"<p><b>Contact:</b> {transport.get('pickup_drop_contact_number', '')}</p>")

            # Medical History
            if 'medical_history' in student_data and student_data['medical_history']:
                summary.append("<h3>Medical History</h3>")
                med = student_data['medical_history'][0] if student_data['medical_history'] else {}
                summary.append(f"<p><b>Disability:</b> {med.get('name_of_disability', '')}</p>")
                summary.append(f"<p><b>Epilepsy:</b> {'Yes' if med.get('epilepsy') else 'No'}</p>")
                summary.append(f"<p><b>Drug/Smoking:</b> {'Yes' if med.get('drug_addiction_smoking') else 'No'}</p>")
                summary.append(f"<p><b>Assistive Device:</b> {med.get('assistive_device_used', '')}</p>")

            # Education
            if 'education_history' in student_data and student_data['education_history']:
                summary.append("<h3>Education History</h3>")
                education = student_data['education_history'][0] if student_data['education_history'] else {}
                summary.append(f"<p><b>Level:</b> {education.get('education_level', '')}</p>")
                summary.append(f"<p><b>Certificate:</b> {'Yes' if education.get('certificate_attached') else 'No'}</p>")

            # Enrollments
            if 'enrollments' in student_data and student_data['enrollments']:
                summary.append("<h3>Course Enrollment</h3>")
                enrollment = student_data['enrollments'][0] if student_data['enrollments'] else {}
                course_name = enrollment.get('course_name', f"Course ID: {enrollment.get('course_id', '')}")
                summary.append(f"<p><b>Course:</b> {course_name}</p>")
                summary.append(f"<p><b>Date:</b> {enrollment.get('date_of_enrollment', '')}</p>")
                summary.append(f"<p><b>Completed:</b> {'Yes' if enrollment.get('completion_status') else 'No'}</p>")

            # Hostel
            if 'hostel_info' in student_data and student_data['hostel_info']:
                summary.append("<h3>Hostel Information</h3>")
                hostel = student_data['hostel_info'][0] if student_data['hostel_info'] else {}
                summary.append(f"<p><b>Duration of Stay:</b> {hostel.get('duration_of_stay', '')}</p>")
                summary.append(f"<p><b>Special Requirements:</b> {hostel.get('special_requirements', '')}</p>")

            # Set the summary text
            self.summary_text.setHtml("\n".join(summary))

        except Exception as e:
            self.logger.error(f"Error generating final summary: {str(e)}")
            self.summary_text.setText(f"Error generating final summary: {str(e)}")

    def complete_registration(self):
        """Save all collected data to the database and complete registration"""
        try:
            # Validate that we have required data
            if not self.data_collected['personal']:
                QMessageBox.warning(self, "Validation Error", "Personal information is required.")
                return

            # Show processing indicator
            self.status_label.setText("Status: Saving data to database... Please wait.")
            QApplication.processEvents()  # Allow UI to update

            # Step 1: Create the student record
            success, result = self.student_service.create_student(self.form_data['personal'])
            if not success:
                QMessageBox.critical(self, "Error", f"Failed to create student record: {result}")
                return

            # Get the new student ID
            student_id = result.student_id
            self.current_student_id = student_id

            # Step 2: Add guardian if data exists
            if self.form_data['guardians']:
                guardian_data = self.form_data['guardians'][0]
                guardian_data['student_id'] = student_id
                self.guardian_service.create_guardian(guardian_data)

            # Step 3: Add medical record if data exists
            if self.data_collected['medical']:
                medical_data = self.form_data['medical']
                medical_data['student_id'] = student_id
                self.medical_service.create_medical_record(medical_data)

            # Step 4: Add education record if data exists
            if self.form_data['education']:
                education_data = self.form_data['education'][0]
                education_data['student_id'] = student_id
                self.education_service.create_education_record(education_data)

            # Step 5: Add enrollment if data exists
            if self.form_data['enrollments']:
                enrollment_data = self.form_data['enrollments'][0]
                enrollment_data['student_id'] = student_id
                # Remove course_name if present as it's not a database field
                if 'course_name' in enrollment_data:
                    del enrollment_data['course_name']
                self.enrollment_service.create_enrollment(enrollment_data)

            # Step 6: Add hostel information if data exists
            if self.data_collected['hostel']:
                hostel_data = self.form_data['hostel']
                hostel_data['student_id'] = student_id
                self.hostel_service.create_hostel_record(hostel_data)

            # Step 7: Add transportation information if data exists
            if self.data_collected['transportation']:
                transport_data = self.form_data['transportation']
                transport_data['student_id'] = student_id
                self.transportation_service.create_transport_record(transport_data)

            # Final step: Fetch complete record for the final summary
            student_data = self.student_service.get_student_with_details(student_id)
            if student_data:
                self.generate_final_summary(student_data)

            # Show success message
            QMessageBox.information(
                self,
                "Registration Complete",
                f"Student registration is now complete for student ID: {student_id}."
            )

            # Emit signal with student ID
            self.student_added.emit(student_id)

            # Close dialog
            self.accept()

        except Exception as e:
            self.logger.error(f"Error completing registration: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

    def tab_changed(self, index):
        """Handle tab change events"""
        tab_titles = [
            "Personal Information",
            "Guardian & Transportation",
            "Medical History",
            "Education, Course & Hostel",
            "Summary"
        ]

        if index < len(tab_titles):
            self.status_label.setText(f"Status: Entering {tab_titles[index]} details...")

        # Update button states
        self.prev_btn.setEnabled(index > 0)

        # Check if we're on the last tab
        if index == self.tabs.count() - 1:
            self.next_btn.setText("Finish")  # Change button text to "Finish" on summary tab
        else:
            self.next_btn.setText("Next")  # Change back to "Next" for other tabs
            self.next_btn.setEnabled(True)

    def next_tab(self):
        """Go to the next tab or finish registration if on the last tab"""
        current_index = self.tabs.currentIndex()

        # If we're on the summary tab, complete registration instead of navigating
        if current_index == self.tabs.count() - 1:  # Summary tab
            self.complete_registration()
            return

        if current_index < self.tabs.count() - 1:
            next_index = current_index + 1

            # Check if we need to validate before moving to specific tabs
            if current_index == 0 and not self.data_collected['personal']:
                # Need to collect personal info before proceeding
                if not self.collect_personal_info():
                    return
            elif current_index == 1:
                # Need to collect guardian and transportation info
                if not self.collect_guardian_transport_info():
                    return
            elif current_index == 2 and not self.data_collected['medical']:
                # Need to collect medical info
                if not self.collect_medical_info():
                    return
            elif current_index == 3:
                # Need to collect education, course, and hostel info
                if not self.collect_education_course_hostel_info():
                    return

            if self.tabs.isTabEnabled(next_index):
                self.tabs.setCurrentIndex(next_index)

                # Update status message based on the tab
                tab_names = ["Personal Information", "Guardian & Transportation", "Medical History",
                             "Education, Course & Hostel", "Summary"]

                if next_index < len(tab_names):
                    self.status_label.setText(f"Status: Entering {tab_names[next_index]} details...")

                # If we're now on the summary tab, generate the preview
                if next_index == 4:  # Summary tab
                    self.generate_summary_preview()

    def previous_tab(self):
        """Go to the previous tab"""
        current_index = self.tabs.currentIndex()
        if current_index > 0:
            self.tabs.setCurrentIndex(current_index - 1)

#
# if __name__ == '__main__':
#     # Test code
#     import sys
#
#     app = QApplication(sys.argv)
#     dialog = StudentRegistrationDialog()
#     dialog.show()
#     sys.exit(app.exec_())