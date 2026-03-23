from apps.payments.models import Transaction
from apps.core.services.notification_service import NotificationService

class WebhookService:
    """
    Service to handle incoming payment gateway webhooks.
    """

    @staticmethod
    def handle_payment_success(tx_ref, payload):
        """
        Handle a successful payment from Interswitch.
        - Marks transaction as success
        - Marks escrow as funded
        - Notifies the sender
        """
        try:
            transaction = Transaction.objects.select_related(
                "escrow", "offer", "offer__sender"
            ).get(tx_ref=tx_ref)
        except Transaction.DoesNotExist:
            # Log this error
            raise Exception(f"Transaction with reference {tx_ref} not found")

        if transaction.status == Transaction.Status.SUCCESS:
            return  # ✅ idempotent

        transaction.mark_success(payload)

        escrow = transaction.escrow
        escrow.mark_funded()

        # 🔔 notify
        NotificationService.notify(
            user=transaction.offer.sender,
            type="payment_success",
            title="Payment Successful",
            message=f"Your payment of {transaction.amount} for offer {transaction.offer.code} has been received.",
            obj=transaction.offer
        )
