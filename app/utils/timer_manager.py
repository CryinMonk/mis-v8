# app/utils/timer_manager.py
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from app.utils.logger import Logger  # Import your logger class


class TimerManager(QObject):
    """Centralized timer manager for the entire application"""

    # Define signals for different refresh events
    dashboard_refresh_signal = pyqtSignal()
    student_data_refresh_signal = pyqtSignal()
    datetime_update_signal = pyqtSignal()

    # Singleton instance
    _instance = None

    @classmethod
    def instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = TimerManager()
        return cls._instance

    @classmethod
    def cleanup_instance(cls):
        """Clean up the singleton instance"""
        if cls._instance is not None:
            cls._instance.cleanup()

    def __init__(self):
        """Initialize the timer manager"""
        super().__init__()
        self.logger = Logger()

        # Flag to track if timers are active
        self.active = False

        # Create a single master timer
        self.master_timer = QTimer()
        self.master_timer.timeout.connect(self._handle_timeout)

        # Track time since last refresh for different components
        self.last_refresh = {
            'dashboard': 0,
            'student_data': 0,
            'datetime': 0
        }

        # Set refresh intervals (in milliseconds)
        self.refresh_intervals = {
            'dashboard': 60000,  # Dashboard every 60 seconds
            'student_data': 30000,  # Student data every 30 seconds
            'datetime': 1000  # DateTime every 1 second
        }

        # Counter for master timer ticks (in milliseconds)
        self.tick_count = 0

        self.logger.info("Timer manager initialized")

    def start(self):
        """Start the master timer"""
        if not self.active:
            self.active = True
            self.tick_count = 0
            self.master_timer.start(1000)  # Tick every second (1000ms)
            self.logger.info("Timer manager started")

    def stop(self):
        """Stop the master timer"""
        if self.active:
            self.active = False
            self.master_timer.stop()
            self.logger.info("Timer manager stopped")

    def _handle_timeout(self):
        """Handle timeout from the master timer"""
        if not self.active:
            return

        # Increment tick count by 1 second (1000ms)
        self.tick_count += 1000

        # Check each refresh interval
        for component, interval in self.refresh_intervals.items():
            if self.tick_count % interval == 0:
                if component == 'dashboard':
                    self.dashboard_refresh_signal.emit()
                elif component == 'student_data':
                    self.student_data_refresh_signal.emit()
                elif component == 'datetime':
                    self.datetime_update_signal.emit()

    def cleanup(self):
        """Clean up all timers when application is closing"""
        if self.active:
            self.stop()

        # Disconnect all signals
        try:
            self.master_timer.timeout.disconnect()
        except TypeError:
            pass  # Signal might not be connected

        # Clear all references to signals
        self.dashboard_refresh_signal.disconnect()
        self.student_data_refresh_signal.disconnect()
        self.datetime_update_signal.disconnect()

        # Reset the instance
        TimerManager._instance = None

        self.logger.info("Timer manager cleaned up")