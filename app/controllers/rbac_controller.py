from app.models.user import UserRole


class RBACController:
    """
    Role-Based Access Control (RBAC) controller that manages permissions
    for different user roles
    """

    def __init__(self):
        # Define role permissions based on the requirements:
        # - Only admin can delete
        # - Data warehouse can insert and update but can't delete
        # - Supervisor can only create & view
        # - Teacher can only view
        # - All roles can generate reports
        # - Backup can be done by admin or data warehouse but only admin can delete backup
        self._permissions = {
            UserRole.ADMIN: {
                'users': ['read', 'create', 'update', 'delete'],
                'data': ['read', 'create', 'update', 'delete'],
                'reports': ['read', 'create', 'update', 'delete'],
                'settings': ['read', 'update'],
                'backup': ['read', 'create', 'restore', 'delete']
            },
            UserRole.DATA_WAREHOUSE: {
                'users': ['read'],
                'data': ['read', 'create', 'update'],  # Can insert and update but not delete
                'reports': ['read', 'create'],
                'settings': ['read'],
                'backup': ['read', 'create', 'restore']  # Can create and restore but not delete backups
            },
            UserRole.SUPERVISOR: {
                'users': ['read'],
                'data': ['read', 'create'],  # Can create and view
                'reports': ['read', 'create'],
                'settings': ['read'],
                'backup': ['read']  # Can only view backups
            },
            UserRole.TEACHER: {
                'users': [],
                'data': ['read'],  # Can only view data
                'reports': ['read', 'create'],  # Can generate reports
                'settings': [],
                'backup': []
            }
        }

    def check_permission(self, user_role, resource, action):
        """
        Check if a user with the given role has permission to perform
        the specified action on the resource

        Args:
            user_role: UserRole enum value
            resource: String resource name (e.g., 'users', 'data')
            action: String action name (e.g., 'read', 'create')

        Returns:
            Boolean indicating if permission is granted
        """
        if not isinstance(user_role, UserRole):
            return False

        role_permissions = self._permissions.get(user_role, {})
        resource_permissions = role_permissions.get(resource, [])

        return action in resource_permissions

    def get_user_permissions(self, user_role):
        """
        Get all permissions for a specific user role

        Args:
            user_role: UserRole enum value

        Returns:
            Dict of resources and their allowed actions
        """
        if not isinstance(user_role, UserRole):
            return {}

        return self._permissions.get(user_role, {})

    def can_delete(self, user_role, resource):
        """
        Check if a user with the given role can delete the specified resource.
        Only admins can delete resources.

        Args:
            user_role: UserRole enum value
            resource: String resource name (e.g., 'users', 'data')

        Returns:
            Boolean indicating if delete permission is granted
        """
        return self.check_permission(user_role, resource, 'delete')

    def can_generate_reports(self, user_role):
        """
        Check if a user with the given role can generate reports.
        All roles can generate reports.

        Args:
            user_role: UserRole enum value

        Returns:
            Boolean indicating if report creation permission is granted
        """
        return self.check_permission(user_role, 'reports', 'create')

    def summarize_role_permissions(self, user_role):
        """
        Provides a human-readable summary of what a role can do

        Args:
            user_role: UserRole enum value

        Returns:
            String describing the role's permissions
        """
        if not isinstance(user_role, UserRole):
            return "Invalid role specified"

        summaries = {
            UserRole.ADMIN: "Administrator with full access to all resources including deletion privileges",
            UserRole.DATA_WAREHOUSE: "Data warehouse role with ability to create, read and update data, but not delete. Can manage backups but not delete them.",
            UserRole.SUPERVISOR: "Supervisor role with read access and ability to create data and reports",
            UserRole.TEACHER: "Teacher role with read-only access to data and ability to generate reports"
        }

        return summaries.get(user_role, "Unknown role")