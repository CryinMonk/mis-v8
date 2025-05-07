# from app.services.crud_service import CrudService
# from app.models.student_models import HostelManagement
# from typing import Dict, List, Any, Tuple, Optional, Union
#
#
# class HostelService(CrudService):
#     """CRUD operations for Hostel Management table"""
#
#     def __init__(self):
#         super().__init__(HostelManagement)
#
#     def create_hostel_record(self, hostel_data: Dict[str, Any]) -> Tuple[bool, Union[HostelManagement, str]]:
#         """
#         Create a new hostel record with validation
#
#         Args:
#             hostel_data: Dictionary with hostel fields
#
#         Returns:
#             Tuple of (success, hostel object or error message)
#         """
#         # Perform validations
#         if 'student_id' not in hostel_data:
#             return False, "Student ID is required"
#
#         # Use the generic create method
#         return self.create(hostel_data)
#
#     def get_by_student(self, student_id: int) -> Optional[HostelManagement]:
#         """
#         Get hostel information for a student
#
#         Args:
#             student_id: ID of the student
#
#         Returns:
#             Hostel record or None if not found
#         """
#         records = self.read_all(filters={'student_id': student_id})
#         return records[0] if records else None


# Current Date and Time (UTC): 2025-05-07 13:50:29
# Current User's Login: CryinMonk

from app.services.crud_service import CrudService
from app.models.student_models import HostelManagement
from typing import Dict, List, Any, Tuple, Optional, Union


