# wallets/serializers.py
from rest_framework import serializers
# from .models import Wallet, Transaction, WalletLedgerEntry
from django.contrib.auth import get_user_model

User = get_user_model()

class WebFundingPayloadSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

