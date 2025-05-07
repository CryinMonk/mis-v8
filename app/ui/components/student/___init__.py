# This file makes the directory a Python package
# Import main widget to make it available directly from package
from app.ui.components.student.student_crud_widget import StudentCrudWidget

__all__ = ['StudentCrudWidget']