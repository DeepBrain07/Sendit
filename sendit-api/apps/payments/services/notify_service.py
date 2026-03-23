from apps.core.services.notification_service import NotificationService

class NotifyServices:
    """
    Initiate → Pay → Webhook → Verify → Escrow FUNDED
    """

    @staticmethod
    def payment_success(transaction):

        offer = transaction.offer

        NotificationService.notify(
            user=offer.sender,
            type="payment_success",
            title="Payment Successful",
            message=f"Your escrow has been funded with (amount: {transaction.amount})",
            obj=offer)
