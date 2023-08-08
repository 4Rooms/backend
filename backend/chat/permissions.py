from rest_framework import permissions


class IsCreatorOrReadOnly(permissions.BasePermission):
    """Permission to update. Check that request is from the obj creator."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # is only description field in request
        return obj.creator == request.user


class IsOnlyDescriptionInRequestData(permissions.BasePermission):
    """Permission to update chat description. Check that request has only a description field."""

    def has_object_permission(self, request, view, obj):
        # is only description field in request
        is_only_description = len(request.data) == 1 and "description" in request.data
        return is_only_description
