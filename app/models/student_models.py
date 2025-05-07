import enum  # Add this import at the top
from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Student(Base):
    __tablename__ = 'students_personal'

    # Define primary key with autoincrement explicitly set to True
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    student_name = Column(String(100), nullable=False)
    cnic = Column(String(15), nullable=False)
    gender = Column(String(1), nullable=False)
    age = Column(Integer, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(15), nullable=False)
    address = Column(Text, nullable=True)
    student_contact_no = Column(String(15), nullable=True)
    student_occupation = Column(String(100), nullable=True)
    admission_type = Column(String(20), nullable=True)
    admission_date = Column(Date, nullable=True)
    accompanied_by_assistant = Column(Boolean, nullable=True, default=False)
    affidavit_attached = Column(Boolean, nullable=True, default=False)

    # Define relationships
    education_history = relationship("EducationHistory", back_populates="student", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    medical_history = relationship("MedicalHistory", back_populates="student", cascade="all, delete-orphan")
    guardians = relationship("StudentGuardian", back_populates="student", cascade="all, delete-orphan")
    hostel_info = relationship("HostelManagement", back_populates="student", cascade="all, delete-orphan")
    transportation = relationship("Transportation", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.student_id}, name='{self.student_name}')>"


class EducationHistory(Base):
    __tablename__ = 'education_history'

    education_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students_personal.student_id'))
    education_level = Column(String(50))
    certificate_attached = Column(Boolean)

    # Relationships
    student = relationship("Student", back_populates="education_history")


class Course(Base):
    __tablename__ = 'courses'

    course_id = Column(Integer, primary_key=True)
    course_name = Column(String(100),nullable=False)

    # Relationships
    enrollments = relationship("Enrollment", back_populates="course")


class Enrollment(Base):
    __tablename__ = 'enrollments'

    enrollment_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students_personal.student_id'))
    course_id = Column(Integer, ForeignKey('courses.course_id'))
    date_of_enrollment = Column(Date)
    completion_status = Column(Boolean)

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class HostelManagement(Base):
    __tablename__ = 'hostel_management'

    hostel_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students_personal.student_id'))
    duration_of_stay = Column(String(50))
    special_requirements = Column(Text)

    # Relationships
    student = relationship("Student", back_populates="hostel_info")


class MedicalHistory(Base):
    __tablename__ = 'medical_history'

    medical_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students_personal.student_id'))
    name_of_disability = Column(String(100),nullable=False)
    brief_medical_history = Column(Text)
    regular_medication = Column(Text)
    epilepsy = Column(Boolean)
    communicable_disease = Column(Text)
    drug_addiction_smoking = Column(Boolean)
    assistive_device_used = Column(String(100))

    # Relationships
    student = relationship("Student", back_populates="medical_history")


class StudentGuardian(Base):
    __tablename__ = 'student_guardians'

    student_guardian_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students_personal.student_id'))
    guardian_name = Column(String(100),nullable=False)
    guardian_relationship = Column(String(50))
    guardian_contact_number = Column(String(15),nullable=False)

    # Relationships
    student = relationship("Student", back_populates="guardians")


class Transportation(Base):
    __tablename__ = 'transportation'

    transport_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students_personal.student_id'))
    pickup_drop_responsible_name = Column(String(100))
    pickup_drop_contact_number = Column(String(15),nullable=False)

    # Relationships
    student = relationship("Student", back_populates="transportation")


class ActionType(enum.Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"


class Admin(Base):
    __tablename__ = 'admin'  # Keep the actual table name as 'admin'

    admin_id = Column(Integer, primary_key=True)
    admin_name = Column(String(100))

    # Relationship to the Action class (not AdminAction)
    actions = relationship("Action", back_populates="admin")


class Action(Base):
    __tablename__ = 'actions'

    action_id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('admin.admin_id'))  # Changed to match Admin's table name
    action_type = Column(Enum(ActionType))
    table_name = Column(String(100))
    record_id = Column(Integer)
    description = Column(Text)
    action_time = Column(Date)

    # Relationship back to Admin class
    admin = relationship("Admin", back_populates="actions")