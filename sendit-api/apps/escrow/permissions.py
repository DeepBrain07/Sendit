from rest_framework.permissions import BasePermission


class IsOfferOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.type.sender == request.user 

class IsOfferOwnerOrIsAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or superusers to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.type.sender == request.user or request.user.is_staff


class IsCarrier(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "type", None) == "carrier"

class IsOfferOrProposalOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.offer.sender == request.user or obj.carrier == request.user or request.user.is_superuser
