from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    message = 'Редактирование чужого контента запрещено!'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Редактировать контент может только администратор!'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or request.user.is_staff
        )
