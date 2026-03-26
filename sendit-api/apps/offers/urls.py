from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"proposals", views.ProposalViewSet, basename="proposal")

urlpatterns = [

    # 🟢 lISTT/ CREATE OFFER (entry point)
    path("", views.OfferListCreateView.as_view(), name="offer-list-create"),

    # 🔍 SINGLE OFFER
    path("<uuid:pk>/", views.OfferView.as_view(), name="offer-detail"),

       # 🧱 Steps
    path("<uuid:pk>/details/", views.OfferDetailsView.as_view(), name="offer-details"),
    path("<uuid:pk>/location/", views.OfferLocationView.as_view(), name="offer-location"),
    path("<uuid:pk>/pricing/", views.OfferPricingView.as_view(), name="offer-pricing"),

    # 👀 REVIEW (read-only)
    path("<uuid:pk>/review/", views.OfferReviewView.as_view(), name="offer-review"),

    # 🔁 TRANSITIONS (state changes)
    path("<uuid:pk>/transition/", views.OfferTransitionView.as_view(), name="offer-transition"),

    # 💰 CHECKOUT
    path("<uuid:pk>/checkout/", views.OfferCheckoutView.as_view(), name="offer-checkout"),

    path("", include(router.urls)),
]