class HostelService(CrudService):
    """CRUD operations for Hostel Management table"""

    def __init__(self):
        super().__init__(HostelManagement)

    def create_hostel_record(self, hostel_data: Dict[str, Any]) -> Tuple[bool, Union[HostelManagement, str]]:
        """
        Create a new hostel record with validation

        Args:
            hostel_data: Dictionary with hostel fields

        Returns:
            Tuple of (success, hostel object or error message)
        """
        # Perform validations
        if 'student_id' not in hostel_data:
            return False, "Student ID is required"

        # Use the generic create method
        return self.create(hostel_data)

    def get_by_student(self, student_id: int) -> Optional[HostelManagement]:
        """
        Get hostel information for a student

        Args:
            student_id: ID of the student

        Returns:
            Hostel record or None if not found
        """
        records = self.read_all(filters={'student_id': student_id})
        return records[0] if records else None

    def get_all_by_student(self, student_id: int) -> List[HostelManagement]:
        """
        Get all hostel records for a student (in case multiple exist)

        Args:
            student_id: ID of the student

        Returns:
            List of hostel records
        """
        return self.read_all(filters={'student_id': student_id})

    def search(self, search_term: str) -> List[HostelManagement]:
        """
        Search for hostel records based on a search term

        Args:
            search_term: Text to search for in hostel records

        Returns:
            List of matching hostel records
        """
        search_term = search_term.lower().strip()

        # If search term is empty, return all records
        if not search_term:
            return self.read_all()

        # If search term is a number, it might be a student ID
        if search_term.isdigit():
            # Try to find by student ID
            student_id = int(search_term)
            hostel_records = self.get_all_by_student(student_id)

            if hostel_records:
                return hostel_records

        # Check for duration-based searches
        if any(word in search_term for word in ['day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years']):
            return self.search_by_duration(search_term)

        # Perform a general search across all hostel records
        all_records = self.read_all()
        results = []

        for record in all_records:
            # Search in duration of stay
            if record.duration_of_stay and search_term in record.duration_of_stay.lower():
                results.append(record)
                continue

            # Search in special requirements
            if record.special_requirements and search_term in record.special_requirements.lower():
                results.append(record)
                continue

            # Search in any other fields that might exist
            for field_name in ['room_number', 'building', 'floor', 'status', 'notes']:
                if hasattr(record, field_name) and getattr(record, field_name):
                    if search_term in str(getattr(record, field_name)).lower():
                        results.append(record)
                        break

        return results

    def advanced_search(self, search_term: str) -> Tuple[List[HostelManagement], Dict[int, List[str]]]:
        """
        Advanced search with match reasons

        Args:
            search_term: Text to search for

        Returns:
            Tuple of (matching records, dictionary of hostel_id to list of match reasons)
        """
        search_term = search_term.lower().strip()
        all_records = self.read_all()
        results = []
        match_reasons = {}  # Dictionary to store match reasons

        for record in all_records:
            record_id = record.hostel_id
            reasons = []

            # Check student ID
            if search_term.isdigit() and int(search_term) == record.student_id:
                results.append(record)
                reasons.append('Student ID')

            # Check duration of stay
            if record.duration_of_stay and search_term in record.duration_of_stay.lower():
                if record not in results:
                    results.append(record)
                reasons.append('Duration of Stay')

            # Check special requirements
            if record.special_requirements and search_term in record.special_requirements.lower():
                if record not in results:
                    results.append(record)
                reasons.append('Special Requirements')

            # Check other fields
            for field_name, display_name in [
                ('room_number', 'Room Number'),
                ('building', 'Building'),
                ('floor', 'Floor'),
                ('status', 'Status'),
                ('notes', 'Notes')
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

    def search_by_duration(self, duration_term: str) -> List[HostelManagement]:
        """
        Search hostel records by duration of stay

        Args:
            duration_term: Duration term to search for (e.g., "6 months")

        Returns:
            List of matching hostel records
        """
        duration_term = duration_term.lower().strip()
        all_records = self.read_all()
        results = []

        for record in all_records:
            if record.duration_of_stay and duration_term in record.duration_of_stay.lower():
                results.append(record)

        return results

    def search_by_requirements(self, requirements_term: str) -> List[HostelManagement]:
        """
        Search hostel records by special requirements

        Args:
            requirements_term: Requirements term to search for

        Returns:
            List of matching hostel records
        """
        requirements_term = requirements_term.lower().strip()
        all_records = self.read_all()
        results = []

        for record in all_records:
            if record.special_requirements and requirements_term in record.special_requirements.lower():
                results.append(record)

        return results

    def get_by_room(self, room_number: str) -> List[HostelManagement]:
        """
        Get hostel records by room number

        Args:
            room_number: Room number to search for

        Returns:
            List of hostel records for that room
        """
        all_records = self.read_all()
        results = []

        for record in all_records:
            if hasattr(record, 'room_number') and record.room_number:
                if str(record.room_number) == str(room_number):
                    results.append(record)

        return results

    def get_by_building(self, building: str) -> List[HostelManagement]:
        """
        Get hostel records by building

        Args:
            building: Building name or number to search for

        Returns:
            List of hostel records for that building
        """
        building = building.lower().strip()
        all_records = self.read_all()
        results = []

        for record in all_records:
            if hasattr(record, 'building') and record.building:
                if building in record.building.lower():
                    results.append(record)

        return results

    def get_hostel_summary(self, student_id: int) -> Dict[str, Any]:
        """
        Get a summary of a student's hostel information

        Args:
            student_id: ID of the student

        Returns:
            Dictionary with hostel summary information
        """
        record = self.get_by_student(student_id)

        if not record:
            return {
                'student_id': student_id,
                'has_hostel': False,
            }

        # Create a summary with available fields
        summary = {
            'student_id': student_id,
            'has_hostel': True,
            'duration_of_stay': record.duration_of_stay,
            'special_requirements': record.special_requirements,
        }

        # Add additional fields if they exist
        for field_name in ['room_number', 'building', 'floor', 'status']:
            if hasattr(record, field_name):
                summary[field_name] = getattr(record, field_name)

        return summary

    def get_students_with_special_requirements(self) -> List[HostelManagement]:
        """
        Get all hostel records for students with special requirements

        Returns:
            List of hostel records with special requirements
        """
        all_records = self.read_all()
        results = []

        for record in all_records:
            if record.special_requirements and record.special_requirements.strip():
                results.append(record)

        return results

    def get_students_by_duration_category(self) -> Dict[str, List[HostelManagement]]:
        """
        Categorize students by their duration of stay in the hostel

        Returns:
            Dictionary mapping duration categories to lists of hostel records
        """
        all_records = self.read_all()
        categories = {
            'short_term': [],  # Less than 3 months
            'medium_term': [],  # 3-6 months
            'long_term': [],  # More than 6 months
            'unknown': []  # Duration not specified or not parseable
        }

        for record in all_records:
            if not record.duration_of_stay or not record.duration_of_stay.strip():
                categories['unknown'].append(record)
                continue

            duration_lower = record.duration_of_stay.lower()

            # Try to determine duration category based on text
            if any(term in duration_lower for term in ['day', 'week', '1 month', '2 month']):
                categories['short_term'].append(record)
            elif any(term in duration_lower for term in ['3 month', '4 month', '5 month', '6 month', 'semester']):
                categories['medium_term'].append(record)
            elif any(term in duration_lower for term in
                     ['year', '7 month', '8 month', '9 month', '10 month', '11 month', '12 month']):
                categories['long_term'].append(record)
            else:
                # Try to parse numeric values
                import re
                number_match = re.search(r'(\d+)', duration_lower)
                if number_match:
                    number = int(number_match.group(1))

                    if 'month' in duration_lower:
                        if number < 3:
                            categories['short_term'].append(record)
                        elif number <= 6:
                            categories['medium_term'].append(record)
                        else:
                            categories['long_term'].append(record)
                    elif 'year' in duration_lower or 'yr' in duration_lower:
                        categories['long_term'].append(record)
                    elif 'week' in duration_lower:
                        categories['short_term'].append(record)
                    elif 'day' in duration_lower:
                        categories['short_term'].append(record)
                    else:
                        categories['unknown'].append(record)
                else:
                    categories['unknown'].append(record)

        return categories