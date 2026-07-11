from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = 'Admin role required.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_admin_role', False)
        )


class IsStaffOrAdminRole(BasePermission):
    message = 'Staff or admin role required.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_staff_role', False)
        )


class IsCustomerRole(BasePermission):
    message = 'Customer role required.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_customer_role', False)
        )
