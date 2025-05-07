from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QAction, QMenu,
                             QToolBar, QStatusBar, QMessageBox, QTabWidget, QApplication,
                             QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt5.QtGui import QIcon, QFont

from app.controllers.rbac_controller import RBACController
from app.utils.logger import Logger
from app.ui.dashboard import DashboardWidget
from app.utils.timer_manager import TimerManager

# Import data explorer conditionally to prevent import errors
try:
    from app.ui.data_explorer import DataExplorerWidget

    DATA_EXPLORER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import DataExplorerWidget: {str(e)}")
    DATA_EXPLORER_AVAILABLE = False


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user, session):
        super().__init__()
        self.user = user
        self.session = session
        self.rbac = RBACController()
        self.logger = Logger()
        self.closing = False  # Flag to track if window is being closed
        self.data_explorer = None  # Initialize as None to avoid reference errors

        self.setWindowTitle(f"MIS - {self.user.role.value.capitalize()} Dashboard")
        self.showMaximized()  # Adjust size for better viewing

        # Initialize UI before setting up timers and connections
        self.init_ui()

        # Set up timer for updating the date/time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every second
        self.update_datetime()  # Initial update

        # Get the timer manager instance and start it
        self.timer_manager = TimerManager.instance()
        self.timer_manager.start()

        # Connect to timer manager signals
        self.timer_manager.dashboard_refresh_signal.connect(self.safe_refresh_dashboard)
        self.timer_manager.student_data_refresh_signal.connect(self.safe_refresh_student_data)
        self.timer_manager.datetime_update_signal.connect(self.update_datetime)

        self.logger.info("MainWindow constructed and timer manager connected")

    def init_ui(self):
        # Set central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create header
        self.create_header()

        # Create tab widget for different sections
        self.tab_widget = QTabWidget()

        # Create dashboard tab with scrolling support
        dash_scroll_area = QScrollArea()
        dash_scroll_area.setWidgetResizable(True)
        dash_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        dash_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.dashboard = DashboardWidget(self.user, self.session)
        dash_scroll_area.setWidget(self.dashboard)

        # Connect the tab switch signal
        self.dashboard.tab_switch_requested.connect(self.switch_tab)
        self.tab_widget.addTab(dash_scroll_area, "Dashboard")

        # Add data explorer tab with error handling but name it "Student Information"
        if DATA_EXPLORER_AVAILABLE:
            try:
                # Wrap data explorer in scroll area
                student_scroll_area = QScrollArea()
                student_scroll_area.setWidgetResizable(True)
                student_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                student_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

                # Create the data explorer widget - use a safe wrapper
                self.data_explorer = DataExplorerWidget(parent=self, user=self.user)
                student_scroll_area.setWidget(self.data_explorer)

                self.tab_widget.addTab(student_scroll_area, "Student Information")
                self.logger.info("Student Information tab initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Student Information tab: {str(e)}")
                error_widget = QWidget()
                error_layout = QVBoxLayout(error_widget)
                error_layout.addWidget(QLabel(f"Error loading Student Information: {str(e)}"))
                self.tab_widget.addTab(error_widget, "Student Information (Error)")
                self.data_explorer = None  # Ensure it's set to None on error

        # Add Course Management tab with scrolling
        course_scroll_area = QScrollArea()
        course_scroll_area.setWidgetResizable(True)
        course_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        course_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        course_widget = QWidget()
        course_layout = QVBoxLayout(course_widget)

        course_header = QLabel("<h3>Course Management</h3>")
        course_header.setAlignment(Qt.AlignCenter)

        course_description = QLabel("This module allows you to manage courses, curricula, and schedule planning.")
        course_description.setAlignment(Qt.AlignCenter)
        course_description.setWordWrap(True)

        course_layout.addWidget(course_header)
        course_layout.addWidget(course_description)
        course_layout.addWidget(QLabel("Course management functionality will be implemented soon"))
        course_layout.addStretch()

        course_scroll_area.setWidget(course_widget)
        self.tab_widget.addTab(course_scroll_area, "Course Management")

        # Add Reports tab with scrolling
        reports_scroll_area = QScrollArea()
        reports_scroll_area.setWidgetResizable(True)
        reports_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        reports_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        reports_widget = QWidget()
        reports_layout = QVBoxLayout(reports_widget)

        reports_header = QLabel("<h3>Reports</h3>")
        reports_header.setAlignment(Qt.AlignCenter)

        reports_description = QLabel("Generate and view various system reports and analytics.")
        reports_description.setAlignment(Qt.AlignCenter)
        reports_description.setWordWrap(True)

        reports_layout.addWidget(reports_header)
        reports_layout.addWidget(reports_description)
        reports_layout.addWidget(QLabel("Reports functionality will be implemented soon"))
        reports_layout.addStretch()

        reports_scroll_area.setWidget(reports_widget)
        self.tab_widget.addTab(reports_scroll_area, "Reports")

        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)

        # Create status bar with date/time and user info
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Create date time label for status bar
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("margin-right: 10px;")

        # Create user info label for status bar
        self.user_label = QLabel(f"User: {self.user.username} ({self.user.role.value})")

        # Add permanent widgets to status bar
        self.statusBar.addPermanentWidget(self.user_label)
        self.statusBar.addPermanentWidget(self.datetime_label)

        # Show temporary status message
        self.statusBar.showMessage("Ready", 3000)

        # Create menu
        self.create_menu()

        # Connect the tab change signal AFTER all tabs are added
        self.tab_widget.currentChanged.connect(self.on_main_tab_changed)

        # Log window creation
        self.logger.info(f"Main window created for user {self.user.username} with role {self.user.role.value}")

    def on_main_tab_changed(self, index):
        """Handle main tab changes to refresh data"""
        self.logger.info(f"Main tab changed to index {index}")

        try:
            # Only proceed if not closing
            if self.closing:
                return

            # Use QTimer.singleShot for safer refresh operations
            if index == 0 and hasattr(self, 'dashboard'):  # Dashboard tab
                QTimer.singleShot(200, lambda: self.safe_refresh_dashboard())
                self.logger.info("Scheduled refresh for Dashboard tab")

            elif index == 1 and self.data_explorer is not None:  # Student Information tab
                QTimer.singleShot(200, lambda: self.safe_refresh_student_data())
                self.logger.info("Scheduled refresh for Student Information tab")

            # Set a status message
            tab_name = self.tab_widget.tabText(index)
            self.statusBar.showMessage(f"Switched to {tab_name}", 3000)
        except Exception as e:
            self.logger.error(f"Error in tab change handler: {str(e)}")

    def safe_refresh_dashboard(self):
        """Safely refresh dashboard with error handling"""
        try:
            if hasattr(self, 'dashboard') and self.dashboard and not self.closing:
                self.dashboard.refresh()
                self.logger.info("Dashboard refreshed successfully")
        except Exception as e:
            self.logger.error(f"Error refreshing dashboard: {str(e)}")

    def safe_refresh_student_data(self):
        """Safely refresh student data with error handling"""
        try:
            if self.data_explorer and not self.closing:
                self.data_explorer.refresh_current_view()
                self.logger.info("Student data refreshed successfully")
        except Exception as e:
            self.logger.error(f"Error refreshing student data: {str(e)}")

    def switch_tab(self, tab_index):
        """Switch to the requested tab"""
        try:
            if self.closing:
                return

            if 0 <= tab_index < self.tab_widget.count():
                self.tab_widget.setCurrentIndex(tab_index)
                tab_name = self.tab_widget.tabText(tab_index)
                self.logger.info(f"Switched to tab: {tab_name}")
                self.statusBar.showMessage(f"Switched to {tab_name}", 3000)
            else:
                self.logger.warning(f"Invalid tab index requested: {tab_index}")
        except Exception as e:
            self.logger.error(f"Error switching tabs: {str(e)}")

    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Welcome message
        welcome_label = QLabel(f"Welcome, {self.user.username}!")
        welcome_label.setFont(QFont("Arial", 14, QFont.Bold))

        # Role label
        role_label = QLabel(f"Role: {self.user.role.value}")
        role_label.setFont(QFont("Arial", 10))

        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.request_logout)

        # Add to layout
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(role_label)
        header_layout.addWidget(self.logout_button)

        # Add to main layout
        self.main_layout.addWidget(header_widget)

    def create_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        self.logout_action = QAction('&Logout', self)
        self.logout_action.setShortcut('Ctrl+L')
        self.logout_action.triggered.connect(self.request_logout)
        file_menu.addAction(self.logout_action)

        self.exit_action = QAction('&Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(self.request_exit)
        file_menu.addAction(self.exit_action)

        # Data menu
        data_menu = menubar.addMenu('&Data')

        self.refresh_action = QAction('&Refresh Data', self)
        self.refresh_action.setShortcut('F5')
        self.refresh_action.triggered.connect(self.refresh_data)
        data_menu.addAction(self.refresh_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        self.about_action = QAction('&About', self)
        self.about_action.triggered.connect(self.show_about)
        help_menu.addAction(self.about_action)

    def update_datetime(self):
        """Update the date/time display with Pakistan Standard Time in 12-hour format"""
        try:
            # Skip update if we're closing
            if self.closing:
                return

            now = QDateTime.currentDateTimeUtc()

            # Pakistan Time is UTC+5
            pakistan_time = now.addSecs(5 * 60 * 60)
            formatted_time = pakistan_time.toString("yyyy-MM-dd hh:mm:ss AP")  # 12-hour format with AM/PM

            self.datetime_label.setText(
                f"Current Date and Time (Pakistan): {formatted_time}")
        except Exception as e:
            self.logger.error(f"Error updating datetime: {str(e)}")

    def refresh_data(self):
        """Refresh the current data view"""
        try:
            # Skip refresh if closing
            if self.closing:
                return

            current_tab = self.tab_widget.currentIndex()

            if current_tab == 0 and hasattr(self, 'dashboard'):  # Dashboard tab
                self.safe_refresh_dashboard()
                self.statusBar.showMessage("Dashboard data refreshed", 3000)

            elif current_tab == 1 and self.data_explorer is not None:  # Student Information tab
                self.safe_refresh_student_data()
                self.statusBar.showMessage("Student data refreshed", 3000)
            else:
                self.statusBar.showMessage("Refresh not implemented for this tab", 3000)
        except Exception as e:
            self.logger.error(f"Error in refresh_data: {str(e)}")
            self.statusBar.showMessage(f"Error refreshing data: {str(e)}", 5000)

    def disconnect_signals(self):
        """Disconnect signals to prevent memory leaks when hiding the window"""
        try:
            self.logger.info("Starting to disconnect all signals...")

            # Set the closing flag first to prevent any further refreshes
            self.closing = True

            # Helper function to safely disconnect a signal
            def safe_disconnect(signal, slot):
                try:
                    if signal.receivers(slot) > 0:  # Check if actually connected
                        signal.disconnect(slot)
                        return True
                    return False
                except (TypeError, RuntimeError, AttributeError) as e:
                    self.logger.debug(f"Signal disconnection note: {e}")
                    return False

            # Stop and disconnect timer manager connections
            if hasattr(self, 'timer_manager') and self.timer_manager:
                # Disconnect our own slots from timer manager signals
                safe_disconnect(self.timer_manager.dashboard_refresh_signal, self.safe_refresh_dashboard)
                safe_disconnect(self.timer_manager.student_data_refresh_signal, self.safe_refresh_student_data)
                safe_disconnect(self.timer_manager.datetime_update_signal, self.update_datetime)

                # Stop the timer manager
                self.timer_manager.stop()

                # Clean up the timer manager singleton
                TimerManager.cleanup_instance()
                self.timer_manager = None

                self.logger.info("Timer manager disconnected and stopped")

            # Stop our own timer
            if hasattr(self, 'timer') and self.timer:
                if self.timer.isActive():
                    self.timer.stop()
                safe_disconnect(self.timer.timeout, self.update_datetime)
                self.timer = None
                self.logger.info("Main window timer stopped")

            # Disconnect button signals
            if hasattr(self, 'logout_button'):
                safe_disconnect(self.logout_button.clicked, self.request_logout)

            # Disconnect menu actions
            if hasattr(self, 'logout_action'):
                safe_disconnect(self.logout_action.triggered, self.request_logout)

            if hasattr(self, 'exit_action'):
                safe_disconnect(self.exit_action.triggered, self.request_exit)

            if hasattr(self, 'refresh_action'):
                safe_disconnect(self.refresh_action.triggered, self.refresh_data)

            if hasattr(self, 'about_action'):
                safe_disconnect(self.about_action.triggered, self.show_about)

            # Disconnect dashboard signals
            if hasattr(self, 'dashboard') and self.dashboard:
                safe_disconnect(self.dashboard.tab_switch_requested, self.switch_tab)

                # Explicitly clean up dashboard
                self.dashboard.deleteLater()
                self.dashboard = None
                self.logger.info("Dashboard widget cleaned up")

            # Disconnect tab change signals
            if hasattr(self, 'tab_widget'):
                safe_disconnect(self.tab_widget.currentChanged, self.on_main_tab_changed)

            # Clean up data explorer widget
            if hasattr(self, 'data_explorer') and self.data_explorer:
                self.data_explorer.close()  # This will trigger its closeEvent
                self.data_explorer = None
                self.logger.info("Data explorer widget cleaned up")

            self.logger.info("All signals disconnected and resources cleaned up")
        except Exception as e:
            self.logger.error(f"Error during signal disconnection: {str(e)}")

    def handle_logout_cleanup(self):
        """Handle proper cleanup during logout"""
        self.logger.info("Starting logout cleanup process...")

        # Set closing flag
        self.closing = True

        # First disconnect all signals
        self.disconnect_signals()

        # Hide the window to prevent further UI updates
        self.hide()

        # Now emit the logout signal
        self.logout_requested.emit()

        self.logger.info("Logout cleanup completed")

    def request_logout(self):
        try:
            reply = QMessageBox.question(self, 'Logout Confirmation',
                                         'Are you sure you want to logout?',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.handle_logout_cleanup()
        except Exception as e:
            self.logger.error(f"Error in logout request: {str(e)}")

    def request_exit(self):
        try:
            reply = QMessageBox.question(self, 'Exit Confirmation',
                                         'Are you sure you want to exit the application?',
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.closing = True
                # First do cleanup
                self.disconnect_signals()

                # Then logout if needed
                if hasattr(self, 'session') and self.session:
                    self.logout_requested.emit()

                QApplication.quit()
        except Exception as e:
            self.logger.error(f"Error in exit request: {str(e)}")

    def show_about(self):
        try:
            QMessageBox.about(self, "About Management Information System",
                              "Management Information System v1.0\n\n"
                              "A secure multi-user system built with PyQt5 and SQLAlchemy\n"
                              "© 2025 - All rights reserved")
        except Exception as e:
            self.logger.error(f"Error showing about dialog: {str(e)}")

    def hideEvent(self, event):
        """Handle hide event to cleanup resources if window is being closed"""
        if self.closing:
            self.logger.info("Window is being hidden during closure process")
        super().hideEvent(event)

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            if self.closing:
                # Application is already in the process of closing
                self.logger.info("Window close event received while already closing")
                event.accept()
                return

            # Otherwise, treat this as a logout request
            self.logger.info("Window close event received, triggering logout")
            event.ignore()
            self.request_logout()
        except Exception as e:
            self.logger.error(f"Error in closeEvent: {str(e)}")
            event.accept()  # Accept anyway to prevent being stuck

    #
    # def report(self, event):
    #     try:
    #         if self.closing:
    #             self.logger.info("Window close event received while already closing")
    #             event.accept()
    #             return
    #
    #         self.logger.info("Window close event received, triggering logout")
    #         event.accept()
    #         return
    #
    #         self.logger.info("Window close event received, triggering logout")
    #         event.ignore()
    #         self.request_logout()
    #     except Exception as e:
    #         self.logger.error(f"Error in report event: {str(e)}")
    #         event.accept()
    #
    # def course(self, event):
    #     try:
    #         self.logger.info("Course event received, triggering logout")
    #         event.accept()
    #         return
    #
    #     self.logger.info("Course event received, triggering logout")
    #     event.accept()
    #     return
    #
    #     self.logger.info("Course event received, triggering logout")
    #     event.ignore()
    #     self.request_logout()
