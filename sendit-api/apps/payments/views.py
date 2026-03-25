from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.payments.services.webhook import WebhookService
import json

class InterswitchWebhookView(APIView):
    """
    Webhook endpoint for Interswitch payment notifications.
    """
    authentication_classes = []  # Public endpoint
    permission_classes = []

    def post(self, request):
        payload = request.data
        tx_ref = payload.get("txn_ref")
        
        if not tx_ref:
            return Response({"error": "Missing txn_ref"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            WebhookService.handle_payment_success(tx_ref, payload)
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error here
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
