# from app.services.crud_service import CrudService
# from app.models.student_models import Transportation
# from typing import Dict, List, Any, Tuple, Optional, Union
#
#
# class TransportationService(CrudService):
#     """CRUD operations for Transportation table"""
#
#     def __init__(self):
#         super().__init__(Transportation)
#
#     def create_transport_record(self, transport_data: Dict[str, Any]) -> Tuple[bool, Union[Transportation, str]]:
#         """
#         Create a new transportation record with validation
#
#         Args:
#             transport_data: Dictionary with transportation fields
#
#         Returns:
#             Tuple of (success, transportation object or error message)
#         """
#         # Perform validations
#         if 'student_id' not in transport_data:
#             return False, "Student ID is required"
#
#         # Use the generic create method
#         return self.create(transport_data)
#
#     def get_by_student(self, student_id: int) -> Optional[Transportation]:
#         """
#         Get transportation information for a student
#
#         Args:
#             student_id: ID of the student
#
#         Returns:
#             Transportation record or None if not found
#         """
#         records = self.read_all(filters={'student_id': student_id})
#         return records[0] if records else None


# Current Date and Time (UTC): 2025-05-07 13:46:54
# Current User: CryinMonk

from app.services.crud_service import CrudService
from app.models.student_models import Transportation
from typing import Dict, List, Any, Tuple, Optional, Union


