# from app.services.crud_service import CrudService
# from app.models.student_models import EducationHistory
# from typing import Dict, List, Any, Tuple, Union
#
#
# class EducationService(CrudService):
#     """CRUD operations for Education History table"""
#
#     def __init__(self):
#         super().__init__(EducationHistory)
#
#     def create_education_record(self, education_data: Dict[str, Any]) -> Tuple[bool, Union[EducationHistory, str]]:
#         """
#         Create a new education record with validation
#
#         Args:
#             education_data: Dictionary with education fields
#
#         Returns:
#             Tuple of (success, education object or error message)
#         """
#         # Perform validations
#         if 'student_id' not in education_data:
#             return False, "Student ID is required"
#
#         if 'education_level' not in education_data or not education_data['education_level']:
#             return False, "Education level is required"
#
#         # Use the generic create method
#         return self.create(education_data)
#
#     def get_by_student(self, student_id: int) -> List[EducationHistory]:
#         """
#         Get education records for a student
#
#         Args:
#             student_id: ID of the student
#
#         Returns:
#             List of education records
#         """
#         return self.read_all(filters={'student_id': student_id})


# Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-05-07 14:25:42
# Current User's Login: CryinMonk

from app.services.crud_service import CrudService
from app.models.student_models import EducationHistory
from typing import Dict, List, Any, Tuple, Union, Optional
import logging

# Get the logger
logger = logging.getLogger("root")


