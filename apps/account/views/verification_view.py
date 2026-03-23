
from ..models import Verification
from ..serializers import VerificationSerializer, ReviewVerificationSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone


class VerificationViewSet(viewsets.ModelViewSet):
    serializer_class = VerificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admin sees all verifications
        if user.is_staff or user.is_superuser:
            return Verification.objects.all()

        # Users see only theirs
        return Verification.objects.filter(profile=user.profile)

    def create(self, request, *args, **kwargs):
        try:

            serializer = self.get_serializer(
                data=request.data, context={'request': request}
            )

            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({"error":str(e)}, status=400)


    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

    def get_serializer_class(self):
        if self.action == "review":
            return ReviewVerificationSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def review(self, request, pk=None):
        """
        Admin verifies or rejects a verification.
        """
        verification = self.get_object()
        serializer = self.get_serializer(
            instance=verification,data=request.data, context={"request":request}, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Update verification
        verification.is_verified = data['is_verified']
        verification.note = data.get('note', verification.note)

        if verification.is_verified:
            verification.verified_by = request.user
            verification.verified_at = timezone.now()
        else:
            # Optional: clear if rejected
            verification.verified_by = None
            verification.verified_at = None

        verification.save()

        # ✅ Safer profile sync
        profile = verification.profile
        profile.is_verified = profile.verifications.filter(
            is_verified=True).exists()
        profile.save()

        return Response({
            "message": "Verification reviewed successfully",
            "is_verified": verification.is_verified,
            "note": verification.note,
            "verified_by": verification.verified_by.id if verification.verified_by else None,
            "verified_at": verification.verified_at
        }, status=status.HTTP_200_OK)
