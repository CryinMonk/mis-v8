# You can run this diagnostic function to check your database setup by adding this to your main.py:
# from app.database.diagnostics import check_database_tables
# check_database_tables()

import sqlalchemy
from sqlalchemy import inspect
from app.database.db_connection import DataDatabase


def check_database_tables():
    """Verify the database tables and their structure"""
    db = DataDatabase()
    engine = db.engine
    inspector = inspect(engine)

    print("Database Tables Diagnostic:")
    print("--------------------------")

    tables = inspector.get_table_names()
    print(f"Found {len(tables)} tables: {', '.join(tables)}")

    # Check specific tables we need
    required_tables = [
        'students_personal',
        'education_history',
        'student_guardians',
        'medical_history',
        'enrollments',
        'hostel_management',
        'transportation',
        'courses'
    ]

    for table in required_tables:
        if table in tables:
            print(f"✓ Found table: {table}")

            # Check primary key
            pk_columns = inspector.get_pk_constraint(table)
            print(f"  - Primary key: {pk_columns}")

            # Check a few columns
            columns = inspector.get_columns(table)
            print(f"  - Columns: {[col['name'] for col in columns]}")

            # Check for auto-increment on primary key
            for col in columns:
                if col['name'] in pk_columns['constrained_columns']:
                    print(f"  - Is PK autoincrement: {col.get('autoincrement', False)}")
        else:
            print(f"✗ Missing required table: {table}")

    print("\n")

    # Test retrieving a specific student
    try:
        connection = engine.connect()
        result = connection.execute(sqlalchemy.text("SELECT * FROM students_personal LIMIT 1"))
        row = result.fetchone()
        if row:
            print(f"Successfully retrieved student: {dict(row)}")
        else:
            print("No students found in database")
        connection.close()
    except Exception as e:
        print(f"Error accessing database: {str(e)}")