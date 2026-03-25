from django.urls import path
from .views import InterswitchWebhookView

urlpatterns = [
    path("webhook/", InterswitchWebhookView.as_view(), name="interswitch-webhook"),
]
