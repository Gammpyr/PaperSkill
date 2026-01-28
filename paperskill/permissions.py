from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """ Является ли пользователь владельцем объекта """
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.owner == request.user
        return False
