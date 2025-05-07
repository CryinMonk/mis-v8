# from app.services.crud_service import CrudService
# from app.models.student_models import Enrollment, Student, Course
# from typing import Dict, List, Any, Tuple, Optional, Union
# import datetime
#
#
# class EnrollmentService(CrudService):
#     """CRUD operations for Enrollment table"""
#
#     def __init__(self):
#         super().__init__(Enrollment)
#
#     def create_enrollment(self, enrollment_data: Dict[str, Any]) -> Tuple[bool, Union[Enrollment, str]]:
#         """
#         Create a new enrollment record with validation
#
#         Args:
#             enrollment_data: Dictionary with enrollment fields
#
#         Returns:
#             Tuple of (success, enrollment object or error message)
#         """
#         # Perform validations
#         if 'student_id' not in enrollment_data:
#             return False, "Student ID is required"
#
#         if 'course_id' not in enrollment_data:
#             return False, "Course ID is required"
#
#         # Format date if provided as string
#         if 'date_of_enrollment' in enrollment_data and isinstance(enrollment_data['date_of_enrollment'], str):
#             try:
#                 enrollment_data['date_of_enrollment'] = datetime.datetime.strptime(
#                     enrollment_data['date_of_enrollment'], '%Y-%m-%d').date()
#             except ValueError:
#                 return False, "Invalid date format for date_of_enrollment. Use YYYY-MM-DD."
#
#         # Use the generic create method
#         return self.create(enrollment_data)
#
#     def get_student_enrollments(self, student_id: int) -> List[Dict[str, Any]]:
#         """
#         Get enrollments for a student with course information
#
#         Args:
#             student_id: ID of the student
#
#         Returns:
#             List of enrollment records with course names
#         """
#         db_session = self.db.get_session()
#         try:
#             # Query enrollments with course information
#             enrollments = (
#                 db_session.query(Enrollment, Course.course_name)
#                 .join(Course, Enrollment.course_id == Course.course_id)
#                 .filter(Enrollment.student_id == student_id)
#                 .all()
#             )
#
#             result = []
#             for enrollment, course_name in enrollments:
#                 enrollment_dict = {
#                     'enrollment_id': enrollment.enrollment_id,
#                     'student_id': enrollment.student_id,
#                     'course_id': enrollment.course_id,
#                     'course_name': course_name,
#                     'date_of_enrollment': enrollment.date_of_enrollment.isoformat() if enrollment.date_of_enrollment else None,
#                     'completion_status': enrollment.completion_status
#                 }
#                 result.append(enrollment_dict)
#
#             return result
#         except Exception as e:
#             self.logger.error(f"Error getting enrollments for student #{student_id}: {str(e)}")
#             return []
#         finally:
#             db_session.close()

# Current Date and Time (UTC): 2025-05-07 13:48:27
# Current User: CryinMonk

from app.services.crud_service import CrudService
from app.models.student_models import Enrollment
from typing import Dict, List, Any, Tuple, Optional, Union
from datetime import datetime


