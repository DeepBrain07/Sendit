import random
import string
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal

# Initialize the manual generator
fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'account.CustomUser'

    email = factory.Sequence(lambda n: f"user{n}@sendit.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    agree_to_privacy_policy = True

class Command(BaseCommand):
    help = "Seeds the Sendit database with Users, Profiles, Wallets, and Ledger Entries."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # 1. Lazy Imports
        from django.contrib.auth import get_user_model
        from apps.account.models import Profile, Verification
        from apps.offers.models import Offer
        from apps.wallets.models import Wallet, WalletLedgerEntry
        from apps.payments.models import Transaction
        from apps.core.models import Location
        
        User = get_user_model()
        SEED_PASSWORD = "Sendit_Secure_Auth_2026!"

        self.stdout.write(self.style.MIGRATE_LABEL("--- Starting Seeding Process ---"))

        # 2. Definitions
        PROTECTED_EMAILS = [
            "heritage@example.com", 
            "olusatimmie07@gmail.com",
            "deepbrain77@gmail.com"
        ]

        # 3. Cleanup non-protected data
        self.stdout.write("Cleaning up old non-protected data...")
        try:
            # We delete everything NOT in protected list
            Transaction.objects.exclude(wallet__user__email__in=PROTECTED_EMAILS).delete()
            WalletLedgerEntry.objects.exclude(wallet__user__email__in=PROTECTED_EMAILS).delete()
            Offer.objects.exclude(sender__email__in=PROTECTED_EMAILS).delete()
            User.objects.filter(is_superuser=False).exclude(email__in=PROTECTED_EMAILS).delete()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Cleanup partially skipped: {e}"))

        # 4. Create Locations
        self.stdout.write("Setting up locations...")
        locations = []
        city_list = ["Lagos", "Abuja", "Port Harcourt", "Ibadan"]
        
        for city_name in city_list:
            # Look for ANY existing entry with this city name
            loc = Location.objects.filter(city=city_name).first()
            
            if not loc:
                # Only create if it truly doesn't exist
                loc = Location.objects.create(city=city_name, area="General")
                self.stdout.write(f"Created new location: {city_name}")
            else:
                self.stdout.write(f"Using existing location: {city_name}")
                
            locations.append(loc)
            
        # 5. Helper Function to Seed Wallet & History
        def seed_user_financials(user):
            # Ensure Wallet exists
            wallet, _ = Wallet.objects.get_or_create(
                user=user,
                defaults={
                    'balance': Decimal("0.00"),
                    'virtual_account_name': f"SENDIT-{user.first_name.upper()}",
                    'virtual_account_number': "".join([str(random.randint(0, 9)) for _ in range(10)]),
                    'virtual_account_bank_number': "WEMA BANK"
                }
            )

            # Clear old entries for this specific user to avoid bloat
            wallet.ledger_entries.all().delete()
            wallet.balance = Decimal("0.00")
            wallet.save()

            # Add Credits (This triggers the WalletLedgerEntry via your model method)
            for _ in range(random.randint(3, 5)):
                amount = Decimal(random.randint(5000, 15000))
                wallet.credit(amount, note="Wallet Top-up")
                
                # Create a matching Transaction for the UI
                tx_ref = f"TXN-{timezone.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=6))}"
                Transaction.objects.create(
                    wallet=wallet,
                    tx_ref=tx_ref,
                    amount=amount,
                    status="success", # Matches your model status
                    verified=True
                )
            
            # Refresh to ensure the instance in memory sees the balance added by the credit method
            wallet.refresh_from_db()
            self.stdout.write(f"Wallet for {user.email} seeded. Balance: ₦{wallet.balance}")

        # 6. Seed Protected Users
        for email in PROTECTED_EMAILS:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'first_name': 'Dev', 'last_name': 'User', 'is_active': True}
            )
            if created:
                user.set_password(SEED_PASSWORD)
                user.save()
            
            seed_user_financials(user)

        # 7. Seed 10 Random Users
        for i in range(10):
            user = UserFactory()
            user.set_password(SEED_PASSWORD)
            user.save()
            seed_user_financials(user)

        self.stdout.write(self.style.SUCCESS("\n✅ Seeded successfully. All wallets now have balances."))