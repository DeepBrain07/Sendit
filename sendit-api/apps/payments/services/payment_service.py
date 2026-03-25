from django.conf import settings
from django.core.exceptions import PermissionDenied
import requests
import base64
from apps.payments.models import Transaction
from apps.core.services.notification_service import NotificationService
# from apps.wallets.services.wallet_services import WalletService


class PaymentService:

    @staticmethod
    def get_interswitch_access_token():
        url = f"{settings.INTERSWITCH_BASE_URL}/passport/oauth/token?grant_type=client_credentials"

        # Interswitch usually uses basic auth for token generation
        auth_str = f"{settings.INTERSWITCH_CLIENT_ID}:{settings.INTERSWITCH_CLIENT_SECRET}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {
            "grant_type": "client_credentials",
            "scope": "profile"
        }
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                return response.json().get("access_token")
            return None
        except requests.RequestException as e:
            print(f"Error fetching access token: {e}")
            return None

    @staticmethod
    def initiate_wallet_funding_via_checkout(offer, user):
        """
        fund your wallet through direct payment of user 
        """
        if not user.profile.is_verified:
            raise PermissionDenied("Only verified users can fund wallet")
        
        try:
    
            # Create or get existing transaction
            transaction, created = Transaction.objects.get_or_create(
                offer=offer,
                defaults={
                    "tx_ref": f"ESCROW_{offer.id}_{offer.code}",
                    "amount": offer.total_price,
                    "status": Transaction.Status.INITIATED
                }
            )

            # Call Interswitch to initiate purchase
            url = f"{settings.INTERSWITCH_BASE_URL}/collections/w/pay"

            access_token = PaymentService.get_interswitch_access_token()
            if not access_token:
                raise Exception("Failed to authenticate with payment gateway")

            payload = {
                "amount": int(transaction.amount * 100),  # amount in kobo
                "currency": "NGN",
                "txn_ref": transaction.tx_ref,
                "site_redirect_url": settings.INTERSWITCH_CALLBACK_URL,
                "customer_email": offer.sender.email,
                "customer_mobile": offer.sender.profile.phone_number if hasattr(offer.sender, 'profile') else None,
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                # Interswitch usually returns a redirect URL or a payment token
                return {
                    "transaction": transaction,
                    "payment_url": data.get("payment_url"),
                    "payment_token": data.get("payment_token")
                }
        except Exception as e:
            raise Exception(f"Payment gateway error: {e}")

    @staticmethod
    def handle_payment_success(transaction, payload=None):

        # 🔥 notify
        NotificationService.notify(
            user=transaction.offer.sender,
            type="payment_success",
            title="Payment Successful",
            message=f"Your escrow for {transaction.offer.code} has been funded with {transaction.amount}",
            obj=transaction.offer
        )
