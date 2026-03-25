from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Media(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    )

    file_url = models.URLField()
    public_id = models.CharField(max_length=255)

    media_type = models.CharField(
        max_length=20, choices=MEDIA_TYPE_CHOICES, default='image')

    # Generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey()

    # control fields
    # avatar, document, selfie, gallery
    tag = models.CharField(max_length=50, blank=True,
                           help_text="thumbnail for offer, avatar for profile, document, selfie, gallery")
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return f"{self.tag or 'media'} - {self.file_url}"


class Notification(models.Model):

    class Type(models.TextChoices):
        NEW_OFFER = "new_offer", "New Offer"
        OFFER_ACCEPTED = "offer_accepted", "Offer Accepted"
        OFFER_COMPLETED = "offer_completed", "Offer Completed"
        PAYMENT_SUCCESS = "payment_success", "Payment Success"
        PAYOUT_SUCCESS = "payout_success", "Payout Success"


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    type = models.CharField(max_length=50, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["created_at"]),
        ]

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    def __str__(self):
        return f"{self.user} - {self.type}"


class Location(models.Model):
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.city} - {self.area}"
