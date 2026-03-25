from apps.escrow.models import Escrow,LedgerEntry

from django.db.models import Sum


class WalletService:

    @staticmethod
    def get_breakdown(user):
        qs = Escrow.objects.filter(offer__carrier=user)

        return {
            "available": qs.filter(
                status="release_ready"
            ).aggregate(total=Sum("amount"))["total"] or 0,

            "locked": qs.filter(
                status="locked"
            ).aggregate(total=Sum("amount"))["total"] or 0,

            "in_transit": qs.filter(
                status="funded"
            ).aggregate(total=Sum("amount"))["total"] or 0,

            "total_earned": qs.filter(
                status="released"
            ).aggregate(total=Sum("amount"))["total"] or 0,
        }
  
    @staticmethod
    def get_history(user):
        return LedgerEntry.objects.filter(
            escrow__offer__carrier=user
        ).order_by("-created_at")
