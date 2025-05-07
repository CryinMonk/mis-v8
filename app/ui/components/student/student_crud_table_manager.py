from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout, QPushButton, QMessageBox, QApplication
from PyQt5.QtCore import Qt

class StudentTableManager:
    """Handles loading and populating table data"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        
    def load_students(self):
        """Load all students into the table"""
        try:
            # Clear the search input
            self.parent.search_input.clear()

            # Reset search input style if it was highlighted
            self.parent.search_input.setStyleSheet("")

            # Log the action
            self.parent.utils._log_activity("Loading all students")

            students = self.parent.student_service.read_all()
            self.populate_table(students)
            self.parent.status_label.setText(f"Loaded {len(students)} students")
        except Exception as e:
            self.parent.logger.error(f"Error loading students: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"Failed to load students: {str(e)}")

    def load_related_table_data(self):
        """Load data for the selected related table"""
        try:
            # Clear the search input if not already cleared
            if self.parent.search_input.text():
                self.parent.search_input.clear()
                self.parent.search_input.setStyleSheet("")

            # Log the action
            self.parent.utils._log_activity(f"Loading all data for {self.parent.selected_table}")

            # Get the appropriate service based on table selection
            service = self.get_service_for_table(self.parent.selected_table)

            if service:
                records = service.read_all()
                self.populate_related_table(records)
                self.parent.status_label.setText(f"Loaded {len(records)} {self.parent.selected_table} records")
            else:
                # Show message if service not available yet
                self.parent.students_table.setRowCount(0)
                QMessageBox.information(self.parent, "Information",
                                        f"Service for {self.parent.selected_table} is not implemented yet.")
                self.parent.status_label.setText(f"No data available for {self.parent.selected_table}")
        except Exception as e:
            self.parent.logger.error(f"Error loading {self.parent.selected_table}: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"Failed to load {self.parent.selected_table}: {str(e)}")

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
            self.parent.logger.error(f"Service for {table_name} not found: {str(e)}")
            return None

    def highlight_student(self, student_id):
        """Highlight a specific student in the table by ID"""
        for row in range(self.parent.students_table.rowCount()):
            id_item = self.parent.students_table.item(row, 0)
            if id_item and int(id_item.text()) == student_id:
                # Select the row
                self.parent.students_table.selectRow(row)
                # Scroll to the row
                self.parent.students_table.scrollToItem(id_item)
                break

    def populate_table(self, students, match_reasons=None, search_term=""):
        """
        Populate the table with student data

        Args:
            students: List of students to display
            match_reasons: Dict of student_id: list of reasons for match
            search_term: Current search term for highlighting
        """
        self.parent.students_table.setRowCount(0)

        for row, student in enumerate(students):
            self.parent.students_table.insertRow(row)

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

            self.parent.students_table.setItem(row, 0, student_id_item)

            # Highlight matching text if search is active
            student_name = student.student_name or ""
            name_item = QTableWidgetItem(student_name)

            if search_term and student_name.lower().find(search_term.lower()) != -1:
                name_item.setBackground(Qt.yellow)
                if 'Name' in reasons:
                    name_item.setToolTip(f"Match found in name: {student_name}")

            self.parent.students_table.setItem(row, 1, name_item)

            self.parent.students_table.setItem(row, 2, QTableWidgetItem(student.gender or ""))

            age_text = str(student.age) if student.age else ""
            self.parent.students_table.setItem(row, 3, QTableWidgetItem(age_text))

            # Highlight CNIC if it matches the search
            cnic = student.cnic or ""
            cnic_item = QTableWidgetItem(cnic)

            if search_term and cnic.lower().find(search_term.lower()) != -1:
                cnic_item.setBackground(Qt.yellow)
                if 'CNIC' in reasons:
                    cnic_item.setToolTip(f"Match found in CNIC: {cnic}")

            self.parent.students_table.setItem(row, 4, cnic_item)

            # Format admission date
            admission_date = ""
            if student.admission_date:
                admission_date = student.admission_date.strftime("%Y-%m-%d")
            self.parent.students_table.setItem(row, 5, QTableWidgetItem(admission_date))

            # Highlight phone if it matches the search
            phone = student.phone or ""
            phone_item = QTableWidgetItem(phone)

            if search_term and phone.lower().find(search_term.lower()) != -1:
                phone_item.setBackground(Qt.yellow)
                if 'Phone' in reasons:
                    phone_item.setToolTip(f"Match found in phone: {phone}")

            self.parent.students_table.setItem(row, 6, phone_item)

            # Add action buttons based on user permissions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)

            # View button (everyone can view)
            view_btn = QPushButton("View")
            view_btn.setProperty("student_id", student.student_id)
            view_btn.clicked.connect(self.parent.view_student)
            actions_layout.addWidget(view_btn)

            # Edit button (only if user has update permission)
            if self.parent.user_role and self.parent.rbac.check_permission(self.parent.user_role, 'data', 'update'):
                edit_btn = QPushButton("Edit")
                edit_btn.setProperty("student_id", student.student_id)
                edit_btn.clicked.connect(self.parent.edit_student)
                actions_layout.addWidget(edit_btn)

            # Delete button (only if user has delete permission)
            if self.parent.user_role and self.parent.rbac.check_permission(self.parent.user_role, 'data', 'delete'):
                delete_btn = QPushButton("Delete")
                delete_btn.setProperty("student_id", student.student_id)
                delete_btn.clicked.connect(self.parent.delete_student)
                actions_layout.addWidget(delete_btn)

            self.parent.students_table.setCellWidget(row, 7, actions_widget)

    def populate_related_table(self, records, match_reasons=None, search_term=""):
        """
        Populate table for related tables (guardians, medical, etc.)

        Args:
            records: List of records to display
            match_reasons: Dict of record_id: list of reasons for match
            search_term: Current search term for highlighting
        """
        self.parent.students_table.setRowCount(0)

        # Handle different table types
        if self.parent.selected_table == "guardians":
            self._populate_guardians_table(records, match_reasons, search_term)
        elif self.parent.selected_table == "medical_history":
            self._populate_medical_table(records, match_reasons, search_term)
        elif self.parent.selected_table == "education":
            self._populate_education_table(records, match_reasons, search_term)
        elif self.parent.selected_table == "enrollments":
            self._populate_enrollments_table(records, match_reasons, search_term)
        elif self.parent.selected_table == "hostel":
            self._populate_hostel_table(records, match_reasons, search_term)
        elif self.parent.selected_table == "transportation":
            self._populate_transportation_table(records, match_reasons, search_term)

    def _populate_guardians_table(self, records, match_reasons=None, search_term=""):
        """Populate guardians table"""
        for row, guardian in enumerate(records):
            self.parent.students_table.insertRow(row)

            # Get primary key and student ID fields
            id_field = 'student_guardian_id'
            record_id = getattr(guardian, id_field, None)
            student_id = guardian.student_id

            # Add data cells
            self.parent.students_table.setItem(row, 0, QTableWidgetItem(str(record_id)))

            # Add student ID with link to student
            student_id_item = QTableWidgetItem(str(student_id))
            self.parent.students_table.setItem(row, 1, student_id_item)

            # Add name with potential highlighting
            name = guardian.guardian_name or ""
            name_item = QTableWidgetItem(name)
            if search_term and name.lower().find(search_term.lower()) != -1:
                name_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 2, name_item)

            # Add relationship
            self.parent.students_table.setItem(row, 3, QTableWidgetItem(guardian.guardian_relationship or ""))

            # Add contact with potential highlighting
            contact = guardian.guardian_contact_number or ""
            contact_item = QTableWidgetItem(contact)
            if search_term and contact.lower().find(search_term.lower()) != -1:
                contact_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 4, contact_item)

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 5, student_id)

    def _populate_medical_table(self, records, match_reasons=None, search_term=""):
        """Populate medical history table"""
        # Implementation details...
        # Similar to _populate_guardians_table with medical-specific data
        for row, medical in enumerate(records):
            self.parent.students_table.insertRow(row)

            # Add data cells
            self.parent.students_table.setItem(row, 0, QTableWidgetItem(str(medical.medical_id)))

            # Add student ID with link to student
            student_id = medical.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.parent.students_table.setItem(row, 1, student_id_item)

            # Add disability name with potential highlighting
            disability = medical.name_of_disability or ""
            disability_item = QTableWidgetItem(disability)
            if search_term and disability.lower().find(search_term.lower()) != -1:
                disability_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 2, disability_item)

            # Add epilepsy status
            epilepsy = "Yes" if medical.epilepsy else "No"
            self.parent.students_table.setItem(row, 3, QTableWidgetItem(epilepsy))

            # Add drug addiction status
            addiction = "Yes" if medical.drug_addiction_smoking else "No"
            self.parent.students_table.setItem(row, 4, QTableWidgetItem(addiction))

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 5, student_id)

    def _populate_education_table(self, records, match_reasons=None, search_term=""):
        """Populate education history table"""
        # Implementation details...
        # Similar to _populate_guardians_table with education-specific data
        for row, education in enumerate(records):
            self.parent.students_table.insertRow(row)

            # Add data cells
            self.parent.students_table.setItem(row, 0, QTableWidgetItem(str(education.education_id)))

            # Add student ID with link to student
            student_id = education.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.parent.students_table.setItem(row, 1, student_id_item)

            # Add education level with potential highlighting
            level = education.education_level or ""
            level_item = QTableWidgetItem(level)
            if search_term and level.lower().find(search_term.lower()) != -1:
                level_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 2, level_item)

            # Add certificate status
            certificate = "Yes" if education.certificate_attached else "No"
            self.parent.students_table.setItem(row, 3, QTableWidgetItem(certificate))

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 4, student_id)

    def _populate_enrollments_table(self, records, match_reasons=None, search_term=""):
        """Populate enrollments table"""
        # Implementation details...
        # Similar to _populate_guardians_table with enrollment-specific data
        for row, enrollment in enumerate(records):
            self.parent.students_table.insertRow(row)

            # Add data cells
            self.parent.students_table.setItem(row, 0, QTableWidgetItem(str(enrollment.enrollment_id)))

            # Add student ID with link to student
            student_id = enrollment.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.parent.students_table.setItem(row, 1, student_id_item)

            # Add course name/id
            course_display = getattr(enrollment, 'course_name', f'Course #{enrollment.course_id}')
            course_item = QTableWidgetItem(course_display)
            if search_term and str(course_display).lower().find(search_term.lower()) != -1:
                course_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 2, course_item)

            # Add date of enrollment
            date_str = ""
            if enrollment.date_of_enrollment:
                if isinstance(enrollment.date_of_enrollment, str):
                    date_str = enrollment.date_of_enrollment
                else:
                    date_str = enrollment.date_of_enrollment.strftime("%Y-%m-%d")
            self.parent.students_table.setItem(row, 3, QTableWidgetItem(date_str))

            # Add completion status
            completion = "Yes" if enrollment.completion_status else "No"
            self.parent.students_table.setItem(row, 4, QTableWidgetItem(completion))

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 5, student_id)

    def _populate_hostel_table(self, records, match_reasons=None, search_term=""):
        """Populate hostel management table"""
        # Implementation details...
        # Similar to _populate_guardians_table with hostel-specific data
        for row, hostel in enumerate(records):
            self.parent.students_table.insertRow(row)

            # Add data cells
            self.parent.students_table.setItem(row, 0, QTableWidgetItem(str(hostel.hostel_id)))

            # Add student ID with link to student
            student_id = hostel.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.parent.students_table.setItem(row, 1, student_id_item)

            # Add duration of stay
            duration = hostel.duration_of_stay or ""
            duration_item = QTableWidgetItem(duration)
            if search_term and duration.lower().find(search_term.lower()) != -1:
                duration_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 2, duration_item)

            # Add special requirements (truncated)
            requirements = hostel.special_requirements or ""
            if len(requirements) > 50:
                requirements = requirements[:47] + "..."
            requirements_item = QTableWidgetItem(requirements)
            if search_term and hostel.special_requirements and hostel.special_requirements.lower().find(
                    search_term.lower()) != -1:
                requirements_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 3, requirements_item)

            # Add action buttons - using the standard student pattern
            self._add_action_buttons_for_related_table(row, 4, student_id)

    def _populate_transportation_table(self, records, match_reasons=None, search_term=""):
        """Populate transportation table"""
        # Implementation details...
        # Similar to _populate_guardians_table with transportation-specific data
        for row, transport in enumerate(records):
            self.parent.students_table.insertRow(row)

            # Add data cells
            self.parent.students_table.setItem(row, 0, QTableWidgetItem(str(transport.transport_id)))

            # Add student ID with link to student
            student_id = transport.student_id
            student_id_item = QTableWidgetItem(str(student_id))
            self.parent.students_table.setItem(row, 1, student_id_item)

            # Add responsible person name
            name = transport.pickup_drop_responsible_name or ""
            name_item = QTableWidgetItem(name)
            if search_term and name.lower().find(search_term.lower()) != -1:
                name_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 2, name_item)

            # Add contact number
            contact = transport.pickup_drop_contact_number or ""
            contact_item = QTableWidgetItem(contact)
            if search_term and contact.lower().find(search_term.lower()) != -1:
                contact_item.setBackground(Qt.yellow)
            self.parent.students_table.setItem(row, 3, contact_item)

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
        view_btn.clicked.connect(self.parent.view_student)
        actions_layout.addWidget(view_btn)

        # Edit button (only if user has update permission)
        if self.parent.user_role and self.parent.rbac.check_permission(self.parent.user_role, 'data', 'update'):
            edit_btn = QPushButton("Edit")
            edit_btn.setProperty("student_id", student_id)
            edit_btn.clicked.connect(self.parent.edit_student)
            actions_layout.addWidget(edit_btn)

        # Delete button (only if user has delete permission)
        if self.parent.user_role and self.parent.rbac.check_permission(self.parent.user_role, 'data', 'delete'):
            delete_btn = QPushButton("Delete")
            delete_btn.setProperty("student_id", student_id)
            delete_btn.clicked.connect(self.parent.delete_student)
            actions_layout.addWidget(delete_btn)

        self.parent.students_table.setCellWidget(row, col, actions_widget)