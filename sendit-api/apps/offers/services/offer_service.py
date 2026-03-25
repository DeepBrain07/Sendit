from apps.core.services.notification_service import NotificationService
from apps.account.models import Profile as UserProfile
from apps.core.services.geo_service import GeoService
from apps.core.models import Notification

# NOTIFICATION 

class OfferService:
    """
    Sender creates Offer
        ↓
      Offer POSTED
        ↓
      Notify nearby carriers
        ↓
      Carriers send Proposals
        ↓
      Notify sender (new proposal)
        ↓
      Sender accepts one proposal
        ↓
      Notify selected carrier
    """

    DEFAULT_RADIUS_KM = 10

    # -------------------------
    # 🔍 MATCHING: CARRIERS
    # -------------------------

    @classmethod
    def get_nearby_carriers(cls, pickup_location):
        profiles = UserProfile.objects.select_related("user", "location")
        nearby = []

        for profile in profiles:
            print(f"[offerservices]:1 {profile.location.latitude, profile.location.longitude}")
            
            if not profile.location:
                continue

            if getattr(profile, "type", None) != "carrier":
                continue

            distance = GeoService.distance_between_locations(
                pickup_location,
                profile.location
            )
           
            radius = cls.DEFAULT_RADIUS_KM

            if distance and distance <= radius:
                nearby.append(profile.user)

        print(f"[offerservices]:3 {[user.email for user in nearby]}")
        return nearby

    # -------------------------
    # 🔍 MATCHING: OFFERS
    # -------------------------

    @classmethod
    def get_nearby_offers(cls, offers,user_location, radius_km=10):

        # offers = Offer.objects.select_related("pickup_location")
        nearby = []

        for offer in offers:
            loc = offer.pickup_location

            if not loc:
                continue

            distance = GeoService.distance_between_locations(
                user_location,
                loc
            )

            if distance and distance <= radius_km:
                offer.distance = distance
                nearby.append(offer)

        return sorted(nearby, key=lambda x: x.distance)

    # -------------------------
    # 🔔 EVENT: OFFER POSTED
    # -------------------------

    @classmethod
    def handle_offer_posted(cls, offer):
        print(f"[offerservices]:handle_offer_posted {offer.pickup_location.latitude, offer.pickup_location.longitude}")
        carriers = cls.get_nearby_carriers(offer.pickup_location)

        if not carriers:
            return

        data = [
            {
                "user": carrier,
                "type": Notification.Type.NEW_OFFER,
                "title": "New Delivery Nearby",
                "message": f"{offer.code} is available near you",
                "content_object": offer
            }
            for carrier in carriers
        ]

        NotificationService.bulk_create(data)

    # -------------------------
    # 🔔 EVENT: PROPOSAL CREATED
    # -------------------------

    @staticmethod
    def handle_new_proposal(proposal):
        """
        Carrier applied to an offer
        Notify sender
        """

        offer = proposal.offer

        NotificationService.create(
            user=offer.sender,
            type=Notification.Type.NEW_PROPOSAL,
            title="New Delivery Proposal",
            message=f"A carrier applied for {offer.code}",
            content_object=offer
        )

    # -------------------------
    # 🔔 EVENT: PROPOSAL ACCEPTED
    # -------------------------

    @staticmethod
    def handle_proposal_accepted(proposal):
        """
        Sender accepted a carrier
        Notify carrier
        """

        NotificationService.create(
            user=proposal.carrier,
            type=Notification.Type.PROPOSAL_ACCEPTED,
            title="You Got the Job 🎉",
            message=f"You were selected for {proposal.offer.code}",
            content_object=proposal.offer
        )

    @staticmethod
    def handle_offer_accepted(offer):
        """
        Offer accepted (direct or via proposal)
        Notify carrier
        """
        if not offer.carrier:
            return

        NotificationService.create(
            user=offer.carrier,
            type=Notification.Type.PROPOSAL_ACCEPTED,
            title="You Got the Job 🎉",
            message=f"You were selected for {offer.code}",
            content_object=offer
        )
