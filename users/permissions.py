from rest_framework.permissions import BasePermission


class IsAdminOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_superuser)
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


class UserDetailPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow GET requests without authentication
        if request.method == 'GET':
            return True
        # DELETE requires admin/superuser
        if request.method == 'DELETE':
            return (
                request.user and 
                request.user.is_authenticated and 
                (request.user.is_admin or request.user.is_superuser)
            )
        # PUT/PATCH requires authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET requests for everyone
        if request.method == 'GET':
            return True
        # DELETE requires admin/superuser (already checked in has_permission)
        if request.method == 'DELETE':
            return True
        # PUT/PATCH only allow users to update their own profile
        return obj.id == request.user.id