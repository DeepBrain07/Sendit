from apps.core.models import Notification


class NotificationService:
    """
    offer becomes POSTED
    offer is ACCEPTED
    (later: cancelled, delivered)
    """

    @staticmethod
<<<<<<< HEAD
    def create(user, type, title, message, content_object=None):
=======
    def create_notification(user, type, title, message, content_object=None):
>>>>>>> e534574 (Initial clean commit)
        
        """
        from core.services.notification_service import NotificationService

        def notify_offer_posted(offer):
            NotificationService.create_notification(
                user=offer.sender,
                type=type
                title="Offer Posted",
                message=f"Your offer {offer.code} is live",
                content_object=offer
            )
        """

        return Notification.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            content_object=content_object
        )

    @staticmethod
    def bulk_create(data_list):
        """
        data_list = [
            {user, type, title, message, content_object}
        ]
        """
        notifications = [
            Notification(**data) for data in data_list
        ]
        return Notification.objects.bulk_create(notifications)
