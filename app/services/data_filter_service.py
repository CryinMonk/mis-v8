from typing import Dict, List, Any, Tuple, Optional, Union
from sqlalchemy import desc, asc, and_, or_, not_, func, text
from sqlalchemy.orm import Query
import datetime


class DataFilterService:
    """
    Service for handling advanced data filtering operations
    Provides methods to filter and sort data in database tables
    """

    def __init__(self, db_session):
        self.db_session = db_session

    def apply_filters(self, model_class, filters=None, sort_by=None, sort_order='asc',
                      page=1, per_page=50, search_term=None, search_fields=None,
                      date_range=None, boolean_filters=None, custom_filters=None):
        """
        Apply filters, sorting, and pagination to a query for any model

        Args:
            model_class: SQLAlchemy model class to query
            filters: Dict of field:value pairs for exact matches
            sort_by: Field to sort by
            sort_order: 'asc' or 'desc'
            page: Page number (for pagination)
            per_page: Items per page
            search_term: Text to search for across search_fields
            search_fields: List of fields to search with search_term
            date_range: Dict of date field and min/max values
            boolean_filters: Dict of boolean field:value pairs
            custom_filters: List of custom SQLAlchemy filter expressions

        Returns:
            Tuple of (data, total_count)
        """
        # Start with base query
        query = self.db_session.query(model_class)

        # Apply exact match filters
        if filters:
            filter_conditions = []
            for field_name, value in filters.items():
                if hasattr(model_class, field_name):
                    field = getattr(model_class, field_name)
                    filter_conditions.append(field == value)
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))

        # Apply search term across multiple fields
        if search_term and search_fields:
            search_conditions = []
            for field_name in search_fields:
                if hasattr(model_class, field_name):
                    field = getattr(model_class, field_name)
                    search_conditions.append(field.ilike(f"%{search_term}%"))
            if search_conditions:
                query = query.filter(or_(*search_conditions))

        # Apply date range filters
        if date_range:
            for field_name, range_values in date_range.items():
                if hasattr(model_class, field_name):
                    field = getattr(model_class, field_name)

                    # Apply minimum date if specified
                    if 'min' in range_values and range_values['min']:
                        min_date = self._parse_date(range_values['min'])
                        if min_date:
                            query = query.filter(field >= min_date)

                    # Apply maximum date if specified
                    if 'max' in range_values and range_values['max']:
                        max_date = self._parse_date(range_values['max'])
                        if max_date:
                            query = query.filter(field <= max_date)

        # Apply boolean filters
        if boolean_filters:
            for field_name, value in boolean_filters.items():
                if hasattr(model_class, field_name):
                    field = getattr(model_class, field_name)
                    # Handle different representations of boolean values
                    if value in [True, 'True', 'true', 1, '1']:
                        query = query.filter(field == True)
                    elif value in [False, 'False', 'false', 0, '0']:
                        query = query.filter(field == False)

        # Apply any custom filters
        if custom_filters:
            for filter_expr in custom_filters:
                query = query.filter(filter_expr)

        # Get total count before pagination
        total_count = query.count()

        # Apply sorting
        if sort_by and hasattr(model_class, sort_by):
            sort_field = getattr(model_class, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(asc(sort_field))

        # Apply pagination
        if page and per_page:
            query = query.limit(per_page).offset((page - 1) * per_page)

        # Execute query and return results
        return query.all(), total_count

    def get_distinct_values(self, model_class, field_name, filters=None):
        """
        Get distinct values for a specific field, useful for dropdown filters

        Args:
            model_class: SQLAlchemy model class
            field_name: Field to get distinct values for
            filters: Optional filters to apply before getting distinct values

        Returns:
            List of distinct values
        """
        if not hasattr(model_class, field_name):
            return []

        field = getattr(model_class, field_name)
        query = self.db_session.query(field).distinct()

        # Apply filters if provided
        if filters:
            filter_conditions = []
            for f_name, value in filters.items():
                if hasattr(model_class, f_name):
                    f = getattr(model_class, f_name)
                    filter_conditions.append(f == value)
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))

        # Execute and extract values
        result = query.all()
        return [r[0] for r in result if r[0] is not None]

    def _parse_date(self, date_str):
        """Helper method to parse date strings"""
        if isinstance(date_str, (datetime.date, datetime.datetime)):
            return date_str

        # Try different date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except (ValueError, TypeError):
                continue

        return None

    def get_table_stats(self, model_class):
        """
        Get basic statistics for a table - counts, date ranges, etc.
        Useful for informing filter UI components

        Args:
            model_class: SQLAlchemy model class

        Returns:
            Dict with table statistics
        """
        stats = {
            'total_records': self.db_session.query(model_class).count(),
            'fields': {}
        }

        # Get column info from SQLAlchemy model
        for column in model_class.__table__.columns:
            field_name = column.name
            field_type = str(column.type)

            # Get specific stats based on field type
            if 'date' in field_type.lower():
                min_date = self.db_session.query(func.min(getattr(model_class, field_name))).scalar()
                max_date = self.db_session.query(func.max(getattr(model_class, field_name))).scalar()
                stats['fields'][field_name] = {
                    'type': 'date',
                    'min': min_date,
                    'max': max_date
                }
            elif field_type.lower() in ('boolean', 'tinyint(1)'):
                true_count = self.db_session.query(model_class).filter(getattr(model_class, field_name) == True).count()
                false_count = self.db_session.query(model_class).filter(
                    getattr(model_class, field_name) == False).count()
                stats['fields'][field_name] = {
                    'type': 'boolean',
                    'true_count': true_count,
                    'false_count': false_count
                }
            elif 'int' in field_type.lower():
                min_val = self.db_session.query(func.min(getattr(model_class, field_name))).scalar()
                max_val = self.db_session.query(func.max(getattr(model_class, field_name))).scalar()
                stats['fields'][field_name] = {
                    'type': 'numeric',
                    'min': min_val,
                    'max': max_val
                }
            elif 'varchar' in field_type.lower() or 'text' in field_type.lower():
                distinct_count = self.db_session.query(
                    func.count(func.distinct(getattr(model_class, field_name)))).scalar()
                stats['fields'][field_name] = {
                    'type': 'text',
                    'distinct_count': distinct_count
                }

        return stats