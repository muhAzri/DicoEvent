from rest_framework.permissions import BasePermission


class IsAdminOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin or request.user.is_superuser)
        )


class IsOrganizerAdminOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_organizer or request.user.is_admin or request.user.is_superuser)
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


class IsOrganizerOwnerOrAdmin(BasePermission):
    """
    Custom permission for events:
    - Organizers can only edit/delete their own events
    - Admins and superusers can edit/delete any event
    """
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return True
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_organizer or request.user.is_admin or request.user.is_superuser)
        )
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET']:
            return True
        
        # Admin and superuser can access any event
        if request.user.is_admin or request.user.is_superuser:
            return True
        
        # Organizers can only access their own events
        if request.user.is_organizer:
            return obj.organizer == request.user
        
        return False


class IsAuthenticatedUser(BasePermission):
    """
    Permission for regular users to create registrations and payments
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated