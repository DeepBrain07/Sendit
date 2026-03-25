from django.urls import path
from .views import InterswitchWebhookView

urlpatterns = [
    path("walletfund/webhook/interswitch/", InterswitchWebhookView.as_view(), name="interswitch-webhook"),
]
