from rest_framework.permissions import BasePermission

class IsStudent(BasePermission):
    """
    يسمح بس للـ users اللي role بتاعهم student
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "student")


class IsInstructor(BasePermission):
    """
    يسمح بس للـ users اللي role بتاعهم instructor
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "instructor")
