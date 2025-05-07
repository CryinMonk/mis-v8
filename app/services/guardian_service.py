# from app.services.crud_service import CrudService
# from app.models.student_models import StudentGuardian
# from typing import Dict, List, Any, Tuple, Union
#
#
# class GuardianService(CrudService):
#     """CRUD operations for Student Guardian table"""
#
#     def __init__(self):
#         super().__init__(StudentGuardian)
#
#     def create_guardian(self, guardian_data: Dict[str, Any]) -> Tuple[bool, Union[StudentGuardian, str]]:
#         """
#         Create a new guardian record with validation
#
#         Args:
#             guardian_data: Dictionary with guardian fields
#
#         Returns:
#             Tuple of (success, guardian object or error message)
#         """
#         # Perform validations
#         if 'student_id' not in guardian_data:
#             return False, "Student ID is required"
#
#         if 'guardian_name' not in guardian_data or not guardian_data['guardian_name']:
#             return False, "Guardian name is required"
#
#         # Use the generic create method
#         return self.create(guardian_data)
#
#     def get_by_student(self, student_id: int) -> List[StudentGuardian]:
#         """
#         Get guardians for a student
#
#         Args:
#             student_id: ID of the student
#
#         Returns:
#             List of guardian records
#         """
#         return self.read_all(filters={'student_id': student_id})


from app.services.crud_service import CrudService
from app.models.student_models import StudentGuardian
from typing import Dict, List, Any, Tuple, Union, Optional


