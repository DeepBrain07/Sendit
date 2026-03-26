from rest_framework.exceptions import ValidationError
from django.db import transaction
from ..models import Offer
from .offer_service import OfferService
from apps.core.models import Location
from apps.core.services.media_service import MediaService


class OfferStepService:

    STEP_ORDER = [
        "details",
        "location",
        "pricing",
        "review",
        "posted"
    ]
    STEP_FIELDS = {
        "details": ["package_type", "is_fragile", "description"],
        "location": ["pickup_location", "delivery_location", "pickup_time", "receiver_name", "receiver_phone"],
        "pricing": ["base_price", "is_urgent"],
    }

    @classmethod
    def get_next_step(cls, current_step):
        try:
            index = cls.STEP_ORDER.index(str(current_step).lower())
            return cls.STEP_ORDER[index + 1]
        except (ValueError, IndexError):
            return current_step
        
    @classmethod
    def _apply_step_data(cls, offer, step, data):
        allowed_fields = None
        if step == Offer.Step.REVIEW:
            allowed_fields = cls.STEP_FIELDS.get(Offer.Step.DETAILS, []) + cls.STEP_FIELDS.get(Offer.Step.LOCATION, []) + cls.STEP_FIELDS.get(Offer.Step.PRICING, [])
        else:
            allowed_fields = cls.STEP_FIELDS.get(step, [])
        print(f"[step service] allowed_fields {allowed_fields}")

        print(f"[step service] data{data}")
        media = data.pop("image", None)
        if media:
            MediaService.attach_file(media, offer, tag="thumbnail")

        # handle pickup and destination locations
        cls._handle_location_step(offer, data)

        for field in allowed_fields:
            if field in data:
                setattr(offer, field, data[field])
        offer.save()

    @classmethod
    def update_step(cls, offer, step, data, user):

      try:
          with transaction.atomic():

            # 1. Permission
            if offer.sender != user:
                raise ValidationError("Not your offer")

            # 2. Lock check (status-based)
            if offer.status in [Offer.Status.ACCEPTED, Offer.Status.IN_TRANSIT, Offer.Status.DELIVERED]:
                raise ValidationError("Offer can no longer be edited")

            # 3. Apply data
            cls._apply_step_data(offer, step, data)
            print(f"[step service] offer {offer}")

            # 4. Validate ONLY this step
            offer.validate_step(step)

            cls.update_step_forward_only(offer, cls.get_next_step(step))

            offer.save()

            return offer
      except Exception as e:
          # optional logging
          print(f"[Offer Step Service] Update step failed {str(e)}")
          raise e

    @classmethod
    def update_step_forward_only(cls, offer, step):
        """Update step only if it's forward in the flow"""
        if step == Offer.Step.REVIEW:
            return

        current_index = cls.STEP_ORDER.index(offer.current_step)
        new_index = cls.STEP_ORDER.index(step)

        if new_index > current_index:
            offer.current_step = step
    
    @classmethod
    def _handle_location_step(cls,offer, data):
        pickup_data = data.pop("pickup_location", None)
        delivery_data = data.pop("delivery_location", None)

        if pickup_data:
            if offer.pickup_location:
                # update existing
                for attr, value in pickup_data.items():
                    setattr(offer.pickup_location, attr, value)
                offer.pickup_location.save()
            else:
                # create new
                offer.pickup_location = Location.objects.create(**pickup_data)
    
        if delivery_data:
            if offer.delivery_location:
                for attr, value in delivery_data.items():
                    setattr(offer.delivery_location, attr, value)
                offer.delivery_location.save()
            else:
                offer.delivery_location = Location.objects.create(**delivery_data)

    @classmethod
    def post_offer(cls, offer, user):

        if offer.sender != user:
            raise ValidationError("Not your offer")

        if not offer.is_complete():
            raise ValidationError("Offer is incomplete")

        offer.status = offer.Status.POSTED
        offer.current_step = "posted"
        offer.save()

        try:
          OfferService.handle_offer_posted(offer)
        except Exception as e:
            print(f"[Offer Step Service] Notification handle offer failed {str(e)}")
        return offer
  
    @staticmethod
    def _post(offer, user):
      """update step draft to posted and status to the last step reviewed"""

      if offer.status == "POSTED" and offer.step == "REVIEW":
        raise ValidationError("Offer already POSTED")
  
      if offer.sender != user:
          raise ValidationError("Not your offer")
    
      if offer.current_step != "review":
          raise ValidationError("Complete all previous steps first")

      if offer.status != Offer.Status.DRAFT:
          raise ValidationError("Only draft can be posted")
      
      if not offer.is_complete():
        raise ValidationError("Offer incomplete")

      offer.status = Offer.Status.POSTED
      offer.current_step = Offer.Step.POSTED
      offer.save()

      OfferService.handle_offer_posted(offer)

      return offer
    