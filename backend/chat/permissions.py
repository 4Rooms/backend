from rest_framework import permissions


class IsCreatorOrReadOnly(permissions.BasePermission):
    """Permission to update. Check that request is from the obj creator."""

    message = "The action is allowed only to the author"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # is only description field in request
        return obj.creator == request.user


class IsSenderOrReadOnly(permissions.BasePermission):
    """Permission to update. Check that request is from the obj sender."""

    message = "The action is allowed only to the author"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # is only description field in request
        return obj.user == request.user


class IsOnlyDescriptionInRequestData(permissions.BasePermission):
    """Permission to update chat description. Check that request has only a description field."""

    message = "Only the chat description can be changed"

    def has_object_permission(self, request, view, obj):
        if request.method != "PATCH":
            return True
        # is only description field in request
        is_only_description = len(request.data) == 1 and "description" in request.data
        return is_only_description


class IsOnlyTextInRequestData(permissions.BasePermission):
    """Permission to update message text. Check that request has only a text field."""

    message = "Only the message text can be changed"

    def has_object_permission(self, request, view, obj):
        if request.method != "PATCH":
            return True
        # is only text field in request
        is_only_text = len(request.data) == 1 and "text" in request.data
        return is_only_text


class IsEmailConfirm(permissions.BasePermission):
    """Permission. Checking that email is confirmed."""

    message = "The email address is unconfirmed."

    def has_permission(self, request, view):
        return request.user.is_email_confirmed
