from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any, Type, Optional, Union, Tuple
from app.database.db_connection import DataDatabase
from app.utils.logger import Logger


class CrudService:
    """
    Base service for CRUD operations.
    Each table-specific service will inherit from this base class.
    """

    def __init__(self, model_class=None):
        """
        Initialize with model class and create database session

        Args:
            model_class: SQLAlchemy model class for the table
        """
        self.model_class = model_class
        self.db = DataDatabase()
        self.logger = Logger()

    def create(self, data: Dict[str, Any]) -> Tuple[bool, Union[object, str]]:
        """
        Create a new record

        Args:
            data: Dictionary of field:value pairs

        Returns:
            Tuple of (success, object or error message)
        """
        db_session = self.db.get_session()
        try:
            # Create new instance of model
            new_record = self.model_class()

            # Get primary key columns of the model
            primary_key_cols = []
            for column in new_record.__table__.primary_key:
                primary_key_cols.append(column.name)

            # Set attributes from data dictionary, excluding primary keys with autoincrement
            for field, value in data.items():
                # Skip primary key fields (let the database assign them)
                if field in primary_key_cols:
                    continue

                if hasattr(new_record, field):
                    setattr(new_record, field, value)

            # Add and commit
            db_session.add(new_record)
            db_session.commit()

            # Create a fresh copy of the object's data
            result = self.model_class()
            for column in new_record.__table__.columns:
                setattr(result, column.name, getattr(new_record, column.name))

            # Return the detached copy
            return True, result

        except SQLAlchemyError as e:
            db_session.rollback()
            error_msg = f"Database error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            db_session.rollback()
            error_msg = f"Error creating record: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        finally:
            db_session.close()

    def read(self, record_id: int) -> Optional[object]:
        """
        Get a single record by ID

        Args:
            record_id: Primary key ID of the record

        Returns:
            Model instance or None if not found
        """
        db_session = self.db.get_session()
        try:
            record = db_session.query(self.model_class).get(record_id)

            if not record:
                return None

            # Create a copy of the record data to return
            result = self.model_class()
            for column in record.__table__.columns:
                setattr(result, column.name, getattr(record, column.name))

            return result
        except Exception as e:
            self.logger.error(f"Error reading record #{record_id}: {str(e)}")
            return None
        finally:
            db_session.close()

    def read_all(self, filters: Dict[str, Any] = None) -> List[object]:
        """
        Get all records, optionally filtered

        Args:
            filters: Dictionary of field:value pairs to filter by

        Returns:
            List of model instances
        """
        db_session = self.db.get_session()
        try:
            query = db_session.query(self.model_class)

            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        query = query.filter(getattr(self.model_class, field) == value)

            # Execute query
            records = query.all()

            # Create copies of the records to return
            results = []
            for record in records:
                result = self.model_class()
                for column in record.__table__.columns:
                    setattr(result, column.name, getattr(record, column.name))
                results.append(result)

            return results
        except Exception as e:
            self.logger.error(f"Error reading records: {str(e)}")
            return []
        finally:
            db_session.close()

    def update(self, record_id: int, data: Dict[str, Any]) -> Tuple[bool, Union[object, str]]:
        """
        Update an existing record

        Args:
            record_id: Primary key ID of the record to update
            data: Dictionary of field:value pairs to update

        Returns:
            Tuple of (success, updated object or error message)
        """
        db_session = self.db.get_session()
        try:
            # Find the record
            record = db_session.query(self.model_class).get(record_id)
            if not record:
                return False, f"Record with ID {record_id} not found"

            # Update fields
            for field, value in data.items():
                if hasattr(record, field):
                    setattr(record, field, value)

            # Commit changes
            db_session.commit()

            # Create a copy of the updated record to return
            result = self.model_class()
            for column in record.__table__.columns:
                setattr(result, column.name, getattr(record, column.name))

            return True, result
        except SQLAlchemyError as e:
            db_session.rollback()
            error_msg = f"Database error updating record #{record_id}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            db_session.rollback()
            error_msg = f"Error updating record #{record_id}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        finally:
            db_session.close()

    def delete(self, record_id: int) -> Tuple[bool, str]:
        """
        Delete a record

        Args:
            record_id: Primary key ID of the record to delete

        Returns:
            Tuple of (success, message)
        """
        db_session = self.db.get_session()
        try:
            # Find the record
            record = db_session.query(self.model_class).get(record_id)
            if not record:
                return False, f"Record with ID {record_id} not found"

            # Delete record
            db_session.delete(record)
            db_session.commit()

            return True, f"Record #{record_id} deleted successfully"
        except SQLAlchemyError as e:
            db_session.rollback()
            error_msg = f"Database error deleting record #{record_id}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            db_session.rollback()
            error_msg = f"Error deleting record #{record_id}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        finally:
            db_session.close()

    def exists(self, record_id: int) -> bool:
        """
        Check if a record exists

        Args:
            record_id: Primary key ID to check

        Returns:
            True if exists, False otherwise
        """
        db_session = self.db.get_session()
        try:
            exists = db_session.query(db_session.query(self.model_class).filter_by(
                id=record_id).exists()).scalar()
            return exists
        except Exception as e:
            self.logger.error(f"Error checking record existence #{record_id}: {str(e)}")
            return False
        finally:
            db_session.close()