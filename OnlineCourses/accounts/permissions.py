from rest_framework.permissions import BasePermission

from accounts.models import User


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.RoleTypes.TEACHER

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == User.RoleTypes.STUDENT
