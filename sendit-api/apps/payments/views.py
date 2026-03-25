import json
import logging
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.payments.services.webhook import WalletFundingWebhookService
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.wallets.models import  Wallet
from apps.payments.models import Transaction
from apps.wallets.services.wallet_services import WalletService

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


def verify_signature(request_body, signature, secret):
    import hmac, hashlib

    computed = hmac.new(
        secret.encode(),
        request_body,
        hashlib.sha512
    ).hexdigest()

    return computed == signature


class WalletFundingService:

    @staticmethod
    def create_wallet_funding_payload(user, amount):
        """
        Creates a transaction and returns the payload the frontend
        will use to render the Interswitch payment form.
        """
        # Ensure wallet exists
        wallet = WalletService.create_wallet_account(user)

        # Create a unique tx_ref per funding attempt
        tx_ref = f"WEB_{uuid.uuid4().hex[:12]}"

        # Create transaction record (INITIATED)
        transaction = Transaction.objects.create(
            tx_ref=tx_ref,
            wallet=wallet,
            amount=amount,
            status=Transaction.Status.INITIATED
        )

        # Payload frontend can use for form
        payload = {
            "tx_ref": tx_ref,  # required by Interswitch
            "amount": int(amount * 100),  # kobo
            "currencyCode": "566",
            "customerId": user.email,
            "redirectUrl": settings.INTERSWITCH_CALLBACK_URL,
            "customerName": f"{user.full_name}",
        }

        return {
            "transaction": transaction,
            "form_payload": payload
        }