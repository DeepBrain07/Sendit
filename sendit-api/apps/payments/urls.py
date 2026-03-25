from django.urls import path
from .views import InterswitchWebhookView, WebFundingPayloadView

urlpatterns = [
    path("walletfund/webhook/interswitch/", InterswitchWebhookView.as_view(), name="interswitch-webhook"),
    path("wallets/fund/web/create_payload/", WebFundingPayloadView.as_view(), name="create_web_funding_payload"),
]
