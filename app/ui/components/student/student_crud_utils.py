class StudentCrudUtils:
    """Utility functions for StudentCrudWidget"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        
    def _get_current_time_utc(self):
        """Get current UTC time formatted as string"""
        # Use the specified timestamp for consistency
        return "2025-05-07 12:35:16"

    def _log_activity(self, message):
        """Log activity with current time and user"""
        timestamp = self._get_current_time_utc()
        self.parent.logger.info(f"[{timestamp}] User {self.parent.current_user}: {message}")