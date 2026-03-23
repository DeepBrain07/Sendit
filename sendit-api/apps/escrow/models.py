from django.db import models

# Create your models here.


class Escrow(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        FUNDED = "funded", "Funded"
        LOCKED = "locked", "Locked"
        RELEASE_READY = "release_ready", "Release Ready"
        RELEASED = "released", "Released"
        CANCELLED = "cancelled", "Cancelled"
        DISPUTED = "disputed", "Disputed"

    offer = models.OneToOneField(
        "offers.Offer",
        on_delete=models.CASCADE,
        related_name="escrow"
    )

    transaction = models.OneToOneField(
        "payments.Transaction",
        on_delete=models.CASCADE,
        related_name="escrow"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=Status.choices)

    is_released = models.BooleanField(default=False)
    released_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 STATE METHODS

    def mark_funded(self):
        if self.status != self.Status.PENDING:
            return

        self.status = self.Status.FUNDED
        self.save(update_fields=["status"])

    def lock(self):
        if self.status != self.Status.FUNDED:
            raise ValueError("Escrow must be funded first")

        self.status = self.Status.LOCKED
        self.save(update_fields=["status"])

    def mark_release_ready(self):
        if self.status != self.Status.LOCKED:
            raise ValueError("Escrow must be locked")

        self.status = self.Status.RELEASE_READY
        self.save(update_fields=["status"])

    def release(self):
        if self.status != self.Status.RELEASE_READY:
            raise ValueError("Not ready for release")


        self.status = self.Status.RELEASED
        self.is_released = True
        self.released_at = timezone.now()

        self.save(update_fields=["status", "is_released", "released_at"])

    def cancel(self):
        if self.status == self.Status.RELEASED:
            raise ValueError("Cannot cancel released escrow")

        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def dispute(self):
        if self.status not in [self.Status.LOCKED, self.Status.RELEASE_READY]:
            raise ValueError("Only locked or release_ready escrow can be disputed")

        self.status = self.Status.DISPUTED
        self.save(update_fields=["status"])


class LedgerEntry(models.Model):

    class EntryType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    escrow = models.ForeignKey(
        "escrow.Escrow",
        on_delete=models.CASCADE,
        related_name="entries"
    )

    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)