class EducationService(CrudService):
    """CRUD operations for Education History table"""

    def __init__(self):
        super().__init__(EducationHistory)

    def create_education_record(self, education_data: Dict[str, Any]) -> Tuple[bool, Union[EducationHistory, str]]:
        """
        Create a new education record with validation

        Args:
            education_data: Dictionary with education fields

        Returns:
            Tuple of (success, education object or error message)
        """
        # Perform validations
        if 'student_id' not in education_data:
            return False, "Student ID is required"

        if 'education_level' not in education_data or not education_data['education_level']:
            return False, "Education level is required"

        # Use the generic create method
        return self.create(education_data)

    def get_by_student(self, student_id: Union[int, str]) -> List[EducationHistory]:
        """
        Get education records for a student with proper type handling

        Args:
            student_id: ID of the student (can be int or string)

        Returns:
            List of education records
        """
        # Handle type conversion if needed
        if isinstance(student_id, str) and student_id.isdigit():
            student_id = int(student_id)
            logger.info(f"Converting student_id parameter to integer: {student_id}")

        # Use read_all with properly typed student_id
        records = self.read_all(filters={'student_id': student_id})
        return records

    def read_all(self, filters: Dict[str, Any] = None) -> List[EducationHistory]:
        """
        Get all education records, optionally filtered, with proper type handling

        Args:
            filters: Dictionary of field:value pairs to filter by

        Returns:
            List of education history records
        """
        # Process filters for proper type conversion
        if filters and 'student_id' in filters and isinstance(filters['student_id'], str):
            if filters['student_id'].isdigit():
                logger.info(f"Converting student_id filter from string '{filters['student_id']}' to integer")
                # Create a new copy of filters to avoid modifying the original
                filters = dict(filters)
                filters['student_id'] = int(filters['student_id'])

        # Call the parent implementation with the processed filters
        return super().read_all(filters)

    def search(self, search_term: str) -> List[EducationHistory]:
        """
        Search for education records based on a search term with proper type handling

        Args:
            search_term: Text to search for in education records

        Returns:
            List of matching education records
        """
        # Trim whitespace and make lowercase
        search_term = search_term.lower().strip()

        # If search term is empty, return all records
        if not search_term:
            return self.read_all()

        # Handle student ID searches with proper type conversion
        if search_term.isdigit():
            # Convert to integer for proper database query
            student_id_int = int(search_term)
            logger.info(f"Search method using integer student ID: {student_id_int}")

            # Use read_all with integer student_id directly
            results = self.read_all(filters={'student_id': student_id_int})
            logger.info(f"Found {len(results)} records for student ID {student_id_int}")
            return results

        # Check for certificate-related searches
        if search_term in ['certificate', 'yes', 'no', 'cert']:
            has_certificate = 'yes' in search_term.lower() or 'certificate' in search_term.lower() or 'cert' in search_term.lower()
            return self.search_by_certificate_status(has_certificate)

        # Perform a general search across all education records
        all_records = self.read_all()
        results = []

        for record in all_records:
            try:
                # Check if student ID matches as string (for partial student ID searches)
                record_id_str = str(getattr(record, 'student_id', ''))
                if record_id_str and search_term in record_id_str:
                    results.append(record)
                    continue

                # Search in education level
                if record.education_level and search_term in record.education_level.lower():
                    results.append(record)
                    continue

                # Search in any institution field if exists
                if hasattr(record, 'institution') and record.institution and search_term in record.institution.lower():
                    results.append(record)
                    continue

                # Search in any grade field if exists
                if hasattr(record, 'grade') and record.grade and search_term in record.grade.lower():
                    results.append(record)
                    continue

                # Search in any comments or notes field if exists
                if hasattr(record, 'comments') and record.comments and search_term in record.comments.lower():
                    results.append(record)
                    continue

                # Search in any year field if exists
                if hasattr(record, 'year_completed') and record.year_completed and search_term in str(
                        record.year_completed).lower():
                    results.append(record)
                    continue
            except Exception as e:
                logger.warning(f"Error in general search: {str(e)}")

        logger.info(f"General search found {len(results)} records for term '{search_term}'")
        return results

    def advanced_search(self, search_term: str) -> Tuple[List[EducationHistory], Dict[int, List[str]]]:
        """
        Advanced search with match reasons, with proper type handling

        Args:
            search_term: Text to search for

        Returns:
            Tuple of (matching records, dictionary of education_id to list of match reasons)
        """
        search_term = search_term.lower().strip()
        match_reasons = {}  # Dictionary to store match reasons

        # Handle student ID searches directly with proper type conversion
        if search_term.isdigit():
            student_id_int = int(search_term)
            logger.info(f"Advanced search with student ID (converted to int): {student_id_int}")

            # Get records with the proper numeric type
            results = self.read_all(filters={'student_id': student_id_int})

            # Add match reasons for student ID matches
            for record in results:
                match_reasons[record.education_id] = ['Student ID']

            return results, match_reasons

        # For non-student ID searches, use the existing code
        all_records = self.read_all()
        results = []

        for record in all_records:
            record_id = record.education_id
            reasons = []

            # Check education level
            if record.education_level and search_term in record.education_level.lower():
                if record not in results:
                    results.append(record)
                reasons.append('Education Level')

            # Check certificate status for specific searches
            if search_term in ['certificate', 'yes', 'no', 'cert']:
                is_cert_search = search_term in ['certificate', 'yes', 'cert']
                if (is_cert_search and record.certificate_attached) or (
                        not is_cert_search and not record.certificate_attached):
                    if record not in results:
                        results.append(record)
                    reasons.append('Certificate Status')

            # Check institution if exists
            if hasattr(record, 'institution') and record.institution and search_term in record.institution.lower():
                if record not in results:
                    results.append(record)
                reasons.append('Institution')

            # Check grade if exists
            if hasattr(record, 'grade') and record.grade and search_term in record.grade.lower():
                if record not in results:
                    results.append(record)
                reasons.append('Grade')

            # Check comments/notes if exists
            if hasattr(record, 'comments') and record.comments and search_term in record.comments.lower():
                if record not in results:
                    results.append(record)
                reasons.append('Comments')

            # Check year completed if exists
            if hasattr(record, 'year_completed') and record.year_completed and search_term in str(
                    record.year_completed).lower():
                if record not in results:
                    results.append(record)
                reasons.append('Year Completed')

            # Store match reasons if any were found
            if reasons:
                match_reasons[record_id] = reasons

        return results, match_reasons

    def search_by_education_level(self, level: str) -> List[EducationHistory]:
        """
        Search education history by education level

        Args:
            level: Education level to search for (e.g., 'primary', 'secondary')

        Returns:
            List of education records with matching level
        """
        level = level.lower().strip()
        all_records = self.read_all()
        results = []

        for record in all_records:
            if record.education_level and level in record.education_level.lower():
                results.append(record)

        return results

    def search_by_certificate_status(self, has_certificate: bool) -> List[EducationHistory]:
        """
        Search education records by certificate attached status

        Args:
            has_certificate: True to find records with certificates, False for without

        Returns:
            List of matching education records
        """
        all_records = self.read_all()
        results = []

        for record in all_records:
            if record.certificate_attached == has_certificate:
                results.append(record)

        return results

    def get_highest_education(self, student_id: int) -> Optional[EducationHistory]:
        """
        Get the highest education level for a student

        Args:
            student_id: ID of the student

        Returns:
            Education record with highest level or None if no records
        """
        records = self.get_by_student(student_id)

        if not records:
            return None

        # Define education level hierarchy (lower index = higher level)
        education_levels = {
            'university': 0,
            'college': 1,
            'higher': 2,
            'secondary': 3,
            'middle': 4,
            'primary': 5,
            'elementary': 6,
            'none': 7,
        }

        highest_record = records[0]
        highest_rank = 999  # Start with a high number (lower is better)

        for record in records:
            # Find the best matching education level in our hierarchy
            current_rank = 999
            for level_name, rank in education_levels.items():
                if level_name in record.education_level.lower():
                    current_rank = min(current_rank, rank)  # Use the highest rank found

            # Update highest record if this one has a higher rank
            if current_rank < highest_rank:
                highest_rank = current_rank
                highest_record = record

        return highest_record

    def get_education_summary(self, student_id: int) -> Dict[str, Any]:
        """
        Get summary of student's education history

        Args:
            student_id: ID of the student

        Returns:
            Dictionary with education summary information
        """
        records = self.get_by_student(student_id)

        if not records:
            return {
                'student_id': student_id,
                'record_count': 0,
                'has_certificate': False,
                'highest_level': None,
            }

        # Get highest education
        highest_education = self.get_highest_education(student_id)

        # Check if any records have certificates
        has_certificate = any(record.certificate_attached for record in records)

        # Create summary
        return {
            'student_id': student_id,
            'record_count': len(records),
            'has_certificate': has_certificate,
            'highest_level': highest_education.education_level if highest_education else None,
            'education_levels': [record.education_level for record in records],
        }

