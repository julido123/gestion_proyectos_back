from rest_framework import permissions

class IsAdminUserType(permissions.BasePermission):
    """
    Permiso que permite el acceso solo a los usuarios con user_type 'ADMIN'.
    """

    def has_permission(self, request, view):
        # Verifica que el usuario esté autenticado y tenga el tipo de usuario 'ADMIN'
        return request.user.is_authenticated and request.user.user_type == 'ADMIN'