class GuardianService(CrudService):
    """CRUD operations for Student Guardian table"""

    def __init__(self):
        super().__init__(StudentGuardian)

    def create_guardian(self, guardian_data: Dict[str, Any]) -> Tuple[bool, Union[StudentGuardian, str]]:
        """
        Create a new guardian record with validation

        Args:
            guardian_data: Dictionary with guardian fields

        Returns:
            Tuple of (success, guardian object or error message)
        """
        # Perform validations
        if 'student_id' not in guardian_data:
            return False, "Student ID is required"

        if 'guardian_name' not in guardian_data or not guardian_data['guardian_name']:
            return False, "Guardian name is required"

        # Use the generic create method
        return self.create(guardian_data)

    def get_by_student(self, student_id: int) -> List[StudentGuardian]:
        """
        Get guardians for a student

        Args:
            student_id: ID of the student

        Returns:
            List of guardian records
        """
        return self.read_all(filters={'student_id': student_id})

    def search(self, search_term: str) -> List[StudentGuardian]:
        """
        Search for guardian records based on a search term

        Args:
            search_term: Text to search for in guardian records

        Returns:
            List of matching guardian records
        """
        search_term = search_term.lower().strip()

        # If search term is empty, return all records
        if not search_term:
            return self.read_all()

        # If search term is a number, it might be a student ID
        if search_term.isdigit():
            # Try to find by student ID
            student_id_matches = self.get_by_student(int(search_term))
            if student_id_matches:
                return student_id_matches

        # Perform a general search across all guardians
        all_guardians = self.read_all()
        results = []

        for guardian in all_guardians:
            # Search in guardian name
            if guardian.guardian_name and search_term in guardian.guardian_name.lower():
                results.append(guardian)
                continue

            # Search in relationship
            if guardian.guardian_relationship and search_term in guardian.guardian_relationship.lower():
                results.append(guardian)
                continue

            # Search in contact number
            if guardian.guardian_contact_number and search_term in guardian.guardian_contact_number.lower():
                results.append(guardian)
                continue

            # Search in address if exists
            if hasattr(guardian,
                       'guardian_address') and guardian.guardian_address and search_term in guardian.guardian_address.lower():
                results.append(guardian)
                continue

            # Search in email if exists
            if hasattr(guardian,
                       'guardian_email') and guardian.guardian_email and search_term in guardian.guardian_email.lower():
                results.append(guardian)
                continue

            # Search in CNIC if exists
            if hasattr(guardian,
                       'guardian_cnic') and guardian.guardian_cnic and search_term in guardian.guardian_cnic.lower():
                results.append(guardian)
                continue

            # If student ID is in the guardian object and matches the search term
            if str(guardian.student_id) == search_term:
                results.append(guardian)
                continue

        return results

    def advanced_search(self, search_term: str) -> Tuple[List[StudentGuardian], Dict[int, List[str]]]:
        """
        Advanced search with match reasons

        Args:
            search_term: Text to search for

        Returns:
            Tuple of (matching records, dictionary of guardian_id to list of match reasons)
        """
        search_term = search_term.lower().strip()
        all_guardians = self.read_all()
        results = []
        match_reasons = {}  # Dictionary to store match reasons

        for guardian in all_guardians:
            guardian_id = guardian.student_guardian_id
            reasons = []

            # Check student ID
            if str(guardian.student_id) == search_term:
                results.append(guardian)
                reasons.append('Student ID')

            # Check guardian name
            if guardian.guardian_name and search_term in guardian.guardian_name.lower():
                if guardian not in results:
                    results.append(guardian)
                reasons.append('Name')

            # Check relationship
            if guardian.guardian_relationship and search_term in guardian.guardian_relationship.lower():
                if guardian not in results:
                    results.append(guardian)
                reasons.append('Relationship')

            # Check contact number
            if guardian.guardian_contact_number and search_term in guardian.guardian_contact_number.lower():
                if guardian not in results:
                    results.append(guardian)
                reasons.append('Contact')

            # Check address if exists
            if hasattr(guardian,
                       'guardian_address') and guardian.guardian_address and search_term in guardian.guardian_address.lower():
                if guardian not in results:
                    results.append(guardian)
                reasons.append('Address')

            # Check email if exists
            if hasattr(guardian,
                       'guardian_email') and guardian.guardian_email and search_term in guardian.guardian_email.lower():
                if guardian not in results:
                    results.append(guardian)
                reasons.append('Email')

            # Check CNIC if exists
            if hasattr(guardian,
                       'guardian_cnic') and guardian.guardian_cnic and search_term in guardian.guardian_cnic.lower():
                if guardian not in results:
                    results.append(guardian)
                reasons.append('CNIC')

            # Store match reasons if any were found
            if reasons:
                match_reasons[guardian_id] = reasons

        return results, match_reasons

    def search_by_relationship(self, relationship_type: str) -> List[StudentGuardian]:
        """
        Search guardians by relationship type

        Args:
            relationship_type: Type of relationship (e.g., 'father', 'mother')

        Returns:
            List of guardians matching the relationship type
        """
        relationship_type = relationship_type.lower().strip()
        all_guardians = self.read_all()
        results = []

        for guardian in all_guardians:
            if guardian.guardian_relationship and relationship_type in guardian.guardian_relationship.lower():
                results.append(guardian)

        return results

    def search_by_contact(self, contact_info: str) -> List[StudentGuardian]:
        """
        Search guardians by contact information

        Args:
            contact_info: Contact number to search for

        Returns:
            List of guardians with matching contact information
        """
        contact_info = contact_info.strip()
        all_guardians = self.read_all()
        results = []

        for guardian in all_guardians:
            if guardian.guardian_contact_number and contact_info in guardian.guardian_contact_number:
                results.append(guardian)

        return results

    def search_by_name(self, name: str) -> List[StudentGuardian]:
        """
        Search guardians by name

        Args:
            name: Guardian name to search for

        Returns:
            List of guardians with matching names
        """
        name = name.lower().strip()
        all_guardians = self.read_all()
        results = []

        for guardian in all_guardians:
            if guardian.guardian_name and name in guardian.guardian_name.lower():
                results.append(guardian)

        return results

    def get_student_all_guardians(self, student_id: int) -> Dict[str, List[StudentGuardian]]:
        """
        Get all guardians for a student organized by relationship

        Args:
            student_id: ID of the student

        Returns:
            Dictionary mapping relationship types to lists of guardians
        """
        guardians = self.get_by_student(student_id)

        # Organize by relationship
        result = {}
        for guardian in guardians:
            relationship = guardian.guardian_relationship or "Other"
            if relationship not in result:
                result[relationship] = []
            result[relationship].append(guardian)

        return result

    def get_primary_guardian(self, student_id: int) -> Optional[StudentGuardian]:
        """
        Get primary guardian for a student (first guardian or one with 'primary' in relationship)

        Args:
            student_id: ID of the student

        Returns:
            Primary guardian or None if no guardians found
        """
        guardians = self.get_by_student(student_id)

        if not guardians:
            return None

        # Look for a guardian with 'primary' in relationship
        for guardian in guardians:
            if guardian.guardian_relationship and 'primary' in guardian.guardian_relationship.lower():
                return guardian

        # Default to first guardian if no primary found
        return guardians[0]