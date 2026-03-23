from django.db import transaction
from rest_framework.exceptions import ValidationError
from ..models import Offer
from .offer_service import OfferService


class OfferStatusService:
    """
     ALLOWED_TRANSITIONS = {
    "draft": ["posted"],
    "posted": ["accepted", "cancelled"],
    "accepted": ["in_transit", "cancelled"],
    "in_transit": ["delivered"],
}
    """

    @classmethod
    def transition(cls, offer, action, user):

        if action == Offer.Status.POSTED:
            return cls._post(offer, user)

        if action == Offer.Status.ACCEPTED:
            return cls._accept(offer, user)

        if action == Offer.Status.IN_TRANSIT:
            return cls._start_transit(offer, user)

        if action == offer.Status.DELIVERED:
            return cls._deliver(offer, user)

        if action == offer.Status.CANCELLED:
            return cls._cancel(offer, user)

        raise ValidationError("Invalid action")
    
  
    @staticmethod
    def _post(offer, user):
      if offer.sender != user:
          raise ValidationError("Not your offer")

      if offer.status != Offer.Status.DRAFT:
          raise ValidationError("Only draft can be posted")

      offer.status = Offer.Status.POSTED
      offer.current_step = Offer.Step.POSTED
      offer.is_complete()
      offer.save()

      OfferService.handle_offer_posted(offer)

      return offer
    
    @staticmethod
    def _accept(offer, user):

      if getattr(user, "type", None) != "carrier":
          raise ValidationError("Only carriers can accept")

      with transaction.atomic():
          offer = Offer.objects.select_for_update().get(pk=offer.pk)

          if offer.status != Offer.Status.POSTED:
              raise ValidationError("Offer not available")

          if offer.carrier:
              raise ValidationError("Offer already accepted")

          offer.carrier = user
          offer.status = Offer.Status.ACCEPTED
          offer.save()

      OfferService.handle_offer_accepted(offer)

      return offer
    
    @staticmethod
    def _start_transit(offer, user):
        if offer.carrier != user:
            raise ValidationError("Not your delivery")

        if offer.status != Offer.Status.ACCEPTED:
            raise ValidationError("Invalid state")

        offer.status = Offer.Status.IN_TRANSIT
        offer.save()

        return offer
    
    @staticmethod
    def _deliver(offer, user):
        if offer.carrier != user:
            raise ValidationError("Not your delivery")

        if offer.status != Offer.Status.IN_TRANSIT:
            raise ValidationError("Invalid state")

        offer.status = Offer.Status.DELIVERED
        offer.save()

        return offer

    @staticmethod
    def _cancel(offer, user):

      if offer.sender != user:
          raise ValidationError("Only sender can cancel")

      if offer.status not in [
          Offer.Status.POSTED,
          Offer.Status.ACCEPTED
      ]:
          raise ValidationError("Cannot cancel at this stage")

      offer.status = Offer.Status.CANCELLED
      offer.save()

      return offer

