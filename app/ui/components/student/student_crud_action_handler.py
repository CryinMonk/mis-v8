from PyQt5.QtWidgets import QMessageBox, QDialog

class StudentActionHandler:
    """Handles CRUD actions for StudentCrudWidget"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        
    def add_student(self):
        """Show comprehensive dialog to register a new student"""
        # Check permission first
        if self.parent.user_role and not self.parent.rbac.check_permission(self.parent.user_role, 'data', 'create'):
            self.parent.utils._log_activity("Permission denied: Attempted to add student")
            QMessageBox.warning(self.parent, "Permission Denied",
                                "You don't have permission to add new students.")
            return

        # Log the action
        self.parent.utils._log_activity("Opening student registration dialog")

        # Import here to avoid circular imports
        from app.ui.components.student_registration import StudentRegistrationDialog

        # Create the registration dialog with the current user
        registration_dialog = StudentRegistrationDialog(self.parent, current_user=self.parent.current_user)
        registration_dialog.student_added.connect(self.parent.on_student_added)
        registration_dialog.exec_()

    def on_student_added(self, student_id):
        """Handle when a new student is added"""
        self.parent.utils._log_activity(f"New student added with ID: {student_id}")

        # Reload the appropriate view (use current table selection)
        if self.parent.selected_table == "students":
            self.parent.table_manager.load_students()
            # Highlight the newly added student
            self.parent.table_manager.highlight_student(student_id)
        else:
            # If we're on a related table view, reload that too as the new student
            # registration might have added related records
            self.parent.table_manager.load_related_table_data()

        # Emit data changed signal
        self.parent.data_changed.emit()

    def edit_student(self):
        """Show dialog to edit an existing student"""
        # Check permission first
        if self.parent.user_role and not self.parent.rbac.check_permission(self.parent.user_role, 'data', 'update'):
            self.parent.utils._log_activity("Permission denied: Attempted to edit student")
            QMessageBox.warning(self.parent, "Permission Denied",
                                "You don't have permission to edit student records.")
            return

        sender = self.parent.sender()
        student_id = sender.property("student_id")

        # Ensure student_id is an integer
        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
            QMessageBox.warning(self.parent, "Error", f"Invalid student ID: {student_id}")
            return

        self.parent.utils._log_activity(f"Opening edit dialog for student with ID: {student_id}")

        student_data = self.parent.student_service.get_student_with_details(student_id)
        if not student_data:
            QMessageBox.warning(self.parent, "Warning", f"Student with ID {student_id} not found.")
            return

        # Use the comprehensive edit dialog
        from app.ui.components.student_edit_dialog import StudentEditDialog
        dialog = StudentEditDialog(student_data, self.parent)

        # If dialog is accepted (saved), reload the student list
        if dialog.exec_() == QDialog.Accepted:
            self.parent.utils._log_activity(f"Student with ID {student_id} updated")

            # Maintain current table view after editing
            self.parent.refresh_current_view()

            # If in student view, highlight the edited student
            if self.parent.selected_table == "students":
                self.parent.table_manager.highlight_student(student_id)

            # Emit data changed signal
            self.parent.data_changed.emit()

    def view_student(self):
        """Show detailed view of a student"""
        sender = self.parent.sender()
        student_id = sender.property("student_id")

        # Ensure student_id is an integer
        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
            QMessageBox.warning(self.parent, "Error", f"Invalid student ID: {student_id}")
            return

        self.parent.utils._log_activity(f"Viewing details for student with ID: {student_id}")

        student_data = self.parent.student_service.get_student_with_details(student_id)
        if not student_data:
            QMessageBox.warning(self.parent, "Warning", f"Student with ID {student_id} not found.")
            return

        from app.ui.components.student_details_dialog import StudentDetailsDialog
        dialog = StudentDetailsDialog(student_data, self.parent)
        dialog.exec_()

    def delete_student(self):
        """Delete a student after confirmation"""
        # Check permission first
        if self.parent.user_role and not self.parent.rbac.check_permission(self.parent.user_role, 'data', 'delete'):
            self.parent.utils._log_activity("Permission denied: Attempted to delete student")
            QMessageBox.warning(self.parent, "Permission Denied",
                                "You don't have permission to delete student records.")
            return

        sender = self.parent.sender()
        student_id = sender.property("student_id")

        self.parent.utils._log_activity(f"Confirming deletion of student with ID: {student_id}")

        reply = QMessageBox.question(
            self.parent, "Confirm Delete",
            f"Are you sure you want to delete student with ID {student_id}? This will also delete all related records.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.parent.utils._log_activity(f"User confirmed deletion of student with ID: {student_id}")

                success, message = self.parent.student_service.delete(student_id)
                if success:
                    self.parent.utils._log_activity(f"Student with ID {student_id} successfully deleted")
                    QMessageBox.information(self.parent, "Success", "Student deleted successfully.")

                    # Reload the current view - maintain table selection
                    self.parent.refresh_current_view()

                    # Emit data changed signal
                    self.parent.data_changed.emit()
                else:
                    self.parent.utils._log_activity(f"Failed to delete student with ID {student_id}: {message}")
                    QMessageBox.critical(self.parent, "Error", f"Failed to delete student: {message}")
            except Exception as e:
                self.parent.logger.error(f"Error deleting student #{student_id}: {str(e)}")
                QMessageBox.critical(self.parent, "Error", f"An unexpected error occurred: {str(e)}")