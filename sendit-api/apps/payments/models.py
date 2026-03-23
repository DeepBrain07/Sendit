from django.db import models

# Create your models here.


class Transaction(models.Model):

    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    offer = models.OneToOneField(
        "offers.Offer",
        on_delete=models.CASCADE,
        related_name="transaction"
    )

    tx_ref = models.CharField(max_length=100, unique=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=Status.choices)

    gateway_response = models.JSONField(null=True, blank=True)

    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def mark_success(self, payload=None):
        if self.status == self.Status.SUCCESS:
            return  # idempotent

        self.status = self.Status.SUCCESS
        self.verified = True
        self.gateway_response = payload
        self.save()

    def mark_failed(self, payload=None):
        self.status = self.Status.FAILED
        self.gateway_response = payload
        self.save()

    def __str__(self):
        return self.tx_ref
