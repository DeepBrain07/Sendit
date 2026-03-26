from .models import Offer, Proposal
from  rest_framework import serializers
from apps.core.services.media_service import MediaService
from apps.core.models import Location
from apps.core.serializers import LocationSerializer,MediaSerializer
from apps.account.serializers import UserSerializer
"""
 "location": {
    "city": "Lagos",
    "area": "Lekki",
    "street": "Admiralty Way",
    "latitude": 6.45,
    "longitude": 3.47
  }

PATCH /offers/{id}/steps/details/
PATCH /offers/{id}/steps/location/
PATCH /offers/{id}/steps/pricing/
"""

class OfferCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = []  # empty → system controls creation

    def create(self, validated_data):
        user = self.context["request"].user
        if not user.profile.is_verified:
            raise serializers.ValidationError("User profile is not verified")
        if not user.profile.type == "sender":
            raise serializers.ValidationError("User profile is not a sender")

        return Offer.objects.create(
            sender=user,
            status=Offer.Status.DRAFT,
            current_step=Offer.Step.DETAILS
        )

class OfferDetailsSerializer(serializers.ModelSerializer):
    # image = serializers.ListField(
    #     child=serializers.ImageField(max_length=None, use_url=True),
    #     required=False
    # )
    image = serializers.ImageField(required=False)
    class Meta:
        model = Offer
        fields = ["package_type", "is_fragile", "description", "image"]


class OfferLocationSerializer(serializers.ModelSerializer):
    # write only serializers
    # Write-only accepts dict
    pickup_location = serializers.JSONField(write_only=True, required=False)
    delivery_location = serializers.JSONField(write_only=True, required=False)
   
    # # Nested read-only for API output
    pickup_location_detail = LocationSerializer(source="pickup_location", read_only=True)
    delivery_location_detail = LocationSerializer(source="delivery_location", read_only=True)

    class Meta:
        model = Offer
        fields = ["id","pickup_location", "delivery_location","pickup_location_detail", "delivery_location_detail","receiver_name", "receiver_phone"]


    def update(self, instance, validated_data):
        pickup_location = validated_data.pop("pickup_location", None)
        if pickup_location:
            instance.pickup_location = Location.objects.create(**pickup_location)
        delivery_location = validated_data.pop("delivery_location", None)
        if delivery_location:
            instance.delivery_location = Location.objects.create(**delivery_location)

class OfferPricingSerializer(serializers.ModelSerializer):
    '''used as review serializer also'''

    class Meta:
        model = Offer
        fields = ["base_price", "is_urgent","total_price", "platform_fee","urgent_fee"]
        read_only = ["total_price", "platform_fee","urgent_fee"]



class OfferTransitionSerializer(serializers.Serializer):
    """Track final offer step to start offer status"""
    action = serializers.ChoiceField(choices=[
        Offer.Status.POSTED,
        Offer.Status.ACCEPTED,
        Offer.Status.IN_TRANSIT,
        Offer.Status.DELIVERED,
        Offer.Status.CANCELLED,
    ])


class OfferListSerializer(serializers.ModelSerializer):

    pickup_location = LocationSerializer()
    delivery_location = LocationSerializer()

    class Meta:
        model = Offer
        fields = [
            "id",
            "code",
            "package_type",
            "is_fragile",
            "pickup_location",
            "delivery_location",
            "base_price",
            "is_urgent",
            "urgent_fee",

            "platform_fee",
            "total_price",
            'receiver_name',
            'receiver_phone',
            "status",
        ]



class OfferSerializer(serializers.ModelSerializer):

    # pickup_location = LocationSerializer()
    # delivery_location = LocationSerializer()
    location = OfferLocationSerializer(source="*", read_only=True)
    details = OfferDetailsSerializer(source="*", read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    pricing = serializers.SerializerMethodField(read_only=True)
    sender_detail = serializers.SerializerMethodField(read_only=True)
    carrier_detail = serializers.SerializerMethodField(read_only=True, allow_null=True)

    def get_pricing(self, obj):
        pricing  = OfferPricingSerializer(obj).data
        pricing["base_price"] = obj.base_price
        return pricing

    class Meta:
        model = Offer
        #all field on model with the custom
        fields = [
            "id",
            "code",
            "package_type",
            "is_fragile",
            "description",
            "image",
            "details",
            "location",
            "pricing",
            "status",
            "current_step",
            "sender_detail",
            "carrier_detail",
        ]

    def get_image(self, obj):
        image = obj.image
        return MediaSerializer(image).data if image else None
    
    def get_sender_detail(self, obj):
        from apps.account.serializers import ProfileSerializer
        return ProfileSerializer(obj.sender.profile).data
    
    def get_carrier_detail(self, obj):
        from apps.account.serializers import ProfileSerializer
        if obj.carrier:
            return ProfileSerializer(obj.carrier.profile).data
        return None



class OfferUpdateSerializer(serializers.ModelSerializer):
    pickup_location = serializers.JSONField(write_only=True)
    delivery_location = serializers.JSONField(write_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Offer
        fields = [
            "package_type", "is_fragile", "description", "image",
            "pickup_location", "delivery_location",
            "receiver_name", "receiver_phone",
            "base_price", "is_urgent"
        ]

    def update(self, instance, validated_data):
        pickup_location = validated_data.pop("pickup_location", None)
        delivery_location = validated_data.pop("delivery_location", None)
        
        if pickup_location:
            instance.pickup_location = Location.objects.create(**pickup_location)
        if delivery_location:
            instance.delivery_location = Location.objects.create(**delivery_location)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ProposalSerializer(serializers.ModelSerializer):
    # we need to import it here to avoid circular imports
    carrier_detail = serializers.SerializerMethodField(read_only=True)
    sender_detail = serializers.SerializerMethodField(read_only=True)
    offer_detail = serializers.SerializerMethodField(source="offer",read_only=True)

    class Meta:
        model = Proposal
        fields = ["id", "offer", "offer_detail", "carrier", "sender_detail","carrier_detail", "price", "message", "status"]
        read_only_fields = ["id", "carrier", "status"]

    def get_carrier_detail(self, obj):
        from apps.account.serializers import ProfileSerializer
        return ProfileSerializer(obj.carrier.profile).data
    
    def get_sender_detail(self, obj):
        from apps.account.serializers import ProfileSerializer
        return ProfileSerializer(obj.sender.profile).data
    
    def get_offer_detail(self, obj):
        return OfferSerializer(obj.offer).data
    
    

    def validate(self, attrs):
        user = self.context["request"].user
        offer = attrs["offer"]

        # ✅ Ensure user is a carrier
        if getattr(user.profile, "type", None) != "carrier":
            raise serializers.ValidationError(
                "Only carriers can submit proposals.")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return Proposal.objects.create(
            carrier=user,
            **validated_data
        )


class ProposalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ["status"]
        read_only_fields = ["status"]

    def validate(self, attrs):
        # Additional validation can be added here if needed
        return attrs


