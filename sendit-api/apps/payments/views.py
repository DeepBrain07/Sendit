from rest_framework import permissions, status
import json
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.payments.services.webhook import WalletFundingWebhookService
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .services.payment_service import PaymentService
from apps.wallets.services.wallet_services import WalletService
from .utils import verify_signature

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class InterswitchWebhookView(APIView):
    """
    Webhook endpoint for Interswitch payment notifications.
    """
    authentication_classes = []  # Public endpoint
    permission_classes = []

    def post(self, request):
        # 🔴 verify signature

        secret = settings.INTERSWITCH_WEBHOOK_SECRET
        raw_body = request.body
        signature = request.headers.get("X-Interswitch-Signature")

        if not signature:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not verify_signature(raw_body, signature, secret):
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload =json.loads(raw_body)   
            if payload.get("event") != "TRANSACTION.COMPLETED":
                return Response(status=200)

            WalletFundingWebhookService.handle(payload)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error here
            logger.error(f"[InterswitchWebhookView] Error: {e}")
            return Response(status=status.HTTP_400_BAD_REQUEST)


class WebFundingViewSet(APIView):
    """
    Handles wallet top-up through web:
    - Generates transaction
    - Returns payload for frontend inline payment
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Provide details user can use to make payment (inline form) 
        and transaction status INITIATED
        """
        amount = request.data.get("amount")
        user = request.user

        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        wallet = getattr(user, "wallet", None)
        if not wallet:
            wallet = WalletService.create_wallet_account(user)

        try:
            transaction, payload = PaymentService.create_funding_payload(
                user=request.user,
                amount=float(amount)
            )

            return Response({
                "message": "Funding initiated",
                "transaction_id": transaction.id,
                "form_payload": payload,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
