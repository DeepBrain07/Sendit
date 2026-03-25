from rest_framework import serializers
from apps.payouts.models import Payout

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = "__all__"
        read_only_fields = ["id", "status", "reference", "created_at"]
