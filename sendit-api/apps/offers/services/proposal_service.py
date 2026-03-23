from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.offers.models import Offer, Proposal
from apps.escrow.models import Escrow
from .offer_service import OfferService

class ProposalService:
    @staticmethod
    @transaction.atomic
    def create_proposal(offer: Offer, carrier, price, message=""):
        """
        Carrier bids for an offer.
        Initial status: PENDING
        """
        # Check if the user is a carrier
        if getattr(carrier.profile, "type", None) != "carrier":
            raise ValidationError("Only carriers can bid for offers")
        
        # Check if user is verified
        if not carrier.profile.is_verified:
            raise ValidationError("Your profile must be verified to bid")

        # Check if offer is posted
        if offer.status != Offer.Status.POSTED:
            raise ValidationError("This offer is no longer accepting proposals")

        # Check if carrier already bid
        if Proposal.objects.filter(offer=offer, carrier=carrier).exists():
            raise ValidationError("You have already submitted a proposal for this offer")

        proposal = Proposal.objects.create(
            offer=offer,
            carrier=carrier,
            price=price,
            message=message,
            status=Proposal.Status.PENDING
        )

        # Notify sender
        OfferService.handle_new_proposal(proposal)
        return proposal

    @staticmethod
    @transaction.atomic
    def accept_proposal(proposal: Proposal, user):
        """
        Sender accepts a carrier's proposal.
        - Selected proposal -> ACCEPTED
        - Other proposals -> REJECTED
        - Offer -> ACCEPTED and carrier attached
        - Escrow status -> LOCKED (funds are now tied to this specific carrier)
        """
        # Check if the user is the sender of the offer
        if proposal.offer.sender != user:
            raise ValidationError("You are not authorized to accept this proposal")

        # Check if the offer's escrow is funded
        try:
            escrow = proposal.offer.escrow
            if escrow.status != Escrow.Status.FUNDED:
                raise ValidationError("You must fund the offer before accepting a proposal")
        except Escrow.DoesNotExist:
            raise ValidationError("No escrow found for this offer. Please fund the offer first.")

        # Check if the offer is already accepted
        if proposal.offer.status == Offer.Status.ACCEPTED:
             raise ValidationError("This offer has already been accepted")

        # Update proposal status
        proposal.status = Proposal.Status.ACCEPTED
        proposal.save()

        # Update other proposals to rejected
        Proposal.objects.filter(offer=proposal.offer).exclude(id=proposal.id).update(
            status=Proposal.Status.REJECTED
        )

        # Update offer
        offer = proposal.offer
        offer.carrier = proposal.carrier
        offer.status = Offer.Status.ACCEPTED
        offer.save()

        # Lock escrow to this transaction/carrier
        escrow.lock()

        # Notify carrier
        OfferService.handle_proposal_accepted(proposal)
        return proposal
