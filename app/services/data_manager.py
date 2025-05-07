from app.services.data_filter_service import DataFilterService
from app.models.student_models import *
from sqlalchemy import func, and_, or_
import datetime


class DataManager:
    """
    Service for managing data operations across tables
    Handles CRUD operations with specialized filtering
    """

    def __init__(self, db_session):
        self.db_session = db_session
        self.filter_service = DataFilterService(db_session)

        # Map table names to model classes
        self.model_map = {
            'students_personal': Student,
            'education_history': EducationHistory,
            'courses': Course,
            'enrollments': Enrollment,
            'hostel_management': HostelManagement,
            'medical_history': MedicalHistory,
            'student_guardians': StudentGuardian,
            'transportation': Transportation,
            'admin': Admin,
            'action': Action
        }

        # Define searchable fields for each table
        self.searchable_fields = {
            'students_personal': ['student_name', 'cnic', 'phone', 'address', 'student_occupation'],
            'education_history': ['education_level'],
            'courses': ['course_name'],
            'hostel_management': ['special_requirements'],
            'medical_history': ['name_of_disability', 'brief_medical_history', 'regular_medication',
                                'communicable_disease', 'assistive_device_used'],
            'student_guardians': ['guardian_name', 'guardian_relationship', 'guardian_contact_number'],
            'transportation': ['pickup_drop_responsible_name', 'pickup_drop_contact_number'],
            'admins': ['admin_name'],
            'admin': ['table_name', 'description']
        }

        # Define date fields for each table
        self.date_fields = {
            'students_personal': ['date_of_birth', 'admission_date'],
            'enrollments': ['date_of_enrollment'],
            'admin': ['action_time']
        }

        # Define boolean fields for each table
        self.boolean_fields = {
            'students_personal': ['accompanied_by_assistant', 'affidavit_attached'],
            'education_history': ['certificate_attached'],
            'enrollments': ['completion_status'],
            'medical_history': ['epilepsy', 'drug_addiction_smoking']
        }

    def get_model_class(self, table_name):
        """Get SQLAlchemy model class for table name"""
        return self.model_map.get(table_name)

    def get_filtered_data(self, table_name, **filter_args):
        """
        Get filtered data for a specific table

        Args:
            table_name: Name of the table to query
            filter_args: Keyword arguments for filtering (see DataFilterService.apply_filters)

        Returns:
            Tuple of (data_list, total_count)
        """
        model_class = self.get_model_class(table_name)
        if not model_class:
            return [], 0

        # If search fields not specified, use predefined searchable fields
        if 'search_term' in filter_args and 'search_fields' not in filter_args:
            filter_args['search_fields'] = self.searchable_fields.get(table_name, [])

        return self.filter_service.apply_filters(model_class, **filter_args)

    def get_student_with_related(self, student_id):
        """
        Get a student record with all related data

        Args:
            student_id: ID of the student

        Returns:
            Dict with student data and related records
        """
        student = self.db_session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return None

        # Convert SQLAlchemy model to dict
        result = self._model_to_dict(student)

        # Add related data
        result['education'] = [self._model_to_dict(edu) for edu in student.education_history]
        result['enrollments'] = []
        for enr in student.enrollments:
            enr_dict = self._model_to_dict(enr)
            enr_dict['course_name'] = enr.course.course_name if enr.course else None
            result['enrollments'].append(enr_dict)

        result['hostel'] = [self._model_to_dict(h) for h in student.hostel_info]
        result['medical'] = [self._model_to_dict(med) for med in student.medical_history]
        result['guardians'] = [self._model_to_dict(g) for g in student.guardians]
        result['transportation'] = [self._model_to_dict(t) for t in student.transportation]

        return result

    def get_table_stats(self, table_name):
        """Get statistics for a table"""
        model_class = self.get_model_class(table_name)
        if not model_class:
            return None

        return self.filter_service.get_table_stats(model_class)

    def get_filter_options(self, table_name):
        """
        Get filtering options for a specific table

        Returns:
            Dict with filter options configuration
        """
        model_class = self.get_model_class(table_name)
        if not model_class:
            return {}

        # Get column information
        columns = []
        primary_key = None
        for column in model_class.__table__.columns:
            col_info = {
                'name': column.name,
                'type': str(column.type),
                'is_primary': column.primary_key,
                'is_nullable': column.nullable,
                'is_foreign_key': bool(column.foreign_keys)
            }

            # Identify primary key column
            if column.primary_key:
                primary_key = column.name

            columns.append(col_info)

        # Get related models for joins
        related_models = []
        for relationship_name in getattr(model_class, '__mapper__').relationships.keys():
            related_models.append(relationship_name)

        # Get applicable filter types
        filter_config = {
            'sortable_fields': [col['name'] for col in columns],
            'searchable_fields': self.searchable_fields.get(table_name, []),
            'date_fields': self.date_fields.get(table_name, []),
            'boolean_fields': self.boolean_fields.get(table_name, []),
            'primary_key': primary_key,
            'columns': columns,
            'related_models': related_models
        }

        return filter_config

    def _model_to_dict(self, model):
        """Convert SQLAlchemy model to dictionary"""
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