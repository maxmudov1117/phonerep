from rest_framework import permissions


class IsShopMemberOrReadOnly(permissions.BasePermission):
    """
    Placeholder permission: customize to allow writes only to authorized users.
    """

    def has_permission(self, request, view):
        # Allow safe methods for everyone; require auth for unsafe methods
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Example: allow edits only for members of the same shop
        # if hasattr(request.user, "shop"):
        #     return obj.shop_id == request.user.shop.id
        return True
