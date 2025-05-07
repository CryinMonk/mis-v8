# from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
#                              QLabel, QLineEdit, QComboBox, QPushButton,
#                              QDateEdit, QCheckBox, QGroupBox, QSlider, QTableWidget,
#                              QTableWidgetItem, QHeaderView, QSplitter, QFrame,
#                              QTabWidget, QScrollArea, QMessageBox)
# from PyQt5.QtCore import Qt, QDate, pyqtSignal
# from PyQt5.QtGui import QFont, QIcon
#
#
# class FilterPanel(QWidget):
#     """Panel with filter controls for table data"""
#
#     filterChanged = pyqtSignal(dict)  # Signal emitted when filters change
#
#     def __init__(self, filter_config, parent=None):
#         super().__init__(parent)
#         self.filter_config = filter_config
#         self.filters = {}
#         self.init_ui()
#
#     def init_ui(self):
#         main_layout = QVBoxLayout(self)
#
#         # Create scroll area for filters
#         scroll_area = QScrollArea()
#         scroll_area.setWidgetResizable(True)
#         scroll_widget = QWidget()
#         scroll_layout = QVBoxLayout(scroll_widget)
#
#         # Group common filter controls
#         search_group = QGroupBox("Search")
#         search_layout = QVBoxLayout(search_group)
#
#         # Search field
#         self.search_input = QLineEdit()
#         self.search_input.setPlaceholderText("Search text...")
#         self.search_input.textChanged.connect(self.on_filter_changed)
#         search_layout.addWidget(self.search_input)
#
#         # Search fields selector (if multiple fields are searchable)
#         if len(self.filter_config.get('searchable_fields', [])) > 1:
#             search_fields_layout = QHBoxLayout()
#             search_fields_label = QLabel("Search in:")
#             self.search_fields = QComboBox()
#             self.search_fields.addItem("All Fields")
#             self.search_fields.addItems(self.filter_config.get('searchable_fields', []))
#             search_fields_layout.addWidget(search_fields_label)
#             search_fields_layout.addWidget(self.search_fields)
#             search_layout.addLayout(search_fields_layout)
#
#         # Add search group to main layout
#         scroll_layout.addWidget(search_group)
#
#         # Date filters (if applicable)
#         date_fields = self.filter_config.get('date_fields', [])
#         if date_fields:
#             date_group = QGroupBox("Date Filters")
#             date_layout = QFormLayout(date_group)
#
#             # Create date filter controls for each date field
#             self.date_filters = {}
#             for field in date_fields:
#                 field_layout = QHBoxLayout()
#
#                 # From date
#                 from_date = QDateEdit(calendarPopup=True)
#                 from_date.setDate(QDate.currentDate().addYears(-5))  # Default to 5 years ago
#                 from_date.setDisplayFormat("yyyy-MM-dd")
#
#                 # To date
#                 to_date = QDateEdit(calendarPopup=True)
#                 to_date.setDate(QDate.currentDate())  # Default to today
#                 to_date.setDisplayFormat("yyyy-MM-dd")
#
#                 # Enable checkbox
#                 enable_check = QCheckBox()
#                 enable_check.setChecked(False)
#                 from_date.setEnabled(False)
#                 to_date.setEnabled(False)
#
#                 # Connect signals
#                 enable_check.stateChanged.connect(
#                     lambda state, f=from_date, t=to_date: self.toggle_date_filter(state, f, t))
#                 from_date.dateChanged.connect(self.on_filter_changed)
#                 to_date.dateChanged.connect(self.on_filter_changed)
#
#                 # Store controls
#                 self.date_filters[field] = {
#                     'enable': enable_check,
#                     'from': from_date,
#                     'to': to_date
#                 }
#
#                 field_layout.addWidget(enable_check)
#                 field_layout.addWidget(from_date)
#                 field_layout.addWidget(QLabel("to"))
#                 field_layout.addWidget(to_date)
#
#                 date_layout.addRow(f"{field.replace('_', ' ').title()}:", field_layout)
#
#             # Add date group to main layout
#             scroll_layout.addWidget(date_group)
#
#         # Boolean filters (if applicable)
#         boolean_fields = self.filter_config.get('boolean_fields', [])
#         if boolean_fields:
#             bool_group = QGroupBox("Boolean Filters")
#             bool_layout = QFormLayout(bool_group)
#
#             # Create toggle for each boolean field
#             self.bool_filters = {}
#             for field in boolean_fields:
#                 combo = QComboBox()
#                 combo.addItem("Any")
#                 combo.addItem("Yes")
#                 combo.addItem("No")
#                 combo.currentIndexChanged.connect(self.on_filter_changed)
#
#                 self.bool_filters[field] = combo
#                 bool_layout.addRow(f"{field.replace('_', ' ').title()}:", combo)
#
#             # Add boolean group to main layout
#             scroll_layout.addWidget(bool_group)
#
#         # Sorting controls
#         sort_group = QGroupBox("Sorting")
#         sort_layout = QFormLayout(sort_group)
#
#         self.sort_field = QComboBox()
#         self.sort_field.addItem("Default")
#         self.sort_field.addItems(self.filter_config.get('sortable_fields', []))
#
#         self.sort_order = QComboBox()
#         self.sort_order.addItem("Ascending")
#         self.sort_order.addItem("Descending")
#
#         sort_layout.addRow("Sort by:", self.sort_field)
#         sort_layout.addRow("Order:", self.sort_order)
#
#         # Connect sort signals
#         self.sort_field.currentIndexChanged.connect(self.on_filter_changed)
#         self.sort_order.currentIndexChanged.connect(self.on_filter_changed)
#
#         # Add sorting group to main layout
#         scroll_layout.addWidget(sort_group)
#
#         # Reset button
#         reset_btn = QPushButton("Reset Filters")
#         reset_btn.clicked.connect(self.reset_filters)
#         scroll_layout.addWidget(reset_btn)
#
#         # Add stretch to push everything up
#         scroll_layout.addStretch()
#
#         # Set the scroll widget and add to main layout
#         scroll_area.setWidget(scroll_widget)
#         main_layout.addWidget(scroll_area)
#
#     def toggle_date_filter(self, state, from_date, to_date):
#         """Enable/disable date filter fields based on checkbox state"""
#         from_date.setEnabled(state == Qt.Checked)
#         to_date.setEnabled(state == Qt.Checked)
#         self.on_filter_changed()
#
#     def on_filter_changed(self, *args, **kwargs):
#         """Update filters when any control changes"""
#         filters = {}
#
#         # Get search term
#         search_term = self.search_input.text().strip()
#         if search_term:
#             filters['search_term'] = search_term
#
#             # Get specific search fields if selected
#             if hasattr(self, 'search_fields') and self.search_fields.currentIndex() > 0:
#                 filters['search_fields'] = [self.search_fields.currentText()]
#
#         # Get date filters
#         if hasattr(self, 'date_filters'):
#             date_range = {}
#             for field, controls in self.date_filters.items():
#                 if controls['enable'].isChecked():
#                     date_range[field] = {
#                         'min': controls['from'].date().toString("yyyy-MM-dd"),
#                         'max': controls['to'].date().toString("yyyy-MM-dd")
#                     }
#             if date_range:
#                 filters['date_range'] = date_range
#
#         # Get boolean filters
#         if hasattr(self, 'bool_filters'):
#             boolean_filters = {}
#             for field, combo in self.bool_filters.items():
#                 if combo.currentIndex() > 0:
#                     # Index 1 = Yes, Index 2 = No
#                     boolean_filters[field] = (combo.currentIndex() == 1)
#             if boolean_filters:
#                 filters['boolean_filters'] = boolean_filters
#
#         # Get sorting
#         if self.sort_field.currentIndex() > 0:
#             filters['sort_by'] = self.sort_field.currentText()
#             filters['sort_order'] = 'asc' if self.sort_order.currentIndex() == 0 else 'desc'
#
#         # Emit the updated filters
#         self.filters = filters
#         self.filterChanged.emit(filters)
#
#     def reset_filters(self):
#         """Reset all filters to default values"""
#         self.search_input.clear()
#
#         if hasattr(self, 'search_fields'):
#             self.search_fields.setCurrentIndex(0)
#
#         if hasattr(self, 'date_filters'):
#             for field, controls in self.date_filters.items():
#                 controls['enable'].setChecked(False)
#
#         if hasattr(self, 'bool_filters'):
#             for field, combo in self.bool_filters.items():
#                 combo.setCurrentIndex(0)
#
#         self.sort_field.setCurrentIndex(0)
#         self.sort_order.setCurrentIndex(0)
#
#         # Update filters
#         self.filters = {}
#         self.filterChanged.emit({})
#
#
# class FilteredTableView(QWidget):
#     """Widget combining a filter panel with a table view"""
#
#     rowSelected = pyqtSignal(int, dict)  # Signal emitted when a row is selected (id, row_data)
#
#     def __init__(self, table_name, data_manager, parent=None):
#         super().__init__(parent)
#         self.table_name = table_name
#         self.data_manager = data_manager
#         self.current_filters = {}
#         self.current_page = 1
#         self.per_page = 50
#         self.total_count = 0
#
#         # Get filter configuration
#         self.filter_config = self.data_manager.get_filter_options(table_name)
#
#         self.init_ui()
#         self.load_data()
#
#     def init_ui(self):
#         main_layout = QHBoxLayout(self)
#
#         # Create splitter for filter panel and table
#         splitter = QSplitter(Qt.Horizontal)
#
#         # Create filter panel
#         self.filter_panel = FilterPanel(self.filter_config)
#         self.filter_panel.filterChanged.connect(self.on_filter_changed)
#
#         # Create frame for filter panel
#         filter_frame = QFrame()
#         filter_layout = QVBoxLayout(filter_frame)
#         filter_layout.addWidget(QLabel(f"<h3>Filter {self.table_name.replace('_', ' ').title()}</h3>"))
#         filter_layout.addWidget(self.filter_panel)
#         splitter.addWidget(filter_frame)
#
#         # Create table widget
#         table_frame = QFrame()
#         table_layout = QVBoxLayout(table_frame)
#
#         # Add title and stats
#         header_layout = QHBoxLayout()
#         title_label = QLabel(f"<h3>{self.table_name.replace('_', ' ').title()}</h3>")
#         self.stats_label = QLabel("")
#         header_layout.addWidget(title_label)
#         header_layout.addStretch()
#         header_layout.addWidget(self.stats_label)
#         table_layout.addLayout(header_layout)
#
#         # Create table
#         self.table = QTableWidget()
#         self.table.setEditTriggers(QTableWidget.NoEditTriggers)
#         self.table.setSelectionBehavior(QTableWidget.SelectRows)
#         self.table.setAlternatingRowColors(True)
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
#         self.table.horizontalHeader().setStretchLastSection(True)
#         self.table.verticalHeader().setVisible(False)
#         self.table.setSelectionMode(QTableWidget.SingleSelection)
#         self.table.itemSelectionChanged.connect(self.on_row_selected)
#         table_layout.addWidget(self.table)
#
#         # Add pagination controls
#         pagination_layout = QHBoxLayout()
#         self.prev_btn = QPushButton("Previous")
#         self.next_btn = QPushButton("Next")
#         self.page_label = QLabel("Page 1")
#
#         self.prev_btn.clicked.connect(self.prev_page)
#         self.next_btn.clicked.connect(self.next_page)
#
#         pagination_layout.addStretch()
#         pagination_layout.addWidget(self.prev_btn)
#         pagination_layout.addWidget(self.page_label)
#         pagination_layout.addWidget(self.next_btn)
#         pagination_layout.addStretch()
#
#         table_layout.addLayout(pagination_layout)
#         splitter.addWidget(table_frame)
#
#         # Set initial splitter sizes (30% filter, 70% table)
#         splitter.setSizes([300, 700])
#
#         main_layout.addWidget(splitter)
#
#     def load_data(self):
#         """Load data with current filters and pagination"""
#         # Prepare filter arguments
#         filter_args = {**self.current_filters}
#         filter_args['page'] = self.current_page
#         filter_args['per_page'] = self.per_page
#
#         # Get data
#         data, self.total_count = self.data_manager.get_filtered_data(self.table_name, **filter_args)
#
#         # Update table
#         self.update_table(data)
#
#         # Update pagination controls
#         self.update_pagination()
#
#         # Update stats
#         total_pages = (self.total_count + self.per_page - 1) // self.per_page
#         showing_from = (self.current_page - 1) * self.per_page + 1 if data else 0
#         showing_to = showing_from + len(data) - 1 if data else 0
#         self.stats_label.setText(f"Showing {showing_from}-{showing_to} of {self.total_count} records")
#
#     def update_table(self, data):
#         """Update table with new data"""
#         self.table.clear()
#
#         if not data:
#             self.table.setRowCount(0)
#             self.table.setColumnCount(0)
#             return
#
#         # Get column names from first data item
#         sample_item = data[0]
#         columns = list(sample_item.__dict__.keys())
#         # Remove SQLAlchemy internal attributes
#         columns = [col for col in columns if not col.startswith('_')]
#
#         # Set table columns
#         self.table.setColumnCount(len(columns))
#         self.table.setHorizontalHeaderLabels([col.replace('_', ' ').title() for col in columns])
#
#         # Add data rows
#         self.table.setRowCount(len(data))
#         for row_idx, item in enumerate(data):
#             for col_idx, column in enumerate(columns):
#                 value = getattr(item, column)
#                 if value is not None:
#                     self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
#
#             # Store row data for later retrieval
#             self.table.setRowHeight(row_idx, 30)
#
#     def update_pagination(self):
#         """Update pagination controls based on current data"""
#         total_pages = (self.total_count + self.per_page - 1) // self.per_page
#         self.page_label.setText(f"Page {self.current_page} of {total_pages}")
#
#         # Enable/disable pagination buttons
#         self.prev_btn.setEnabled(self.current_page > 1)
#         self.next_btn.setEnabled(self.current_page < total_pages)
#
#     def on_filter_changed(self, filters):
#         """Handle filter changes"""
#         self.current_filters = filters
#         self.current_page = 1  # Reset to first page
#         self.load_data()
#
#     def prev_page(self):
#         """Go to previous page"""
#         if self.current_page > 1:
#             self.current_page -= 1
#             self.load_data()
#
#     def next_page(self):
#         """Go to next page"""
#         total_pages = (self.total_count + self.per_page - 1) // self.per_page
#         if self.current_page < total_pages:
#             self.current_page += 1
#             self.load_data()
#
#     def on_row_selected(self):
#         """Handle row selection"""
#         selected_items = self.table.selectedItems()
#         if not selected_items:
#             return
#
#         # Get row data
#         row = selected_items[0].row()
#         primary_key_col = self.filter_config.get('primary_key')
#
#         # Find primary key value
#         pk_value = None
#         cols = [self.table.horizontalHeaderItem(col).text().lower().replace(' ', '_')
#                 for col in range(self.table.columnCount())]
#
#         if primary_key_col in cols:
#             pk_idx = cols.index(primary_key_col)
#             pk_item = self.table.item(row, pk_idx)
#             if pk_item:
#                 pk_value = int(pk_item.text())
#
#         # Get full row data
#         row_data = {}
#         for col in range(self.table.columnCount()):
#             col_name = cols[col]
#             item = self.table.item(row, col)
#             row_data[col_name] = item.text() if item else None
#
#         if pk_value:
#             self.rowSelected.emit(pk_value, row_data)