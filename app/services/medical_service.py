from app.services.crud_service import CrudService
from app.models.student_models import MedicalHistory
from typing import Dict, List, Any, Tuple, Optional, Union


class MedicalService(CrudService):
    """CRUD operations for Medical History table"""

    def __init__(self):
        super().__init__(MedicalHistory)

    def create_medical_record(self, medical_data: Dict[str, Any]) -> Tuple[bool, Union[MedicalHistory, str]]:
        """
        Create a new medical history record with validation

        Args:
            medical_data: Dictionary with medical fields

        Returns:
            Tuple of (success, medical object or error message)
        """
        # Perform validations
        if 'student_id' not in medical_data:
            return False, "Student ID is required"

        # Use the generic create method
        return self.create(medical_data)

    def get_by_student(self, student_id: int) -> Optional[MedicalHistory]:
        """
        Get medical history for a student

        Args:
            student_id: ID of the student

        Returns:
            Medical history record or None if not found
        """
        records = self.read_all(filters={'student_id': student_id})
        return records[0] if records else None

    def get_all_by_student(self, student_id: int) -> List[MedicalHistory]:
        """
        Get all medical history records for a student

        Args:
            student_id: ID of the student

        Returns:
            List of medical history records
        """
        return self.read_all(filters={'student_id': student_id})

    def search(self, search_term: str) -> List[MedicalHistory]:
        """
        Search for medical records based on a search term

        Args:
            search_term: Text to search for in medical records

        Returns:
            List of matching medical records
        """
        search_term = search_term.lower().strip()

        # If search term is empty, return all records
        if not search_term:
            return self.read_all()

        # If search term is a number, it might be a student ID
        if search_term.isdigit():
            # Try to find by student ID
            student_id = int(search_term)
            medical_record = self.get_by_student(student_id)

            return [medical_record] if medical_record else []

        # Check for epilepsy-related searches
        if search_term in ['epilepsy', 'epileptic', 'yes']:
            return self.search_by_condition('epilepsy', True)

        # Check for non-epilepsy searches
        if search_term in ['no epilepsy', 'not epileptic', 'no']:
            return self.search_by_condition('epilepsy', False)

        # Check for addiction-related searches
        if any(term in search_term for term in ['addiction', 'drug', 'smoking']):
            return self.search_by_condition('drug_addiction_smoking', True)

        # Perform a general search across all medical records
        all_records = self.read_all()
        results = []

        for record in all_records:
            # Search in disability name
            if record.name_of_disability and search_term in record.name_of_disability.lower():
                results.append(record)
                continue

            # Search in additional information if it exists
            if hasattr(record, 'additional_information') and record.additional_information:
                if search_term in record.additional_information.lower():
                    results.append(record)
                    continue

            # Search in medical history if it exists
            if hasattr(record, 'medical_history_details') and record.medical_history_details:
                if search_term in record.medical_history_details.lower():
                    results.append(record)
                    continue

            # Search in medication if it exists
            if hasattr(record, 'medication') and record.medication:
                if search_term in record.medication.lower():
                    results.append(record)
                    continue

        return results

    def advanced_search(self, search_term: str) -> Tuple[List[MedicalHistory], Dict[int, List[str]]]:
        """
        Advanced search with match reasons

        Args:
            search_term: Text to search for

        Returns:
            Tuple of (matching records, dictionary of medical_id to list of match reasons)
        """
        search_term = search_term.lower().strip()
        all_records = self.read_all()
        results = []
        match_reasons = {}  # Dictionary to store match reasons

        for record in all_records:
            record_id = record.medical_id
            reasons = []

            # Check student ID
            if search_term.isdigit() and int(search_term) == record.student_id:
                results.append(record)
                reasons.append('Student ID')

            # Check for epilepsy
            if search_term in ['epilepsy', 'epileptic', 'yes']:
                if record.epilepsy:
                    if record not in results:
                        results.append(record)
                    reasons.append('Epilepsy')

            # Check for non-epilepsy
            if search_term in ['no epilepsy', 'not epileptic', 'no']:
                if not record.epilepsy:
                    if record not in results:
                        results.append(record)
                    reasons.append('No Epilepsy')

            # Check for addiction
            if any(term in search_term for term in ['addiction', 'drug', 'smoking']):
                if record.drug_addiction_smoking:
                    if record not in results:
                        results.append(record)
                    reasons.append('Drug Addiction/Smoking')

            # Check disability name
            if record.name_of_disability and search_term in record.name_of_disability.lower():
                if record not in results:
                    results.append(record)
                reasons.append('Disability Name')

            # Check additional information
            if hasattr(record, 'additional_information') and record.additional_information:
                if search_term in record.additional_information.lower():
                    if record not in results:
                        results.append(record)
                    reasons.append('Additional Information')

            # Check medical history details
            if hasattr(record, 'medical_history_details') and record.medical_history_details:
                if search_term in record.medical_history_details.lower():
                    if record not in results:
                        results.append(record)
                    reasons.append('Medical History Details')

            # Check medication
            if hasattr(record, 'medication') and record.medication:
                if search_term in record.medication.lower():
                    if record not in results:
                        results.append(record)
                    reasons.append('Medication')

            # Store match reasons if any were found
            if reasons:
                match_reasons[record_id] = reasons

        return results, match_reasons

    def search_by_condition(self, condition_field: str, is_positive: bool) -> List[MedicalHistory]:
        """
        Search medical records by a specific condition field

        Args:
            condition_field: Field name to check (e.g., 'epilepsy', 'drug_addiction_smoking')
            is_positive: True to find records with condition, False for without

        Returns:
            List of matching medical records
        """
        all_records = self.read_all()
        results = []

        for record in all_records:
            if hasattr(record, condition_field):
                field_value = getattr(record, condition_field)
                if bool(field_value) == is_positive:
                    results.append(record)

        return results

    def search_by_disability(self, disability_name: str) -> List[MedicalHistory]:
        """
        Search medical records by disability name

        Args:
            disability_name: Name of disability to search for

        Returns:
            List of matching medical records
        """
        disability_name = disability_name.lower().strip()
        all_records = self.read_all()
        results = []

        for record in all_records:
            if record.name_of_disability and disability_name in record.name_of_disability.lower():
                results.append(record)

        return results

    def get_medical_summary(self, student_id: int) -> Dict[str, Any]:
        """
        Get a summary of a student's medical information

        Args:
            student_id: ID of the student

        Returns:
            Dictionary with medical summary information
        """
        record = self.get_by_student(student_id)

        if not record:
            return {
                'student_id': student_id,
                'has_medical_record': False,
                'has_disability': False,
                'has_epilepsy': False,
                'has_addiction': False
            }

        return {
            'student_id': student_id,
            'has_medical_record': True,
            'has_disability': bool(record.name_of_disability),
            'disability_name': record.name_of_disability,
            'has_epilepsy': record.epilepsy,
            'has_addiction': record.drug_addiction_smoking,
            'additional_information': getattr(record, 'additional_information', None),
        }

    def get_students_with_special_needs(self) -> List[MedicalHistory]:
        """
        Get all students with special medical needs

        Returns:
            List of medical records for students with disabilities or conditions
        """
        all_records = self.read_all()
        results = []

        for record in all_records:
            # Check if has a disability
            if record.name_of_disability:
                results.append(record)
                continue

            # Check if has epilepsy
            if record.epilepsy:
                results.append(record)
                continue

            # Check if has addiction
            if record.drug_addiction_smoking:
                results.append(record)
                continue

        return results