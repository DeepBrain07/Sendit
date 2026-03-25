from django.db.models import Sum, Case, When, DecimalField
from django.conf import settings
import requests
from apps.wallets.models import Wallet
from apps.payments.services.payment_service import PaymentService
from apps.escrow.models import Escrow

import logging

logger = logging.getLogger(__name__)


class WalletService:
    @staticmethod
    def create_wallet_account(user):
        # Check if wallet exists
        """
        Provider	Value
        9 Payment Service Bank	9PSB
        WEMA Bank	WEMA
        Fidelity Bank	FBP
        """

        wallet, created = Wallet.objects.get_or_create(user=user)
        if wallet.virtual_account_number:
            return wallet  # already created

        try:
            access_token = PaymentService.get_interswitch_access_token()
            if not access_token:
                raise Exception("Failed to authenticate with Interswitch")

            payload = {
                "accountName": f"{user.full_name}",
                "merchantCode": settings.INTERSWITCH_MERCHANT_CODE,
                "provider": "WEMA"
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                f"{settings.INTERSWITCH_BASE_URL}/paymentgateway/api/v1/payable/virtualaccount",
                json=payload,
                headers=headers
            )
            logger.info(f"[wallet create response] {response.json()}")

            if response.status_code in [200, 201]:
                data = response.json()
                wallet.virtual_account_name = data["accountName"]
                wallet.virtual_account_number = data["accountNumber"]
                wallet.virtual_account_bank_number = data["bankName"]
                wallet.provider = data["bankCode"]
                wallet.balance = 0
                wallet.save()
                return wallet

        except requests.RequestException as e:
            logging.error(f"[wallet create error] {e}")
            raise Exception(f"Failed to create virtual account: {e}")

    @staticmethod
    def get_breakdown(user):

        data = Escrow.objects.filter(
            offer__carrier=user
        ).aggregate(
            locked=Sum(
                Case(
                    When(status="locked", then="amount"),
                    output_field=DecimalField()
                )
            ),
            available=Sum(
                Case(
                    When(status="release_ready", then="amount"),
                    output_field=DecimalField()
                )
            ),
            total_earned=Sum(
                Case(
                    When(status="released", then="amount"),
                    output_field=DecimalField()
                )
            ),
        )

        return {
            "wallet_balance": user.wallet.balance,
            "locked": data["locked"] or 0,
            "release_ready": data["available"] or 0,
            "total_earned": data["total_earned"] or 0,
        }

    @staticmethod
    def get_full_history(wallet):

        ledger_qs = wallet.ledger_entries.all().values(
            "id",
            "amount",
            "entry_type",
            "note",
            "created_at"
        )

        tx_qs = wallet.transactions.all().values(
            "id",
            "amount",
            "status",
            "tx_ref",
            "created_at"
        )

        # Normalize both
        ledger_data = [
            {
                "id": item["id"],
                "type": "ledger",
                "sub_type": item["entry_type"],
                "amount": item["amount"],
                "note": item["note"],
                "status": "completed",
                "created_at": item["created_at"],
            }
            for item in ledger_qs
        ]

        tx_data = [
            {
                "id": item["id"],
                "type": "transaction",
                "sub_type": "funding",
                "amount": item["amount"],
                "note": item["tx_ref"],
                "status": item["status"],  # initiated, failed, success
                "created_at": item["created_at"],
            }
            for item in tx_qs
        ]

        combined = ledger_data + tx_data

        return sorted(
            combined,
            key=lambda x: x["created_at"],
            reverse=True
        )
