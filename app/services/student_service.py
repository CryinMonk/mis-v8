from app.services.crud_service import CrudService
from app.models.student_models import (
    Student,
    StudentGuardian,
    EducationHistory,  # Add this import
    Enrollment,        # Add this import
    Course,            # Add this import
    MedicalHistory,    # Add this import
    HostelManagement,  # Add this import
    Transportation     # Add this import
)
from typing import Dict, List, Any, Tuple, Optional, Union
import datetime
# import logging  # Add this for logger
from sqlalchemy import or_
# from sqlalchemy.orm import joinedload


class StudentService(CrudService):
    """CRUD operations for Student table"""

    def __init__(self):
        super().__init__(Student)

    def create_student(self, student_data: Dict[str, Any]) -> Tuple[bool, Union[Student, str]]:
        """
        Create a new student record with validation

        Args:
            student_data: Dictionary with student fields

        Returns:
            Tuple of (success, student object or error message)
        """
        # Perform validations
        if 'student_name' not in student_data or not student_data['student_name']:
            return False, "Student name is required"

        # Format date fields if provided as strings
        if 'date_of_birth' in student_data and isinstance(student_data['date_of_birth'], str):
            try:
                student_data['date_of_birth'] = datetime.datetime.strptime(
                    student_data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return False, "Invalid date format for date_of_birth. Use YYYY-MM-DD."

        if 'admission_date' in student_data and isinstance(student_data['admission_date'], str):
            try:
                student_data['admission_date'] = datetime.datetime.strptime(
                    student_data['admission_date'], '%Y-%m-%d').date()
            except ValueError:
                return False, "Invalid date format for admission_date. Use YYYY-MM-DD."

        # Use the generic create method
        return self.create(student_data)

    def get_student_with_details(self, student_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a student with related records

        Args:
            student_id: ID of the student

        Returns:
            Dictionary with student and related data or None
        """
        db_session = self.db.get_session()
        try:
            # First try to get the base student record
            student = db_session.query(Student).get(student_id)

            if not student:
                self.logger.error(f"Student with ID {student_id} not found")
                return None

            # Create a dictionary copy of the student data
            result = {}
            for column in student.__table__.columns:
                value = getattr(student, column.name)
                # Convert dates to string for easier handling
                if isinstance(value, (datetime.date, datetime.datetime)):
                    value = value.strftime('%Y-%m-%d')
                result[column.name] = value

            # Fetch related data with separate queries to avoid session issues

            # Education History
            education_history = db_session.query(EducationHistory).filter(
                EducationHistory.student_id == student_id
            ).all()
            result['education_history'] = []
            for edu in education_history:
                edu_dict = {}
                for column in edu.__table__.columns:
                    value = getattr(edu, column.name)
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        value = value.strftime('%Y-%m-%d')
                    edu_dict[column.name] = value
                result['education_history'].append(edu_dict)

            # Enrollments - with course names
            enrollments = db_session.query(Enrollment).filter(
                Enrollment.student_id == student_id
            ).all()
            result['enrollments'] = []
            for enr in enrollments:
                enr_dict = {}
                for column in enr.__table__.columns:
                    value = getattr(enr, column.name)
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        value = value.strftime('%Y-%m-%d')
                    enr_dict[column.name] = value

                # Get course name if available
                if hasattr(enr, 'course_id') and enr.course_id:
                    course = db_session.query(Course).get(enr.course_id)
                    if course:
                        enr_dict['course_name'] = course.course_name
                    else:
                        enr_dict['course_name'] = f"Unknown Course"
                else:
                    enr_dict['course_name'] = "No course assigned"

                result['enrollments'].append(enr_dict)

            # Medical History
            medical_history = db_session.query(MedicalHistory).filter(
                MedicalHistory.student_id == student_id
            ).all()
            result['medical_history'] = []
            for med in medical_history:
                med_dict = {}
                for column in med.__table__.columns:
                    value = getattr(med, column.name)
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        value = value.strftime('%Y-%m-%d')
                    med_dict[column.name] = value
                result['medical_history'].append(med_dict)

            # Guardians
            guardians = db_session.query(StudentGuardian).filter(
                StudentGuardian.student_id == student_id
            ).all()
            result['guardians'] = []
            for guard in guardians:
                guard_dict = {}
                for column in guard.__table__.columns:
                    value = getattr(guard, column.name)
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        value = value.strftime('%Y-%m-%d')
                    guard_dict[column.name] = value
                result['guardians'].append(guard_dict)

            # Hostel information
            hostel_info = db_session.query(HostelManagement).filter(
                HostelManagement.student_id == student_id
            ).all()
            result['hostel_info'] = []
            for host in hostel_info:
                host_dict = {}
                for column in host.__table__.columns:
                    value = getattr(host, column.name)
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        value = value.strftime('%Y-%m-%d')
                    host_dict[column.name] = value
                result['hostel_info'].append(host_dict)

            # Transportation
            transportation = db_session.query(Transportation).filter(
                Transportation.student_id == student_id
            ).all()
            result['transportation'] = []
            for trans in transportation:
                trans_dict = {}
                for column in trans.__table__.columns:
                    value = getattr(trans, column.name)
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        value = value.strftime('%Y-%m-%d')
                    trans_dict[column.name] = value
                result['transportation'].append(trans_dict)

            return result

        except Exception as e:
            self.logger.error(f"Error getting student with details #{student_id}: {str(e)}")
            return None
        finally:
            db_session.close()

    def advanced_search(self, search_term: str) -> Tuple[List[Student], Dict[int, List[str]]]:
        """
        Search for students by multiple fields including guardian information

        Args:
            search_term: Term to search for

        Returns:
            Tuple of (list of matching students, dict of student_id: match_reasons)
        """
        db_session = self.db.get_session()
        try:
            # Try to parse student_id if the search term is a number
            student_id = None
            if search_term.isdigit():
                student_id = int(search_term)

            # Keep track of why each student matched
            match_reasons = {}

            # Query students directly first
            direct_students = []

            # Check each field individually to track match reasons
            name_matches = db_session.query(Student).filter(
                Student.student_name.ilike(f'%{search_term}%')
            ).all()
            for student in name_matches:
                if student.student_id not in match_reasons:
                    match_reasons[student.student_id] = []
                match_reasons[student.student_id].append('Name')
                direct_students.append(student)

            cnic_matches = db_session.query(Student).filter(
                Student.cnic.ilike(f'%{search_term}%')
            ).all()
            for student in cnic_matches:
                if student.student_id not in match_reasons:
                    match_reasons[student.student_id] = []
                match_reasons[student.student_id].append('CNIC')
                if student not in direct_students:
                    direct_students.append(student)

            phone_matches = db_session.query(Student).filter(
                or_(
                    Student.phone.ilike(f'%{search_term}%'),
                    Student.student_contact_no.ilike(f'%{search_term}%')
                )
            ).all()
            for student in phone_matches:
                if student.student_id not in match_reasons:
                    match_reasons[student.student_id] = []
                match_reasons[student.student_id].append('Phone')
                if student not in direct_students:
                    direct_students.append(student)

            address_matches = db_session.query(Student).filter(
                Student.address.ilike(f'%{search_term}%')
            ).all()
            for student in address_matches:
                if student.student_id not in match_reasons:
                    match_reasons[student.student_id] = []
                match_reasons[student.student_id].append('Address')
                if student not in direct_students:
                    direct_students.append(student)

            # If search term is a number, also search by student_id
            if student_id:
                id_student = db_session.query(Student).filter(
                    Student.student_id == student_id
                ).first()
                if id_student:
                    if id_student.student_id not in match_reasons:
                        match_reasons[id_student.student_id] = []
                    match_reasons[id_student.student_id].append('Student ID')
                    if id_student not in direct_students:
                        direct_students.append(id_student)

            # Search in guardian data
            guardian_results = db_session.query(
                StudentGuardian, Student
            ).join(
                Student, StudentGuardian.student_id == Student.student_id
            ).filter(
                or_(
                    StudentGuardian.guardian_name.ilike(f'%{search_term}%'),
                    StudentGuardian.guardian_contact_number.ilike(f'%{search_term}%')
                )
            ).all()

            # Process guardian matches
            for guardian, student in guardian_results:
                if student.student_id not in match_reasons:
                    match_reasons[student.student_id] = []

                if search_term.lower() in guardian.guardian_name.lower():
                    match_reasons[student.student_id].append('Guardian Name')

                if guardian.guardian_contact_number and search_term.lower() in guardian.guardian_contact_number.lower():
                    match_reasons[student.student_id].append('Guardian Contact')

                if student not in direct_students:
                    direct_students.append(student)

            # Convert direct_students to a list of detached dictionaries
            result_students = []
            for student in direct_students:
                # Create a fresh copy of the student data
                student_copy = Student()
                for column in student.__table__.columns:
                    setattr(student_copy, column.name, getattr(student, column.name))
                result_students.append(student_copy)

            return result_students, match_reasons

        except Exception as e:
            self.logger.error(f"Error in advanced search: {str(e)}")
            return [], {}
        finally:
            db_session.close()

    def _model_to_dict(self, model):
        """Helper method to convert SQLAlchemy model to dict"""
        if not model:
            return None

        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            # Convert dates to string for easier handling
            if isinstance(value, (datetime.date, datetime.datetime)):
                value = value.isoformat()
            result[column.name] = value

        return result