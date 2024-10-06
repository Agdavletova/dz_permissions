from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только владельцу объекта для изменения или удаления.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить доступ только создателю объекта
        if request.user.is_staff == True:
            return True
        return obj.creator == request.user