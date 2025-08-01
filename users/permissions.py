from rest_framework.permissions import BasePermission


class IsAdminOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'superuser']
        )


class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow GET requests without authentication
        if request.method == 'GET':
            return True
        # Require authentication for other methods
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET requests for everyone
        if request.method == 'GET':
            return True
        # Only allow user to update their own profile
        return obj.id == request.user.id