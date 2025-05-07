from PyQt5.QtWidgets import QMessageBox, QApplication
from datetime import datetime


class StudentSearchHandler:
    """Handles search functionality for StudentCrudWidget"""

    def __init__(self, parent_widget):
        self.parent = parent_widget

    def search_students(self):
        """Search for students or related records based on current table selection"""
        search_term = self.parent.search_input.text().strip()
        if not search_term:
            # Use refresh_current_view to properly handle different tables
            self.parent.refresh_current_view()
            return

        try:
            # Show searching indicator
            self.parent.status_label.setText("Searching...")
            QApplication.processEvents()  # Update UI

            # Log the search
            self.parent.utils._log_activity(f"Searching for {self.parent.selected_table} with term: '{search_term}'")

            # Perform table-specific search
            if self.parent.selected_table == "students":
                self._search_students_table(search_term)
            elif self.parent.selected_table == "guardians":
                self._search_guardians_table(search_term)
            elif self.parent.selected_table == "medical_history":
                self._search_medical_table(search_term)
            elif self.parent.selected_table == "education":
                self._search_education_table(search_term)
            elif self.parent.selected_table == "enrollments":
                self._search_enrollments_table(search_term)
            elif self.parent.selected_table == "hostel":
                self._search_hostel_table(search_term)
            elif self.parent.selected_table == "transportation":
                self._search_transportation_table(search_term)
            else:
                # Fallback to generic search for unknown tables
                self._search_generic_table(search_term)

            # Change background color of search input to indicate active search
            self.parent.search_input.setStyleSheet("background-color: #FFFFD0;")  # Light yellow

        except Exception as e:
            self.parent.logger.error(f"Error searching {self.parent.selected_table}: {str(e)}")
            QMessageBox.critical(self.parent, "Error", f"Search failed: {str(e)}")

    def _search_students_table(self, search_term):
        """Specialized search for students table"""
        # Get search results and match reasons for students
        students, match_reasons = self.parent.student_service.advanced_search(search_term)
        self.parent.table_manager.populate_table(students, match_reasons, search_term)
        count = len(students)
        self.parent.status_label.setText(f"Found {count} matching students")

        # Show message if no results
        if count == 0:
            QMessageBox.information(
                self.parent,
                "No Results",
                f"No students found matching '{search_term}'."
            )

    def _search_guardians_table(self, search_term):
        """Specialized search for guardians table"""
        service = self.parent.table_manager.get_service_for_table("guardians")
        if not service:
            self._handle_missing_service("guardians")
            return

        try:
            # Try advanced search first
            if hasattr(service, 'advanced_search'):
                guardians, match_reasons = service.advanced_search(search_term)
                self.parent.table_manager.populate_related_table(guardians, match_reasons, search_term)
            else:
                # Use specialized guardian search if available
                if hasattr(service, 'search_guardians'):
                    guardians = service.search_guardians(search_term)
                else:
                    # Fall back to basic search
                    guardians = service.search(search_term)

                self.parent.table_manager.populate_related_table(guardians, None, search_term)

            count = len(guardians)
            self.parent.status_label.setText(f"Found {count} matching guardians")

            # Show message if no results
            if count == 0:
                QMessageBox.information(
                    self.parent,
                    "No Results",
                    f"No guardians found matching '{search_term}'."
                )
        except Exception as e:
            self.parent.logger.error(f"Guardian search error: {str(e)}")
            raise

    def _search_medical_table(self, search_term):
        """Specialized search for medical history table"""
        service = self.parent.table_manager.get_service_for_table("medical_history")
        if not service:
            self._handle_missing_service("medical history")
            return

        try:
            # Determine if search is for a specific condition
            search_for_condition = any(keyword in search_term.lower() for keyword in
                                       ['disability', 'epilepsy', 'addiction', 'drug', 'smoking'])

            # Try specialized medical search if available
            if hasattr(service, 'search_by_condition') and search_for_condition:
                records = service.search_by_condition(search_term)
            elif hasattr(service, 'advanced_search'):
                records, match_reasons = service.advanced_search(search_term)
                self.parent.table_manager.populate_related_table(records, match_reasons, search_term)
                count = len(records)
                self.parent.status_label.setText(f"Found {count} matching medical records")

                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No medical history records found matching '{search_term}'."
                    )
                return
            else:
                # Fall back to basic search
                records = service.search(search_term)

            self.parent.table_manager.populate_related_table(records, None, search_term)
            count = len(records)
            self.parent.status_label.setText(f"Found {count} matching medical records")

            # Show message if no results
            if count == 0:
                QMessageBox.information(
                    self.parent,
                    "No Results",
                    f"No medical history records found matching '{search_term}'."
                )
        except Exception as e:
            self.parent.logger.error(f"Medical search error: {str(e)}")
            raise

    def _search_education_table(self, search_term):
        """Specialized search for education table"""
        service = self.parent.table_manager.get_service_for_table("education")
        if not service:
            self._handle_missing_service("education")
            return

        try:
            self.parent.logger.info(f"Searching for education records with term: '{search_term}'")

            # Handle student ID search with proper type conversion
            if search_term.isdigit():
                self.parent.logger.info(f"Detected student ID search: {search_term}")
                # Convert string to integer for database query
                student_id_int = int(search_term)
                self.parent.logger.info(f"Converted student ID to integer: {student_id_int}")

                # Use integer value with filters
                records = service.read_all(filters={'student_id': student_id_int})

                # Log results
                self.parent.logger.info(f"Found {len(records)} education records for student ID {student_id_int}")

                # Display the results
                self.parent.table_manager.populate_related_table(records, None, search_term)
                count = len(records)
                self.parent.status_label.setText(f"Found {count} matching education records")

                # Show message if no results
                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No education records found for student ID '{search_term}'."
                    )
                return

            # Check if searching for certificate status
            certificate_search = any(term in search_term.lower() for term in
                                     ['certificate', 'certified', 'cert', 'yes', 'no'])

            if hasattr(service, 'search_by_education_level') and not certificate_search:
                records = service.search_by_education_level(search_term)
            elif hasattr(service, 'search_by_certificate_status') and certificate_search:
                has_certificate = 'yes' in search_term.lower() or 'cert' in search_term.lower()
                records = service.search_by_certificate_status(has_certificate)
            elif hasattr(service, 'advanced_search'):
                records, match_reasons = service.advanced_search(search_term)
                self.parent.table_manager.populate_related_table(records, match_reasons, search_term)
                count = len(records)
                self.parent.status_label.setText(f"Found {count} matching education records")

                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No education records found matching '{search_term}'."
                    )
                return
            else:
                # Fall back to basic search
                records = service.search(search_term)

            self.parent.table_manager.populate_related_table(records, None, search_term)
            count = len(records)
            self.parent.status_label.setText(f"Found {count} matching education records")

            # Show message if no results
            if count == 0:
                QMessageBox.information(
                    self.parent,
                    "No Results",
                    f"No education records found matching '{search_term}'."
                )
        except Exception as e:
            self.parent.logger.error(f"Education search error: {str(e)}")
            raise

    def _search_enrollments_table(self, search_term):
        """Specialized search for enrollments table"""
        service = self.parent.table_manager.get_service_for_table("enrollments")
        if not service:
            self._handle_missing_service("enrollments")
            return

        try:
            self.parent.logger.info(f"Searching for enrollment records with term: '{search_term}'")

            # First check if it's a date format - this takes precedence
            is_date_search = self._is_date_format(search_term)

            # Handle numeric searches (could be student_id, course_id, or a numeric date)
            if search_term.isdigit() and not is_date_search:
                self.parent.logger.info(f"Detected numeric search: {search_term}")
                # Convert string to integer for ID fields
                numeric_id = int(search_term)
                self.parent.logger.info(f"Converted to integer for ID search: {numeric_id}")

                # Create a list to collect all results
                all_records = []

                # Try as student_id
                student_records = service.read_all(filters={'student_id': numeric_id})
                if student_records:
                    self.parent.logger.info(f"Found {len(student_records)} records matching student_id {numeric_id}")
                    all_records.extend(student_records)

                # Also try as course_id (might match both)
                course_records = service.read_all(filters={'course_id': numeric_id})
                if course_records:
                    self.parent.logger.info(f"Found {len(course_records)} records matching course_id {numeric_id}")
                    # Only add records not already in all_records
                    for record in course_records:
                        if record not in all_records:
                            all_records.append(record)

                # Also check if this could be part of a year in enrollment date
                # This needs to use the string search for dates
                if hasattr(service, 'search_by_date'):
                    date_records = service.search_by_date(search_term)
                    if date_records:
                        self.parent.logger.info(f"Found {len(date_records)} records matching date with '{search_term}'")
                        # Only add records not already in all_records
                        for record in date_records:
                            if record not in all_records:
                                all_records.append(record)

                # Display the combined results
                self.parent.logger.info(
                    f"Found total of {len(all_records)} enrollment records for numeric search {search_term}")
                self.parent.table_manager.populate_related_table(all_records, None, search_term)
                count = len(all_records)
                self.parent.status_label.setText(f"Found {count} matching enrollment records")

                # Show message if no results
                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No enrollment records found for '{search_term}'."
                    )
                return

            # Handle specific date searches
            if is_date_search and hasattr(service, 'search_by_date'):
                self.parent.logger.info(f"Detected date format search: {search_term}")
                records = service.search_by_date(search_term)

                self.parent.table_manager.populate_related_table(records, None, search_term)
                count = len(records)
                self.parent.status_label.setText(f"Found {count} matching enrollment records")

                # Show message if no results
                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No enrollment records found for date '{search_term}'."
                    )
                return

            # Check for completion status searches
            is_completion_search = any(term in search_term.lower() for term in
                                       ['complete', 'completed', 'completion', 'yes', 'no'])

            if hasattr(service, 'search_by_completion_status') and is_completion_search:
                is_completed = 'yes' in search_term.lower() or 'complete' in search_term.lower()
                records = service.search_by_completion_status(is_completed)
            elif hasattr(service, 'search_by_course'):
                records = service.search_by_course(search_term)
            elif hasattr(service, 'advanced_search'):
                records, match_reasons = service.advanced_search(search_term)
                self.parent.table_manager.populate_related_table(records, match_reasons, search_term)
                count = len(records)
                self.parent.status_label.setText(f"Found {count} matching enrollment records")

                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No enrollment records found matching '{search_term}'."
                    )
                return
            else:
                # Fall back to basic search
                records = service.search(search_term)

            self.parent.table_manager.populate_related_table(records, None, search_term)
            count = len(records)
            self.parent.status_label.setText(f"Found {count} matching enrollment records")

            # Show message if no results
            if count == 0:
                QMessageBox.information(
                    self.parent,
                    "No Results",
                    f"No enrollment records found matching '{search_term}'."
                )
        except Exception as e:
            self.parent.logger.error(f"Enrollment search error: {str(e)}")
            raise

    def _search_hostel_table(self, search_term):
        """Specialized search for hostel table that handles dual-purpose numeric searches"""
        service = self.parent.table_manager.get_service_for_table("hostel")
        if not service:
            self._handle_missing_service("hostel")
            return

        try:
            self.parent.logger.info(f"Searching for hostel records with term: '{search_term}'")
            all_records = []  # To collect results from multiple search approaches
            match_sources = {}  # Track where each record was found

            # Handle numeric search - check both student_id AND duration
            if search_term.isdigit():
                self.parent.logger.info(f"Detected numeric search: {search_term}")

                # 1. Check as student_id (integer)
                student_id_int = int(search_term)
                self.parent.logger.info(f"Checking as student ID (integer): {student_id_int}")

                student_id_records = service.read_all(filters={'student_id': student_id_int})
                if student_id_records:
                    self.parent.logger.info(f"Found {len(student_id_records)} records with student ID {student_id_int}")
                    all_records.extend(student_id_records)

                    # Track which records were found via student ID
                    for record in student_id_records:
                        record_id = getattr(record, 'hostel_id', id(record))
                        match_sources[record_id] = match_sources.get(record_id, []) + ["Student ID"]

                # 2. Also check as duration (string)
                self.parent.logger.info(f"Also checking as duration (string): '{search_term}'")

                # Try using specialized duration search first
                if hasattr(service, 'search_by_duration'):
                    duration_records = service.search_by_duration(search_term)
                    if duration_records:
                        self.parent.logger.info(
                            f"Found {len(duration_records)} records with duration matching '{search_term}'")

                        # Add only new records to avoid duplicates
                        for record in duration_records:
                            if record not in all_records:
                                all_records.append(record)

                            # Track which records were found via duration
                            record_id = getattr(record, 'hostel_id', id(record))
                            match_sources[record_id] = match_sources.get(record_id, []) + ["Duration"]
                else:
                    # Try general search for duration if no specialized method
                    all_db_records = service.read_all()
                    for record in all_db_records:
                        try:
                            duration_field = getattr(record, 'duration_of_stay', None)
                            if duration_field and search_term in duration_field:
                                if record not in all_records:
                                    all_records.append(record)

                                # Track which records were found via duration
                                record_id = getattr(record, 'hostel_id', id(record))
                                match_sources[record_id] = match_sources.get(record_id, []) + ["Duration"]
                        except Exception as e:
                            self.parent.logger.warning(f"Error checking duration: {str(e)}")

                # Display the combined results with match reasons
                combined_count = len(all_records)
                self.parent.logger.info(f"Found total of {combined_count} records from numeric search '{search_term}'")

                # Convert match_sources to the format expected by populate_related_table
                match_reasons = {}
                for record in all_records:
                    record_id = getattr(record, 'hostel_id', id(record))
                    if record_id in match_sources:
                        match_reasons[record_id] = match_sources[record_id]

                self.parent.table_manager.populate_related_table(all_records, match_reasons, search_term)
                self.parent.status_label.setText(f"Found {combined_count} matching hostel records")

                # Show message if no results
                if combined_count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No hostel records found for '{search_term}'."
                    )
                return

            # Handle non-numeric searches
            # Specialized searches based on term
            if hasattr(service, 'search_by_duration'):
                # Try to interpret as duration search
                if any(term in search_term.lower() for term in
                       ['day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years']):
                    records = service.search_by_duration(search_term)
                    self.parent.table_manager.populate_related_table(records, None, search_term)
                    count = len(records)
                    self.parent.status_label.setText(f"Found {count} matching hostel records")

                    if count == 0:
                        QMessageBox.information(
                            self.parent,
                            "No Results",
                            f"No hostel records found with duration matching '{search_term}'."
                        )
                    return

            if hasattr(service, 'search_by_requirements'):
                # Try to interpret as requirements search
                records = service.search_by_requirements(search_term)
                self.parent.table_manager.populate_related_table(records, None, search_term)
                count = len(records)
                self.parent.status_label.setText(f"Found {count} matching hostel records")

                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No hostel records found with requirements matching '{search_term}'."
                    )
                return

            # Try advanced search if available
            if hasattr(service, 'advanced_search'):
                records, match_reasons = service.advanced_search(search_term)
                self.parent.table_manager.populate_related_table(records, match_reasons, search_term)
                count = len(records)
                self.parent.status_label.setText(f"Found {count} matching hostel records")

                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No hostel records found matching '{search_term}'."
                    )
                return

            # Fall back to basic search
            records = service.search(search_term)
            self.parent.table_manager.populate_related_table(records, None, search_term)
            count = len(records)
            self.parent.status_label.setText(f"Found {count} matching hostel records")

            # Show message if no results
            if count == 0:
                QMessageBox.information(
                    self.parent,
                    "No Results",
                    f"No hostel records found matching '{search_term}'."
                )
        except Exception as e:
            self.parent.logger.error(f"Hostel search error: {str(e)}")
            raise

    def _search_transportation_table(self, search_term):
        """Specialized search for transportation table with comprehensive numeric handling"""
        service = self.parent.table_manager.get_service_for_table("transportation")
        if not service:
            self._handle_missing_service("transportation")
            return

        try:
            self.parent.logger.info(f"Searching for transportation records with term: '{search_term}'")
            all_records = []  # To collect results from multiple search approaches
            match_sources = {}  # Track where each record was found

            # Special handling for numeric searches - check both student_id AND contact numbers
            if search_term.isdigit():
                self.parent.logger.info(f"Detected numeric search: {search_term}")

                # 1. Check as student_id (integer)
                student_id_int = int(search_term)
                self.parent.logger.info(f"Checking as student ID (integer): {student_id_int}")

                student_id_records = service.read_all(filters={'student_id': student_id_int})
                if student_id_records:
                    self.parent.logger.info(f"Found {len(student_id_records)} records with student ID {student_id_int}")
                    all_records.extend(student_id_records)

                    # Track which records were found via student ID
                    for record in student_id_records:
                        record_id = getattr(record, 'transport_id', id(record))
                        match_sources[record_id] = match_sources.get(record_id, []) + ["Student ID"]

                # 2. Check as contact number (string)
                self.parent.logger.info(f"Also checking as contact number (string): '{search_term}'")

                # Try using specialized contact search if available
                if hasattr(service, 'search_by_contact'):
                    contact_records = service.search_by_contact(search_term)
                    if contact_records:
                        self.parent.logger.info(
                            f"Found {len(contact_records)} records with contact number matching '{search_term}'")

                        # Add only new records to avoid duplicates
                        for record in contact_records:
                            if record not in all_records:
                                all_records.append(record)

                            # Track which records were found via contact
                            record_id = getattr(record, 'transport_id', id(record))
                            match_sources[record_id] = match_sources.get(record_id, []) + ["Contact Number"]
                else:
                    # Try general search for contact if no specialized method
                    all_db_records = service.read_all()
                    for record in all_db_records:
                        try:
                            # Check both pickup_drop_contact_number field
                            contact_field = getattr(record, 'pickup_drop_contact_number', None)
                            if contact_field and search_term in contact_field:
                                if record not in all_records:
                                    all_records.append(record)

                                # Track which records were found via contact
                                record_id = getattr(record, 'transport_id', id(record))
                                match_sources[record_id] = match_sources.get(record_id, []) + ["Contact Number"]
                        except Exception as e:
                            self.parent.logger.warning(f"Error checking contact number: {str(e)}")

                # Display the combined results with match reasons
                combined_count = len(all_records)
                self.parent.logger.info(f"Found total of {combined_count} records from numeric search '{search_term}'")

                # Convert match_sources to the format expected by populate_related_table
                match_reasons = {}
                for record in all_records:
                    record_id = getattr(record, 'transport_id', id(record))
                    if record_id in match_sources:
                        match_reasons[record_id] = match_sources[record_id]

                self.parent.table_manager.populate_related_table(all_records, match_reasons, search_term)
                self.parent.status_label.setText(f"Found {combined_count} matching transportation records")

                # Show message if no results
                if combined_count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No transportation records found for '{search_term}'."
                    )
                return

            # Handle non-wholly-numeric searches (could still be partial phone numbers)
            is_contact_search = any(c.isdigit() for c in search_term)

            if hasattr(service, 'search_by_contact') and is_contact_search:
                records = service.search_by_contact(search_term)
            elif hasattr(service, 'search_by_responsible_person'):
                records = service.search_by_responsible_person(search_term)
            elif hasattr(service, 'advanced_search'):
                records, match_reasons = service.advanced_search(search_term)
                self.parent.table_manager.populate_related_table(records, match_reasons, search_term)
                count = len(records)
                self.parent.status_label.setText(f"Found {count} matching transportation records")

                if count == 0:
                    QMessageBox.information(
                        self.parent,
                        "No Results",
                        f"No transportation records found matching '{search_term}'."
                    )
                return
            else:
                # Fall back to basic search
                records = service.search(search_term)

            self.parent.table_manager.populate_related_table(records, None, search_term)
            count = len(records)
            self.parent.status_label.setText(f"Found {count} matching transportation records")

            # Show message if no results
            if count == 0:
                QMessageBox.information(
                    self.parent,
                    "No Results",
                    f"No transportation records found matching '{search_term}'."
                )
        except Exception as e:
            self.parent.logger.error(f"Transportation search error: {str(e)}")
            raise

    def _search_generic_table(self, search_term):
        """Generic search for any table type"""
        # Get the appropriate service for the selected table
        service = self.parent.table_manager.get_service_for_table(self.parent.selected_table)
        if not service:
            self._handle_missing_service(self.parent.selected_table)
            return

        try:
            # Assume each service has a search method
            if hasattr(service, 'advanced_search'):
                records, match_reasons = service.advanced_search(search_term)
                self.parent.table_manager.populate_related_table(records, match_reasons, search_term)
            else:
                # Fallback to basic search if advanced_search is not available
                records = service.search(search_term)
                self.parent.table_manager.populate_related_table(records)

            count = len(records)
            self.parent.status_label.setText(f"Found {count} matching {self.parent.selected_table}")

            # If no results found, show a message
            if count == 0:
                QMessageBox.information(
                    self.parent,
                    "No Results",
                    f"No {self.parent.selected_table} found matching '{search_term}'."
                )
        except Exception as e:
            self.parent.logger.error(f"Generic search error: {str(e)}")
            raise

    def _handle_missing_service(self, table_name):
        """Handle case when service is not available"""
        self.parent.students_table.setRowCount(0)
        self.parent.status_label.setText(f"Search not available for {table_name}")
        QMessageBox.information(
            self.parent,
            "Service Not Available",
            f"The search service for {table_name} is not implemented yet."
        )

    def _is_date_format(self, text):
        """Check if text appears to be in a date format"""
        date_formats = [
            "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y",  # Hyphen formats
            "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y",  # Slash formats
            "%d.%m.%Y", "%Y.%m.%d",  # Dot formats
            "%b %d %Y", "%d %b %Y", "%B %d %Y"  # Month name formats
        ]

        # Check for common date separators
        has_separator = any(sep in text for sep in ['/', '-', '.'])

        # Quick check before trying conversions
        if not has_separator and not text.replace(' ', '').isalnum():
            return False

        # Try each format
        for date_format in date_formats:
            try:
                datetime.strptime(text, date_format)
                return True
            except ValueError:
                continue

        return False

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

    def show_search_info(self):
        """Show information about search capabilities"""
        self.parent.utils._log_activity("Viewed search help information")

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
                "Medical history - Keywords from medical history",
                "Epilepsy - Search for 'epilepsy' or 'yes'/'no'",
                "Drug addiction - Search for 'addiction', 'drug', or 'yes'/'no'"
            ],
            "education": [
                "Student ID - Associated student ID",
                "Education level - Full or partial education level",
                "Certificate - Search for 'certificate', 'yes', or 'no'"
            ],
            "enrollments": [
                "Student ID - Associated student ID",
                "Course ID or name - Full or partial course information",
                "Enrollment date - Date in YYYY-MM-DD format",
                "Completion status - Search for 'completed', 'yes', or 'no'"
            ],
            "hostel": [
                "Student ID - Associated student ID",
                "Duration of stay - Full or partial duration (e.g., 'days', 'weeks', 'months')",
                "Special requirements - Keywords from requirements"
            ],
            "transportation": [
                "Student ID - Associated student ID",
                "Responsible person - Full or partial name",
                "Contact number - Full or partial contact number"
            ]
        }

        # Get search fields for current table
        current_fields = search_help.get(self.parent.selected_table, ["No specific search fields available"])

        # Get table display name
        table_display_name = next((option["display"] for option in self.parent.table_options
                                   if option["id"] == self.parent.selected_table),
                                  self.parent.selected_table.capitalize())

        # Build HTML message
        message = f"<h3>Search Capabilities for {table_display_name}</h3>"
        message += "<p>You can search using any of the following information:</p><ul>"

        for field in current_fields:
            message += f"<li><b>{field}</b></li>"

        message += "</ul><p>Simply enter any of the above information in the search box and click Search.</p>"
        message += "<p>You can press Reset to show all records again.</p>"

        # Add specific examples for the current table
        examples = self._get_search_examples_for_table(self.parent.selected_table)
        if examples:
            message += "<h4>Examples:</h4><ul>"
            for example in examples:
                message += f"<li>{example}</li>"
            message += "</ul>"

        QMessageBox.information(self.parent, "Search Help", message)

    def _get_search_examples_for_table(self, table_name):
        """Get search examples specific to each table"""
        examples = {
            "students": [
                "Enter a name like 'Smith' to find all students with that name",
                "Enter a CNIC number like '12345' to find matching records",
                "Enter a phone number to find students with matching contact info"
            ],
            "guardians": [
                "Enter a student ID to find all guardians for that student",
                "Enter a relationship like 'father' or 'mother' to find all matching guardians",
                "Enter a phone number to find guardians with matching contact info"
            ],
            "medical_history": [
                "Enter 'epilepsy' to find students with epilepsy",
                "Enter 'yes' to find students with drug addiction marked as yes",
                "Enter a disability name to find matching conditions"
            ],
            "education": [
                "Enter an education level like 'secondary' or 'university'",
                "Enter 'certificate yes' to find records with certificates attached",
                "Enter a student ID to find education history for that student"
            ],
            "enrollments": [
                "Enter a date like '2024-01-15' to find enrollments from that date",
                "Enter 'completed' to find all completed courses",
                "Enter a course name to find all enrollments in that course"
            ],
            "hostel": [
                "Enter '6 months' to find students staying for that duration",
                "Enter keywords like 'dietary' to find special requirements",
                "Enter a student ID to find hostel info for that student"
            ],
            "transportation": [
                "Enter a name to find responsible persons for transportation",
                "Enter a phone number to find matching contact information",
                "Enter a student ID to find transportation details for that student"
            ]
        }

        return examples.get(table_name, [])