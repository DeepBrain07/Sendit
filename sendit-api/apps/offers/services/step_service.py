from rest_framework.exceptions import ValidationError
from django.db import transaction
from ..models import Offer
from .offer_service import OfferService
from apps.core.models import Location
from apps.core.services.media_service import MediaService

class OfferStepService:
    STEP_ORDER = ["details", "location", "pricing", "review", "posted"]
    
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
        # Determine which fields are allowed to be updated in this request
        if step == Offer.Step.REVIEW:
            allowed_fields = (cls.STEP_FIELDS["details"] + 
                             cls.STEP_FIELDS["location"] + 
                             cls.STEP_FIELDS["pricing"])
        else:
            allowed_fields = cls.STEP_FIELDS.get(step, [])

        # Handle Image
        media = data.pop("image", None)
        if media:
            try:
                MediaService.attach_file(media, offer, tag="thumbnail")
            except Exception as e:
                # Log but don't crash the whole process if Cloudinary is down
                print(f"[Step Service] Media attachment failed: {e}")

        # Handle locations specifically
        cls._handle_location_step(offer, data)

        # Update remaining fields
        for field in allowed_fields:
            if field in data:
                setattr(offer, field, data[field])
        
        offer.save()

    @classmethod
    def update_step_forward_only(cls, offer, step):
        """Update current_step only if the new step is further in the order"""
        try:
            current_index = cls.STEP_ORDER.index(offer.current_step)
            new_index = cls.STEP_ORDER.index(step)
            if new_index > current_index:
                offer.current_step = step
        except ValueError:
            pass # Handle case where current_step might not be in STEP_ORDER

    @classmethod
    def _handle_location_step(cls, offer, data):
        pickup_data = data.pop("pickup_location", None)
        delivery_data = data.pop("delivery_location", None)

        for loc_type, loc_data in [("pickup_location", pickup_data), ("delivery_location", delivery_data)]:
            if loc_data:
                existing_loc = getattr(offer, loc_type)
                if existing_loc:
                    for attr, value in loc_data.items():
                        setattr(existing_loc, attr, value)
                    existing_loc.save()
                else:
                    new_loc = Location.objects.create(**loc_data)
                    setattr(offer, loc_type, new_loc)