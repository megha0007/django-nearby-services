__author__ = "Megha Shinde"
__date__ = "16-02-2026"
__lastupdatedby__ = "Megha Shinde"
__lastupdateddate__ = "18-02-2026"

from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "admin"
        )


class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["admin", "staff"]
        )