class EnrollmentService(CrudService):
    """CRUD operations for Enrollment table"""

    def __init__(self):
        super().__init__(Enrollment)

    def create_enrollment(self, enrollment_data: Dict[str, Any]) -> Tuple[bool, Union[Enrollment, str]]:
        """
        Create a new enrollment record with validation

        Args:
            enrollment_data: Dictionary with enrollment fields

        Returns:
            Tuple of (success, enrollment object or error message)
        """
        # Perform validations
        if 'student_id' not in enrollment_data:
            return False, "Student ID is required"

        if 'course_id' not in enrollment_data:
            return False, "Course ID is required"

        # Use the generic create method
        return self.create(enrollment_data)

    def get_by_student(self, student_id: int) -> List[Enrollment]:
        """
        Get enrollment records for a student

        Args:
            student_id: ID of the student

        Returns:
            List of enrollment records
        """
        return self.read_all(filters={'student_id': student_id})

    def get_by_course(self, course_id: int) -> List[Enrollment]:
        """
        Get enrollment records for a course

        Args:
            course_id: ID of the course

        Returns:
            List of enrollment records
        """
        return self.read_all(filters={'course_id': course_id})

    def search(self, search_term: str) -> List[Enrollment]:
        """
        Search for enrollment records based on a search term

        Args:
            search_term: Text to search for in enrollment records

        Returns:
            List of matching enrollment records
        """
        search_term = search_term.lower().strip()

        # If search term is empty, return all records
        if not search_term:
            return self.read_all()

        # If search term is a number, it might be a student ID or course ID
        if search_term.isdigit():
            # Try to find by student ID
            student_id = int(search_term)
            student_enrollments = self.get_by_student(student_id)

            if student_enrollments:
                return student_enrollments

            # If not found by student ID, try course ID
            course_id = int(search_term)
            course_enrollments = self.get_by_course(course_id)

            if course_enrollments:
                return course_enrollments

        # Check for completion status searches
        if search_term in ['complete', 'completed', 'yes']:
            return self.search_by_completion_status(True)

        if search_term in ['incomplete', 'not complete', 'no']:
            return self.search_by_completion_status(False)

        # Check for date-based searches
        if self._is_date_format(search_term):
            return self.search_by_date(search_term)

        # Perform a general search across all enrollment records
        all_records = self.read_all()
        results = []

        for record in all_records:
            # Search in course-related fields if they exist
            if hasattr(record, 'course_name') and record.course_name:
                if search_term in record.course_name.lower():
                    results.append(record)
                    continue

            # Search in enrollment notes if they exist
            if hasattr(record, 'notes') and record.notes:
                if search_term in record.notes.lower():
                    results.append(record)
                    continue

            # Search in any other text fields
            for field_name in ['instructor', 'location', 'session', 'enrollment_status']:
                if hasattr(record, field_name) and getattr(record, field_name):
                    if search_term in str(getattr(record, field_name)).lower():
                        results.append(record)
                        break

        return results

    def advanced_search(self, search_term: str) -> Tuple[List[Enrollment], Dict[int, List[str]]]:
        """
        Advanced search with match reasons

        Args:
            search_term: Text to search for

        Returns:
            Tuple of (matching records, dictionary of enrollment_id to list of match reasons)
        """
        search_term = search_term.lower().strip()
        all_records = self.read_all()
        results = []
        match_reasons = {}  # Dictionary to store match reasons

        for record in all_records:
            record_id = record.enrollment_id
            reasons = []

            # Check student ID
            if search_term.isdigit() and int(search_term) == record.student_id:
                results.append(record)
                reasons.append('Student ID')

            # Check course ID
            if search_term.isdigit() and int(search_term) == record.course_id:
                if record not in results:
                    results.append(record)
                reasons.append('Course ID')

            # Check completion status
            if search_term in ['complete', 'completed', 'yes']:
                if record.completion_status:
                    if record not in results:
                        results.append(record)
                    reasons.append('Completion Status')
            elif search_term in ['incomplete', 'not complete', 'no']:
                if not record.completion_status:
                    if record not in results:
                        results.append(record)
                    reasons.append('Completion Status')

            # Check date of enrollment
            if hasattr(record, 'date_of_enrollment') and record.date_of_enrollment:
                date_str = ""
                if isinstance(record.date_of_enrollment, datetime):
                    date_str = record.date_of_enrollment.strftime("%Y-%m-%d")
                else:
                    date_str = str(record.date_of_enrollment)

                if search_term in date_str:
                    if record not in results:
                        results.append(record)
                    reasons.append('Enrollment Date')

            # Check course name
            if hasattr(record, 'course_name') and record.course_name:
                if search_term in record.course_name.lower():
                    if record not in results:
                        results.append(record)
                    reasons.append('Course Name')

            # Check notes
            if hasattr(record, 'notes') and record.notes:
                if search_term in record.notes.lower():
                    if record not in results:
                        results.append(record)
                    reasons.append('Notes')

            # Check other text fields
            for field_name, display_name in [
                ('instructor', 'Instructor'),
                ('location', 'Location'),
                ('session', 'Session'),
                ('enrollment_status', 'Status')
            ]:
                if hasattr(record, field_name) and getattr(record, field_name):
                    if search_term in str(getattr(record, field_name)).lower():
                        if record not in results:
                            results.append(record)
                        reasons.append(display_name)

            # Store match reasons if any were found
            if reasons:
                match_reasons[record_id] = reasons

        return results, match_reasons

    def search_by_completion_status(self, is_completed: bool) -> List[Enrollment]:
        """
        Search enrollment records by completion status

        Args:
            is_completed: True for completed enrollments, False for incomplete

        Returns:
            List of matching enrollment records
        """
        all_records = self.read_all()
        results = []

        for record in all_records:
            if record.completion_status == is_completed:
                results.append(record)

        return results

    def search_by_date(self, date_str: str) -> List[Enrollment]:
        """
        Search enrollment records by enrollment date

        Args:
            date_str: Date string to search for

        Returns:
            List of matching enrollment records
        """
        all_records = self.read_all()
        results = []

        for record in all_records:
            if hasattr(record, 'date_of_enrollment') and record.date_of_enrollment:
                # Convert record date to string if it's a datetime object
                record_date_str = ""
                if isinstance(record.date_of_enrollment, datetime):
                    record_date_str = record.date_of_enrollment.strftime("%Y-%m-%d")
                else:
                    record_date_str = str(record.date_of_enrollment)

                if date_str in record_date_str:
                    results.append(record)

        return results

    def search_by_course(self, course_term: str) -> List[Enrollment]:
        """
        Search enrollment records by course name or ID

        Args:
            course_term: Course name or ID to search for

        Returns:
            List of matching enrollment records
        """
        all_records = self.read_all()
        results = []

        # Check if course_term is a course ID
        if course_term.isdigit():
            course_id = int(course_term)
            return self.get_by_course(course_id)

        # Search by course name
        course_term = course_term.lower().strip()

        for record in all_records:
            if hasattr(record, 'course_name') and record.course_name:
                if course_term in record.course_name.lower():
                    results.append(record)

        return results

    def get_student_active_enrollments(self, student_id: int) -> List[Enrollment]:
        """
        Get active (incomplete) enrollments for a student

        Args:
            student_id: ID of the student

        Returns:
            List of active enrollment records
        """
        enrollments = self.get_by_student(student_id)
        return [e for e in enrollments if not e.completion_status]

    def get_student_completed_enrollments(self, student_id: int) -> List[Enrollment]:
        """
        Get completed enrollments for a student

        Args:
            student_id: ID of the student

        Returns:
            List of completed enrollment records
        """
        enrollments = self.get_by_student(student_id)
        return [e for e in enrollments if e.completion_status]

    def get_enrollment_summary(self, student_id: int) -> Dict[str, Any]:
        """
        Get summary of a student's enrollments

        Args:
            student_id: ID of the student

        Returns:
            Dictionary with enrollment summary
        """
        enrollments = self.get_by_student(student_id)
        active_enrollments = [e for e in enrollments if not e.completion_status]
        completed_enrollments = [e for e in enrollments if e.completion_status]

        # Get course names if available
        course_names = []
        for enrollment in enrollments:
            if hasattr(enrollment, 'course_name') and enrollment.course_name:
                course_names.append(enrollment.course_name)
            else:
                course_names.append(f"Course #{enrollment.course_id}")

        # Get most recent enrollment date
        latest_date = None
        for enrollment in enrollments:
            if hasattr(enrollment, 'date_of_enrollment') and enrollment.date_of_enrollment:
                if latest_date is None or enrollment.date_of_enrollment > latest_date:
                    latest_date = enrollment.date_of_enrollment

        return {
            'student_id': student_id,
            'total_enrollments': len(enrollments),
            'active_enrollments': len(active_enrollments),
            'completed_enrollments': len(completed_enrollments),
            'course_names': course_names,
            'latest_enrollment_date': latest_date,
        }

    def _is_date_format(self, text: str) -> bool:
        """
        Check if text appears to be in a date format

        Args:
            text: Text to check

        Returns:
            True if text appears to be a date, False otherwise
        """
        date_formats = [
            "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y",  # Hyphen formats
            "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y",  # Slash formats
            "%d.%m.%Y", "%Y.%m.%d",  # Dot formats
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