
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied,  ValidationError


from .models import Offer
from .services.step_service import OfferStepService
from apps.offers.services.offer_service import OfferService
from apps.offers.services.status_service import OfferStatusService
from .serializers import  (OfferCreateSerializer, OfferListSerializer,
OfferDetailsSerializer,OfferLocationSerializer,OfferPricingSerializer, 
OfferTransitionSerializer,OfferSerializer)
from .documentation.offers.schemas import (offer_list_create_doc, offer_step_details_doc, offer_location_doc, 
                                           offer_pricing_doc, offer_review_doc, offer_transition_doc, offer_detail_doc)

@offer_list_create_doc
class OfferListCreateView(ListCreateAPIView):
    """
    offers/?mine=true
    """
    # queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OfferCreateSerializer
        return OfferListSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def get_queryset(self):
        
        queryset = Offer.objects.select_related(
            "sender",
            "carrier",
            "pickup_location",
            "delivery_location",
        ).prefetch_related(
            "media",
        )
        params = self.request.query_params
        print(f"[offer list] queryset: {queryset}, params: {params}")

         # 1. Robust Boolean Check
        mine = str(params.get("mine", "")).lower() in ["1", "true", "yes"]
        
        if mine:
            # User wants their own offers (regardless of status)
            queryset = queryset.filter(sender=self.request.user)
        else:
            # Marketplace view: only show public/posted offers 
            # AND exclude the user's own offers so they don't see themselves in the market
            queryset = queryset.filter(status=Offer.Status.POSTED).exclude(sender=self.request.user)
 
        # -------------------------------
        # Filter: urgent
        # -------------------------------
        urgent = params.get("urgent")
        if urgent is not None:
            if urgent.lower() in ["1", "true", "yes"]:
                queryset = queryset.filter(is_urgent=True)
            elif urgent.lower() in ["0", "false", "no"]:
                queryset = queryset.filter(is_urgent=False)

        # -------------------------------
        # Filter: price range
        # -------------------------------
        min_price = params.get("min_price")
        max_price = params.get("max_price")

        if min_price:
            try:
                queryset = queryset.filter(total_price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                queryset = queryset.filter(total_price__lte=float(max_price))
            except ValueError:
                pass

        # -------------------------------
        # Filter: today
        # -------------------------------
        today = params.get("today")
        if today and today.lower() in ["1", "true", "yes"]:
            start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            queryset = queryset.filter(created_at__range=(start, end))

        # -------------------------------
        # Filter: city or area
        # -------------------------------
        city_or_area = params.get("city_or_area")
        if city_or_area:
            queryset = queryset.filter(
                Q(pickup_location__city__icontains=city_or_area) |
                Q(pickup_location__area__icontains=city_or_area) |
                Q(delivery_location__city__icontains=city_or_area) |
                Q(delivery_location__area__icontains=city_or_area)
            )

        # -------------------------------
        # Filter: nearby (chained)
        # -------------------------------
        lat = params.get("lat")
        lng = params.get("lng")
        radius = params.get("radius", 10)  # default 10 km

        if lat and lng:
            try:
                user_location = OfferService.create_temp_location(float(lat), float(lng))
                queryset = OfferService.get_nearby_offers(offers=queryset, user_location=self.request.user.profile.location, radius_km=float(radius) if radius else 10)
            except ValueError:
                pass

        return queryset.order_by("-created_at")

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        print(f"[offer list] queryset: {queryset}")

        if not queryset.exists():
            return Response({
                "count": 0,
                "message": "No offers match found",
                "offers": []
            }, status=200)

        # Use serializer with many=True
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "count": queryset.count(),
            "offers": serializer.data
        }, status=200)

    def create(self, request, *args, **kwargs):
        """Create a new offer"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            offer = serializer.save()

            return Response({
                "success": True,
                "message": "STEP_CREATE_SUCCESS",
                "data": {
                    "id": offer.id,
                    "status": offer.status,
                    "current_step": offer.current_step
                }
            })

        except ValidationError as e:
            return Response({
                "success": False,
                "error": {
                    "code": "STEP_VALIDATION_FAILED",
                    "message": str(e)
                }
            }, status=400)

class BaseOfferStepView(APIView):
    permission_classes = [IsAuthenticated]

    step = None
    serializer_class = None

    def get(self, request, pk):
        """Return the serializer fields for browsable form"""
        offer = get_object_or_404(Offer, pk=pk)
        serializer = self.serializer_class(instance=offer)
        return Response(serializer.data)

    def patch(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        serializer = self.serializer_class(instance=offer,data=request.data,partial=True,context={"request": request})
        serializer.is_valid(raise_exception=True)

        try:
            print(f"[base step] step: {self.step} id{offer.id}, status{offer.current_step}")
            offer = OfferStepService.update_step(
                offer=offer,
                step=self.step,
                data=serializer.validated_data,
                user=request.user
            )

            return Response({
                "success": True,
                "message": "STEP_UPDATE_SUCCESS",
                "data": {
                    "id": offer.id,
                    "status": offer.status,
                    "current_step": offer.current_step
                }
            })

        except ValidationError as e:
            return Response({
                "success": False,
                "error": {
                    "code": "STEP_VALIDATION_FAILED",
                    "message": str(e)
                }
            }, status=400)

@offer_step_details_doc
class OfferDetailsView(BaseOfferStepView):
    step = Offer.Step.DETAILS
    serializer_class = OfferDetailsSerializer

@offer_location_doc
class OfferLocationView(BaseOfferStepView):
    step = Offer.Step.LOCATION
    serializer_class = OfferLocationSerializer

@offer_pricing_doc
class OfferPricingView(BaseOfferStepView):
    step = Offer.Step.PRICING
    serializer_class = OfferPricingSerializer

@offer_review_doc
class OfferReviewView(APIView):
    """offer review"""
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        if offer.sender != request.user:
            raise PermissionDenied()

        serializer = OfferListSerializer(offer)

        return Response({
            "success": True,
            "data": serializer.data
        })

@offer_transition_doc
class OfferTransitionView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        serializer = OfferTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            OfferStatusService.transition(
              offer=offer,
              action=str(serializer.validated_data["action"]).lower().strip(),
              user=request.user
            )

            return Response({
              "success": True,
              "message":"OFFER STATUS UPDATE SUCCESS",
              "data": {
                  "id": offer.id,
                  "status": offer.status,
                  "current_step": offer.current_step
              }
          },status=200)

        except Exception as e:
            return Response({
                "error": True,
                "message": str(e)
            }, status=400)

@offer_detail_doc
class OfferView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)

        serializer = OfferSerializer(offer)

        return Response({
            "success": True,
            "data": serializer.data
        })
