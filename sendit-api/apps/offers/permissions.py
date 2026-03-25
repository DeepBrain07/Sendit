from rest_framework.permissions import BasePermission


class IsSender(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.type.sender == request.user


class IsCarrier(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "type", None) == "carrier"
