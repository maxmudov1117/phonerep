from rest_framework import permissions


class IsShopOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    - Safe methods (GET, HEAD, OPTIONS): allowed to any authenticated user (or you can change to AllowAny)
    - POST: allowed to authenticated users
    - PUT/PATCH/DELETE: only allowed to shop.created_by, shop.admins, or superusers.
    """

    def has_permission(self, request, view):
        # Allow list/retrieve for safe methods; creation allowed for authenticated users.
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action == "create":
            return request.user and request.user.is_authenticated
        # for other methods, object-level permission will be used
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Safe methods are allowed
        if request.method in permissions.SAFE_METHODS:
            return True

        # superusers always allowed
        if getattr(request.user, "is_superuser", False):
            return True

        # check owner
        if hasattr(obj, "created_by") and obj.created_by_id == request.user.id:
            return True

        # check admins many-to-many
        if obj.admins.filter(pk=request.user.pk).exists():
            return True

        return False
