from django.conf import settings
import requests
from apps.wallets.models import Wallet
from apps.payments.services.payment_service import PaymentService

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
              "provider":"WEMA"
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

