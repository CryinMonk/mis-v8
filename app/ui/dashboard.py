import datetime
import traceback

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QFrame, QSizePolicy,
                             QMessageBox, QSpacerItem, QGraphicsDropShadowEffect, QApplication, QGraphicsView)
from PyQt5.QtCore import Qt, QDateTime, QTimeZone, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRect, \
    QMargins, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QGradient, QIcon
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSlice
from app.utils.logger import Logger
from app.database.db_connection import DataDatabase

try:
    from app.models.student_models import Student, Course, Enrollment, HostelManagement
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Failed to import student models: {str(e)}")
    MODELS_AVAILABLE = False

from sqlalchemy import func, desc


class NumberDisplayWidget(QFrame):

    def __init__(self, title, value="0", icon_path=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.title_label = QLabel(title.upper())
        self.title_label.setStyleSheet("color: #616161; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")
        header_layout.addWidget(self.title_label, 1)

        if icon_path:
            try:
                icon_label = QLabel()
                icon_label.setPixmap(QIcon(icon_path).pixmap(20, 20))
                icon_label.setAlignment(Qt.AlignRight)
                header_layout.addWidget(icon_label)
            except Exception as e:
                print(f"Failed to load icon {icon_path}: {str(e)}")

        layout.addLayout(header_layout)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #1976D2; font-size: 36px; font-weight: 500;")
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(self.value_label)
        layout.addStretch()

    def set_value(self, value):
        self.value_label.setText(str(value))

    def set_color(self, color):
        self.value_label.setStyleSheet(f"color: {color}; font-size: 36px; font-weight: 500;")


class DashboardWidget(QWidget):

    tab_switch_requested = pyqtSignal(int)

    def __init__(self, user, session=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.session = session
        self.logger = Logger()
        self.first_load = True
        self.animation_played = False

        self.current_date_time_str = "2025-04-27 10:42:49"
        self.current_user_str = "CryinMonk"

        self._opacity = 1.0

        self.db_session = None
        try:
            self.db = DataDatabase()
            self.db_session = self.db.get_session()
            self.logger.info("Dashboard database connection established successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database connection for dashboard: {str(e)}")

        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)

        self.init_ui()
        self.update_datetime()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f4f6f8;
            }
            QLabel {
                color: #333;
            }
        """)

        header_frame = QFrame()
        header_frame.setMinimumHeight(180)
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet("""
            #headerFrame {
                background: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5,
                                           stop:0 #3949ab, stop:0.5 #5c6bc0, stop:1 #7986cb);
                border-radius: 12px;
                padding: 20px 25px;
            }
        """)
        header_shadow = QGraphicsDropShadowEffect(self)
        header_shadow.setBlurRadius(20)
        header_shadow.setColor(QColor(0, 0, 0, 50))
        header_shadow.setOffset(0, 4)
        header_frame.setGraphicsEffect(header_shadow)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        welcome_label = QLabel("Student Management Dashboard")
        welcome_label.setStyleSheet("""
            color: white;
            font-size: 26px; 
            font-weight: 600;
            background-color: transparent;
        """)
        welcome_label.setAlignment(Qt.AlignLeft)

        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9); 
            font-size: 14px;
            background-color: transparent;
        """)
        self.datetime_label.setAlignment(Qt.AlignLeft)

        user_name = getattr(self.user, 'username', self.current_user_str)
        user_info = QLabel(f"User: {user_name}")
        user_info.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9); 
            font-size: 14px;
            background-color: transparent;
        """)
        user_info.setAlignment(Qt.AlignLeft)

        self.session_info = QLabel()
        self.session_info.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8); 
            font-size: 13px;
            background-color: transparent;
        """)
        self.session_info.setAlignment(Qt.AlignLeft)

        header_layout.addWidget(welcome_label)
        header_layout.addWidget(self.datetime_label)
        header_layout.addWidget(user_info)
        header_layout.addWidget(self.session_info)
        header_layout.addStretch(1)

        main_layout.addWidget(header_frame)

        metrics_container = QFrame()
        metrics_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        metrics_shadow = QGraphicsDropShadowEffect(self)
        metrics_shadow.setBlurRadius(15)
        metrics_shadow.setColor(QColor(0, 0, 0, 30))
        metrics_shadow.setOffset(0, 2)
        metrics_container.setGraphicsEffect(metrics_shadow)

        metrics_layout = QVBoxLayout(metrics_container)
        metrics_layout.setContentsMargins(20, 15, 20, 20)
        metrics_layout.setSpacing(15)

        metrics_header = QLabel("Key Statistics")
        metrics_header.setStyleSheet("font-size: 18px; font-weight: 600; color: #424242; margin-bottom: 5px;")
        metrics_layout.addWidget(metrics_header)

        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(20)
        metrics_grid.setContentsMargins(0, 10, 0, 0)

        self.total_students_widget = NumberDisplayWidget("Total Students")
        self.active_courses_widget = NumberDisplayWidget("Active Courses")
        self.active_courses_widget.set_color("#4CAF50")

        self.new_students_widget = NumberDisplayWidget("New Students (30 days)")
        self.new_students_widget.set_color("#FF9800")

        self.hostel_students_widget = NumberDisplayWidget("Students in Hostel")
        self.hostel_students_widget.set_color("#9C27B0")

        metrics_grid.addWidget(self.total_students_widget, 0, 0)
        metrics_grid.addWidget(self.active_courses_widget, 0, 1)
        metrics_grid.addWidget(self.new_students_widget, 1, 0)
        metrics_grid.addWidget(self.hostel_students_widget, 1, 1)

        metrics_layout.addLayout(metrics_grid)
        main_layout.addWidget(metrics_container)

        charts_container = QFrame()
        charts_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        charts_shadow = QGraphicsDropShadowEffect(self)
        charts_shadow.setBlurRadius(15)
        charts_shadow.setColor(QColor(0, 0, 0, 30))
        charts_shadow.setOffset(0, 2)
        charts_container.setGraphicsEffect(charts_shadow)

        charts_layout = QVBoxLayout(charts_container)
        charts_layout.setContentsMargins(20, 15, 20, 20)
        charts_layout.setSpacing(15)

        charts_header = QLabel("Analytics Overview")
        charts_header.setStyleSheet("font-size: 18px; font-weight: 600; color: #424242; margin-bottom: 5px;")
        charts_layout.addWidget(charts_header)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(20)
        charts_grid.setContentsMargins(0, 10, 0, 0)

        self.gender_chart = self.create_pie_chart("Student Gender Distribution")
        charts_grid.addWidget(self.gender_chart, 0, 0)

        self.enrollment_chart = self.create_pie_chart("Enrollment Status")
        charts_grid.addWidget(self.enrollment_chart, 0, 1)

        self.monthly_chart = self.create_bar_chart("Monthly Admissions (Last 6 Months)")
        charts_grid.addWidget(self.monthly_chart, 1, 0, 1, 2)

        charts_layout.addLayout(charts_grid)
        main_layout.addWidget(charts_container)

        actions_container = QFrame()
        actions_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        actions_shadow = QGraphicsDropShadowEffect(self)
        actions_shadow.setBlurRadius(15)
        actions_shadow.setColor(QColor(0, 0, 0, 30))
        actions_shadow.setOffset(0, 2)
        actions_container.setGraphicsEffect(actions_shadow)

        actions_layout = QVBoxLayout(actions_container)
        actions_layout.setContentsMargins(20, 15, 20, 20)
        actions_layout.setSpacing(15)

        actions_header = QLabel("Quick Access")
        actions_header.setStyleSheet("font-size: 18px; font-weight: 600; color: #424242; margin-bottom: 5px;")
        actions_layout.addWidget(actions_header)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 10, 0, 0)

        self.create_action_button(buttons_layout, "Students", None, self.open_student_registration)
        self.create_action_button(buttons_layout, "Courses", None, self.open_course_management)
        self.create_action_button(buttons_layout, "Reports", None, self.open_reports)
        buttons_layout.addStretch(1)

        actions_layout.addLayout(buttons_layout)
        main_layout.addWidget(actions_container)

        main_layout.addStretch(1)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 10, 0, 0)

        self.last_update_label = QLabel("Last updated: Never")
        self.last_update_label.setStyleSheet("color: #757575; font-size: 11px;")
        self.last_update_label.setAlignment(Qt.AlignRight)

        footer_layout.addStretch(1)
        footer_layout.addWidget(self.last_update_label)
        main_layout.addLayout(footer_layout)

    def create_pie_chart(self, title):
        chart = QChart()
        chart.setTitle(title)
        chart.setTitleFont(QFont("Segoe UI", 11, QFont.Bold))
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 9))
        chart.setBackgroundBrush(QBrush(Qt.transparent))
        chart.setMargins(QMargins(5, 5, 5, 5))

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(280)
        chart_view.setStyleSheet("background-color: transparent; border: none;")

        chart_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        chart_view.setRenderHint(QPainter.SmoothPixmapTransform)

        return chart_view

    def create_bar_chart(self, title):
        chart = QChart()
        chart.setTitle(title)
        chart.setTitleFont(QFont("Segoe UI", 11, QFont.Bold))
        chart.legend().setVisible(False)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 9))
        chart.setBackgroundBrush(QBrush(Qt.transparent))
        chart.setMargins(QMargins(5, 5, 5, 5))

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(300)
        chart_view.setStyleSheet("background-color: transparent; border: none;")

        return chart_view

    def create_action_button(self, layout, title, icon_path, callback):
        button = QPushButton(title)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(40)
        button.setMinimumWidth(120)

        if icon_path:
            try:
                button.setIcon(QIcon(icon_path))
                button.setIconSize(QSize(18, 18))
            except Exception as e:
                self.logger.error(f"Failed to load icon {icon_path}: {str(e)}")

        button.setStyleSheet("""
            QPushButton {
                background-color: #e3f2fd;
                color: #1e88e5;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 13px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #bbdefb;
            }
            QPushButton:pressed {
                background-color: #90caf9;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        button.setGraphicsEffect(shadow)

        button.clicked.connect(callback)
        layout.addWidget(button)

    def update_datetime(self):
        try:
            now = QDateTime.currentDateTimeUtc()
            pakistan_time = now.addSecs(5 * 60 * 60)
            formatted_time = pakistan_time.toString("dddd, MMMM d, yyyy hh:mm:ss AP")
            self.datetime_label.setText(f"{formatted_time} (PST)")
        except Exception as e:
            self.logger.error(f"Error updating datetime: {str(e)}")
            self.datetime_label.setText("Error updating time")


    def update_session_info(self):
        ip_address = "N/A"
        login_time = "N/A"
        try:
            if self.session:
                ip_address = getattr(self.session, 'ip_address', 'N/A') or "N/A"
                created_at_utc = getattr(self.session, 'created_at', None)

                if isinstance(created_at_utc, datetime.datetime):
                    login_time_pk = created_at_utc + datetime.timedelta(hours=5)
                    login_time = login_time_pk.strftime("%Y-%m-%d %I:%M %p")
        except Exception as e:
             self.logger.error(f"Error formatting session info: {str(e)}")

        self.session_info.setText(f"IP: {ip_address} | Logged In: {login_time}")

    def load_data(self):
        self.logger.info("Starting dashboard data load...")
        stats = None
        try:
            if not self.first_load and self.db_session:
                 self.db_session.expire_all()
                 self.logger.info("Database session expired for refresh.")

            stats = self.get_analytics_data()

            if not stats:
                raise ValueError("Failed to retrieve analytics data.")

            self.total_students_widget.set_value(stats.get('total_students', 0))
            self.active_courses_widget.set_value(stats.get('active_courses', 0))
            self.new_students_widget.set_value(stats.get('new_registrations', 0))
            self.hostel_students_widget.set_value(stats.get('hostel_students', 0))

            animate = self.should_animate()
            self.logger.info(f"Animation enabled for this load: {animate}")

            gender_chart = self.gender_chart.chart()
            gender_chart.removeAllSeries()
            gender_chart.setAnimationOptions(QChart.SeriesAnimations if animate else QChart.NoAnimation)

            gender_series = QPieSeries()
            gender_series.setHoleSize(0.35)
            male_count = stats.get('male_count', 0)
            female_count = stats.get('female_count', 0)

            male_slice = gender_series.append(f"Male ({male_count})", male_count)
            female_slice = gender_series.append(f"Female ({female_count})", female_count)

            male_slice.setBrush(QColor("#2196F3"))
            female_slice.setBrush(QColor("#E91E63"))
            male_slice.setLabelVisible(True)
            female_slice.setLabelVisible(True)
            if male_count >= female_count:
                 male_slice.setExploded(True)
            else:
                 female_slice.setExploded(True)

            gender_series.setLabelsPosition(QPieSlice.LabelOutside)
            for slice_ in gender_series.slices():
                slice_.setLabel(f"{slice_.label()} - {slice_.percentage()*100:.1f}%")
                slice_.setLabelFont(QFont("Segoe UI", 8))

            gender_chart.addSeries(gender_series)

            enrollment_chart = self.enrollment_chart.chart()
            enrollment_chart.removeAllSeries()
            enrollment_chart.setAnimationOptions(QChart.SeriesAnimations if animate else QChart.NoAnimation)

            enrollment_series = QPieSeries()
            enrollment_series.setHoleSize(0.35)
            active_count = stats.get('active_enrollments', 0)
            completed_count = stats.get('completed_enrollments', 0)

            active_slice = enrollment_series.append(f"Active ({active_count})", active_count)
            completed_slice = enrollment_series.append(f"Completed ({completed_count})", completed_count)

            active_slice.setBrush(QColor("#FFB300"))
            completed_slice.setBrush(QColor("#8BC34A"))
            active_slice.setLabelVisible(True)
            completed_slice.setLabelVisible(True)
            if active_count >= completed_count:
                active_slice.setExploded(True)
            else:
                completed_slice.setExploded(True)

            enrollment_series.setLabelsPosition(QPieSlice.LabelOutside)
            for slice_ in enrollment_series.slices():
                slice_.setLabel(f"{slice_.label()} - {slice_.percentage()*100:.1f}%")
                slice_.setLabelFont(QFont("Segoe UI", 8))

            enrollment_chart.addSeries(enrollment_series)

            monthly_chart = self.monthly_chart.chart()
            monthly_chart.removeAllSeries()
            for axis in monthly_chart.axes():
                monthly_chart.removeAxis(axis)

            monthly_chart.setAnimationOptions(QChart.SeriesAnimations if animate else QChart.NoAnimation)

            bar_set = QBarSet("Admissions")
            gradient = QLinearGradient(0, 0, 0, 300)
            gradient.setColorAt(0.0, QColor("#42A5F5"))
            gradient.setColorAt(1.0, QColor("#1E88E5"))
            bar_set.setBrush(gradient)
            bar_set.setBorderColor(Qt.transparent)

            categories = []
            counts = []
            max_value = 0
            monthly_admissions = stats.get('monthly_admissions', [])
            if not monthly_admissions:
                 monthly_admissions = self.get_empty_months()

            for month, count in monthly_admissions:
                categories.append(month)
                counts.append(count)
                if count > max_value:
                    max_value = count
            bar_set.append(counts)

            bar_series = QBarSeries()
            bar_series.append(bar_set)
            bar_series.setBarWidth(0.8)
            monthly_chart.addSeries(bar_series)

            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            axis_x.setLabelsFont(QFont("Segoe UI", 9))
            axis_x.setLabelsColor(QColor("#616161"))
            monthly_chart.addAxis(axis_x, Qt.AlignBottom)
            bar_series.attachAxis(axis_x)

            axis_y = QValueAxis()
            axis_y.setRange(0, max(max_value * 1.1, 10))
            axis_y.setTickCount(6)
            axis_y.setLabelsFont(QFont("Segoe UI", 9))
            axis_y.setLabelsColor(QColor("#616161"))
            axis_y.setGridLineVisible(True)
            axis_y.setGridLineColor(QColor("#eeeeee"))
            monthly_chart.addAxis(axis_y, Qt.AlignLeft)
            bar_series.attachAxis(axis_y)

            now = QDateTime.currentDateTime()
            self.last_update_label.setText(f"Last updated: {now.toString('yyyy-MM-dd hh:mm:ss AP')}")

            if animate:
                self.animation_played = True
                self.logger.info("Animations played, setting animation_played flag to True.")

            self.logger.info(f"Dashboard data loaded successfully.")

        except Exception as e:
            self.logger.error(f"Error loading dashboard data: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.last_update_label.setText(f"Update failed: {QDateTime.currentDateTime().toString('hh:mm:ss AP')}")

    def should_animate(self):
        should = self.first_load or not self.animation_played
        self.logger.debug(f"should_animate check: first_load={self.first_load}, animation_played={self.animation_played} -> Result: {should}")
        return should

    def get_analytics_data(self):
        self.logger.info("Fetching analytics data from database...")
        analytics = self.get_empty_analytics_structure()

        if not self.db_session:
            self.logger.warning("Database session not available for analytics.")
            return analytics

        if not MODELS_AVAILABLE:
            self.logger.warning("Required models not available for analytics.")
            return analytics

        try:
            analytics['total_students'] = self.db_session.query(func.count(Student.student_id)).scalar() or 0

            if hasattr(Student, 'gender'):
                analytics['male_count'] = self.db_session.query(func.count(Student.student_id)).filter(Student.gender.ilike('M%')).scalar() or 0
                analytics['female_count'] = self.db_session.query(func.count(Student.student_id)).filter(Student.gender.ilike('F%')).scalar() or 0
                other_count = analytics['total_students'] - analytics['male_count'] - analytics['female_count']
                if other_count > 0:
                     self.logger.warning(f"Found {other_count} students with gender other than M/F.")
            else:
                self.logger.warning("Student model has no 'gender' attribute. Cannot calculate gender breakdown.")


            if hasattr(Course, 'is_active'):
                 analytics['active_courses'] = self.db_session.query(func.count(Course.course_id)).filter(Course.is_active == True).scalar() or 0
            else:
                 analytics['active_courses'] = self.db_session.query(func.count(Course.course_id)).scalar() or 0
                 self.logger.warning("Course model has no 'is_active' attribute. Counting all courses.")


            if hasattr(Enrollment, 'completion_status'):
                try:
                    analytics['active_enrollments'] = self.db_session.query(func.count(Enrollment.enrollment_id)).filter(Enrollment.completion_status == False).scalar() or 0
                    analytics['completed_enrollments'] = self.db_session.query(func.count(Enrollment.enrollment_id)).filter(Enrollment.completion_status == True).scalar() or 0
                except Exception:
                    try:
                        analytics['active_enrollments'] = self.db_session.query(func.count(Enrollment.enrollment_id)).filter(Enrollment.completion_status == 0).scalar() or 0
                        analytics['completed_enrollments'] = self.db_session.query(func.count(Enrollment.enrollment_id)).filter(Enrollment.completion_status == 1).scalar() or 0
                    except Exception as e:
                         self.logger.error(f"Could not determine enrollment status (tried bool and int): {e}")
            else:
                 self.logger.warning("Enrollment model has no 'completion_status' attribute.")


            thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
            date_field_reg = None
            if hasattr(Student, 'admission_date'): date_field_reg = Student.admission_date
            elif hasattr(Student, 'date_of_registration'): date_field_reg = Student.date_of_registration
            elif hasattr(Student, 'created_at'): date_field_reg = Student.created_at

            if date_field_reg:
                try:
                    analytics['new_registrations'] = self.db_session.query(func.count(Student.student_id)).filter(
                        date_field_reg >= thirty_days_ago).scalar() or 0
                except Exception as e:
                    self.logger.error(f"Error querying new registrations using {date_field_reg.key}: {e}")
            else:
                self.logger.warning("No suitable date field found for new registrations (tried admission_date, date_of_registration, created_at).")


            if hasattr(HostelManagement, 'active_status'):
                try:
                    analytics['hostel_students'] = self.db_session.query(func.count(HostelManagement.hostel_id)).filter(HostelManagement.active_status == True).scalar() or 0
                except Exception as e:
                     self.logger.error(f"Error querying active hostel students: {e}")
                     if hasattr(HostelManagement, 'hostel_id'):
                         analytics['hostel_students'] = self.db_session.query(func.count(HostelManagement.hostel_id)).scalar() or 0
            elif hasattr(HostelManagement, 'hostel_id'):
                 analytics['hostel_students'] = self.db_session.query(func.count(HostelManagement.hostel_id)).scalar() or 0
                 self.logger.warning("HostelManagement has no 'active_status'. Counting all records.")
            else:
                 self.logger.warning("HostelManagement model or required fields not found.")


            date_field_adm = date_field_reg
            if date_field_adm:
                monthly_data = []
                current_date = datetime.datetime.utcnow()
                for i in range(5, -1, -1):
                    target_month_date = current_date - datetime.timedelta(days=30 * i)
                    month_start = datetime.datetime(target_month_date.year, target_month_date.month, 1)

                    next_month_year = month_start.year
                    next_month_month = month_start.month + 1
                    if next_month_month > 12:
                        next_month_month = 1
                        next_month_year += 1
                    month_end = datetime.datetime(next_month_year, next_month_month, 1) - datetime.timedelta(seconds=1)

                    month_name = month_start.strftime("%b %y")

                    try:
                        count = self.db_session.query(func.count(Student.student_id)).filter(
                            date_field_adm >= month_start,
                            date_field_adm <= month_end
                        ).scalar() or 0
                        monthly_data.append((month_name, count))
                    except Exception as e:
                        self.logger.error(f"Error querying admissions for {month_name}: {e}")
                        monthly_data.append((month_name, 0))

                analytics['monthly_admissions'] = monthly_data
            else:
                self.logger.warning("No date field for monthly admissions. Using empty data.")
                analytics['monthly_admissions'] = self.get_empty_months()


            self.logger.info(f"Analytics data fetched: {analytics}")
            return analytics

        except Exception as e:
            self.logger.error(f"Fatal error fetching dashboard analytics: {str(e)}")
            self.logger.error(traceback.format_exc())
            return self.get_empty_analytics_structure()

    def get_empty_analytics_structure(self):
        return {
            'total_students': 0,
            'male_count': 0,
            'female_count': 0,
            'active_courses': 0,
            'active_enrollments': 0,
            'completed_enrollments': 0,
            'new_registrations': 0,
            'hostel_students': 0,
            'monthly_admissions': self.get_empty_months()
        }

    def get_empty_months(self, num_months=6):
        monthly_data = []
        current_date = datetime.datetime.utcnow()
        for i in range(num_months - 1, -1, -1):
            target_month_date = current_date - datetime.timedelta(days=30 * i)
            month_name = datetime.datetime(target_month_date.year, target_month_date.month, 1).strftime("%b %y")
            monthly_data.append((month_name, 0))
        return monthly_data


    def handle_tab_activation(self):
        self.logger.info("Dashboard tab activated, refreshing data...")

        try:
             self.load_data()

        except Exception as e:
             self.logger.error(f"Error during tab activation refresh: {e}")
             QMessageBox.warning(self, "Refresh Error", f"Failed to refresh dashboard data:\n{str(e)}")


    def _request_tab_switch(self, index):
        self.logger.info(f"Requesting switch to tab index {index}")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.tab_switch_requested.emit(index)
        QTimer.singleShot(150, QApplication.restoreOverrideCursor)

    def open_student_registration(self):
        self._request_tab_switch(1)

    def open_course_management(self):
        self._request_tab_switch(2)

    def open_reports(self):
        self._request_tab_switch(3)

    def open_settings(self):
        self.logger.info("Settings action triggered")
        QMessageBox.information(self, "Settings", "Settings module is not yet implemented.")


    def getOpacity(self):
        return self._opacity

    def setOpacity(self, opacity):
        self._opacity = opacity
        self.setWindowOpacity(opacity)

    opacity = pyqtProperty(float, getOpacity, setOpacity)

    def showEvent(self, event):
        super().showEvent(event)

        if not self.first_load:
            self.logger.debug("Dashboard showEvent: Tab reactivated.")
            self.handle_tab_activation()
        else:
            self.logger.debug("Dashboard showEvent: First load.")
            self.first_load = False

        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"opacity", self)
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.start()

        event.accept()


    def hideEvent(self, event):
        super().hideEvent(event)
        event.accept()


    def cleanup(self):
        self.logger.info("Cleaning up DashboardWidget resources...")
        if hasattr(self, 'datetime_timer'):
            self.datetime_timer.stop()
            self.logger.info("Stopped datetime timer.")

        if hasattr(self, 'db_session') and self.db_session:
            try:
                self.db_session.close()
                self.logger.info("Closed database session.")
            except Exception as e:
                self.logger.error(f"Error closing database session: {str(e)}")

        if hasattr(self, 'fade_animation') and self.fade_animation:
            self.fade_animation.stop()

        self.logger.info("Dashboard cleanup complete.")

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)