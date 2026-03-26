from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from .models import Escrow
from .serializers import EscrowSerializer
from .services.escrow_services import EscrowService 
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOfferOrProposalOwnerOrAdmin



class EscrowViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for viewing Escrows and triggering status transitions.
    - Fund: Fund the escrow
    -
    - Release: Release funds from the escrow (admin only)
    - Dispute: Open a dispute on the escrow
    """
    help_text = "View all escrows or view a specific escrow by ID."
    queryset = Escrow.objects.select_related('offer', 'released_by').all()
    serializer_class = EscrowSerializer
    permission_classes = [IsAuthenticated]

    @decorators.action(detail=True, permission_classes=[IsOfferOrProposalOwnerOrAdmin], methods=['post'])
    def fund(self, request, pk=None):
        escrow = self.get_object()
        # Call your specific service method
        EscrowService.fund_escrow(escrow)
        return Response({"status": "Escrow funded successfully"}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        escrow = self.get_object()
        # Pass the admin user and any extra data (like partial release amount)
        amount = request.data.get('amount', escrow.amount)
        EscrowService.release_funds(escrow, admin=request.user, amount=amount)
        return Response({"status": "Funds released"}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        escrow = self.get_object()
        reason = request.data.get('reason')
        EscrowService.open_dispute(escrow, user=request.user, reason=reason)
        return Response({"status": "Dispute opened"}, status=status.HTTP_200_OK)