class TransportationService(CrudService):
    """CRUD operations for Transportation table"""

    def __init__(self):
        super().__init__(Transportation)

    def create_transport_record(self, transport_data: Dict[str, Any]) -> Tuple[bool, Union[Transportation, str]]:
        """
        Create a new transportation record with validation

        Args:
            transport_data: Dictionary with transportation fields

        Returns:
            Tuple of (success, transportation object or error message)
        """
        # Perform validations
        if 'student_id' not in transport_data:
            return False, "Student ID is required"

        # Use the generic create method
        return self.create(transport_data)

    def get_by_student(self, student_id: int) -> Optional[Transportation]:
        """
        Get transportation information for a student

        Args:
            student_id: ID of the student

        Returns:
            Transportation record or None if not found
        """
        records = self.read_all(filters={'student_id': student_id})
        return records[0] if records else None

    def get_all_by_student(self, student_id: int) -> List[Transportation]:
        """
        Get all transportation records for a student (in case multiple exist)

        Args:
            student_id: ID of the student

        Returns:
            List of transportation records
        """
        return self.read_all(filters={'student_id': student_id})

    def search(self, search_term: str) -> List[Transportation]:
        """
        Search for transportation records based on a search term

        Args:
            search_term: Text to search for in transportation records

        Returns:
            List of matching transportation records
        """
        search_term = search_term.lower().strip()

        # If search term is empty, return all records
        if not search_term:
            return self.read_all()

        # If search term is a number, it might be a student ID or contact number
        if search_term.isdigit():
            # Try to find by student ID first
            student_id = int(search_term)
            transport_records = self.get_all_by_student(student_id)

            if transport_records:
                return transport_records

            # If no records found by student ID, look for contact numbers
            return self.search_by_contact(search_term)

        # Perform a general search across all transportation records
        all_records = self.read_all()
        results = []

        for record in all_records:
            # Search in responsible person name
            if (hasattr(record, 'pickup_drop_responsible_name') and
                    record.pickup_drop_responsible_name and
                    search_term in record.pickup_drop_responsible_name.lower()):
                results.append(record)
                continue

            # Search in contact number
            if (hasattr(record, 'pickup_drop_contact_number') and
                    record.pickup_drop_contact_number and
                    search_term in record.pickup_drop_contact_number):
                results.append(record)
                continue

            # Search in transport type if it exists
            if hasattr(record, 'transport_type') and record.transport_type:
                if search_term in record.transport_type.lower():
                    results.append(record)
                    continue

            # Search in route information if it exists
            if hasattr(record, 'route_information') and record.route_information:
                if search_term in record.route_information.lower():
                    results.append(record)
                    continue

            # Search in additional notes if it exists
            if hasattr(record, 'notes') and record.notes:
                if search_term in record.notes.lower():
                    results.append(record)
                    continue

        return results

    def advanced_search(self, search_term: str) -> Tuple[List[Transportation], Dict[int, List[str]]]:
        """
        Advanced search with match reasons

        Args:
            search_term: Text to search for

        Returns:
            Tuple of (matching records, dictionary of transport_id to list of match reasons)
        """
        search_term = search_term.lower().strip()
        all_records = self.read_all()
        results = []
        match_reasons = {}  # Dictionary to store match reasons

        for record in all_records:
            record_id = record.transport_id
            reasons = []

            # Check student ID
            if search_term.isdigit() and int(search_term) == record.student_id:
                results.append(record)
                reasons.append('Student ID')

            # Check responsible person name
            if (hasattr(record, 'pickup_drop_responsible_name') and
                    record.pickup_drop_responsible_name and
                    search_term in record.pickup_drop_responsible_name.lower()):
                if record not in results:
                    results.append(record)
                reasons.append('Responsible Person')

            # Check contact number
            if (hasattr(record, 'pickup_drop_contact_number') and
                    record.pickup_drop_contact_number and
                    search_term in record.pickup_drop_contact_number):
                if record not in results:
                    results.append(record)
                reasons.append('Contact Number')

            # Check transport type
            if hasattr(record, 'transport_type') and record.transport_type:
                if search_term in record.transport_type.lower():
                    if record not in results:
                        results.append(record)
                    reasons.append('Transport Type')

            # Check route information
            if hasattr(record, 'route_information') and record.route_information:
                if search_term in record.route_information.lower():
                    if record not in results:
                        results.append(record)
                    reasons.append('Route Information')

            # Check notes
            if hasattr(record, 'notes') and record.notes:
                if search_term in record.notes.lower():
                    if record not in results:
                        results.append(record)
                    reasons.append('Notes')

            # Store match reasons if any were found
            if reasons:
                match_reasons[record_id] = reasons

        return results, match_reasons

    def search_by_responsible_person(self, name: str) -> List[Transportation]:
        """
        Search transportation records by responsible person's name

        Args:
            name: Responsible person's name to search for

        Returns:
            List of matching transportation records
        """
        name = name.lower().strip()
        all_records = self.read_all()
        results = []

        for record in all_records:
            if (hasattr(record, 'pickup_drop_responsible_name') and
                    record.pickup_drop_responsible_name and
                    name in record.pickup_drop_responsible_name.lower()):
                results.append(record)

        return results

    def search_by_contact(self, contact: str) -> List[Transportation]:
        """
        Search transportation records by contact number

        Args:
            contact: Contact number to search for (partial matches supported)

        Returns:
            List of matching transportation records
        """
        contact = contact.strip()
        all_records = self.read_all()
        results = []

        for record in all_records:
            if (hasattr(record, 'pickup_drop_contact_number') and
                    record.pickup_drop_contact_number and
                    contact in record.pickup_drop_contact_number):
                results.append(record)

        return results

    def search_by_transport_type(self, transport_type: str) -> List[Transportation]:
        """
        Search transportation records by transport type

        Args:
            transport_type: Type of transportation to search for

        Returns:
            List of matching transportation records
        """
        transport_type = transport_type.lower().strip()
        all_records = self.read_all()
        results = []

        for record in all_records:
            if (hasattr(record, 'transport_type') and
                    record.transport_type and
                    transport_type in record.transport_type.lower()):
                results.append(record)

        return results

    def get_transportation_summary(self, student_id: int) -> Dict[str, Any]:
        """
        Get a summary of a student's transportation arrangements

        Args:
            student_id: ID of the student

        Returns:
            Dictionary with transportation summary information
        """
        record = self.get_by_student(student_id)

        if not record:
            return {
                'student_id': student_id,
                'has_transportation': False,
            }

        return {
            'student_id': student_id,
            'has_transportation': True,
            'responsible_person': getattr(record, 'pickup_drop_responsible_name', None),
            'contact_number': getattr(record, 'pickup_drop_contact_number', None),
            'transport_type': getattr(record, 'transport_type', None),
            'route_information': getattr(record, 'route_information', None),
        }

    def get_students_by_transport_type(self, transport_type: str) -> List[Transportation]:
        """
        Get all students using a specific type of transportation

        Args:
            transport_type: Type of transportation (e.g., 'school_bus', 'private')

        Returns:
            List of transportation records for that transport type
        """
        return self.search_by_transport_type(transport_type)

    def get_students_without_transportation(self) -> List[int]:
        """
        Find student IDs that don't have transportation records

        Returns:
            List of student IDs without transportation arrangements
        """
        # This would require comparing with the student table
        # Implementation would depend on how you want to handle this cross-table check
        # This is a placeholder that should be updated based on your data model
        pass