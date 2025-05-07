from app.services.crud_service import CrudService
from app.models.student_models import Course
from typing import Dict, List, Any, Tuple, Union


class CourseService(CrudService):
    """CRUD operations for Course table"""

    def __init__(self):
        super().__init__(Course)

    def create_course(self, course_data: Dict[str, Any]) -> Tuple[bool, Union[Course, str]]:
        """
        Create a new course with validation

        Args:
            course_data: Dictionary with course fields

        Returns:
            Tuple of (success, course object or error message)
        """
        # Perform validations
        if 'course_name' not in course_data or not course_data['course_name']:
            return False, "Course name is required"

        # Use the generic create method
        return self.create(course_data)

    def get_all_courses(self) -> List[Course]:
        """
        Get all courses

        Returns:
            List of all courses
        """
        return self.read_all()