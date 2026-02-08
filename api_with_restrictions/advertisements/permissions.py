from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user == obj.creator
    

class IsAdminOrReadOnly(BasePermission):
    """Дополнительный permission для админов"""

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True 
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):    
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True 
        return request.user and request.user.is_staff