import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker # Standard faker for manual loops
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal

# Initialize the manual generator
fake = Faker()

# --- Factories using String References (Registry Safe) ---

class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'account.CustomUser'

    email = factory.Sequence(lambda n: f"user{n}@sendit.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    agree_to_privacy_policy = True

class Command(BaseCommand):
    help = "Seeds the Sendit database with Users, Profiles, and related data."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # 1. Lazy Imports: This prevents the 'AppRegistryNotReady' error
        from django.contrib.auth import get_user_model
        from apps.account.models import Profile, Verification
        from apps.offers.models import Offer
        from apps.wallets.models import Wallet
        from apps.core.models import Location
        
        User = get_user_model()
        SEED_PASSWORD = "Sendit_Secure_Auth_2026!"

        self.stdout.write(self.style.MIGRATE_LABEL("--- Starting Seeding Process ---"))

        # 2. Cleanup existing data
        self.stdout.write("Cleaning up old non-admin data...")
        try:
            Offer.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Cleanup partially skipped: {e}"))

        # 3. Create Superuser
        if not User.objects.filter(email="admin@sendit.com").exists():
            User.objects.create_superuser(
                email="admin@sendit.com",
                password=SEED_PASSWORD,
                first_name="Admin",
                last_name="Super"
            )
            self.stdout.write(self.style.SUCCESS("Created Admin: admin@sendit.com"))

        # 4. Create/Get Locations (Duplicate-Safe)
        self.stdout.write("Setting up locations...")
        locations = []
        for city_name in ["Lagos", "Abuja", "Port Harcourt", "Ibadan"]:
            loc = Location.objects.filter(city=city_name).first()
            if not loc:
                loc = Location.objects.create(city=city_name, area="General")
            locations.append(loc)

        # 5. Create Test Users
        self.stdout.write("Creating 10 test users and profiles...")
        user_types = ['sender', 'carrier']
        
        for i in range(10):
            user = UserFactory()
            user.set_password(SEED_PASSWORD)
            user.save()

            # Lifecycle hooks may have created the profile, so use get_or_create
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.type = random.choice(user_types)
            profile.phone_number = f"080{random.randint(10000000, 99999999)}"
            profile.is_new_user = False 
            profile.location = random.choice(locations)
            profile.save()

            # 6. Initialize Wallets
            Wallet.objects.get_or_create(user=user, defaults={'balance': 10000.00})

            # 7. Add Verifications
            if i % 3 == 0:
                Verification.objects.create(
                    profile=profile,
                    verification_type='nin',
                    id_number=str(random.randint(10000000000, 99999999999)),
                    is_verified=True,
                    verified_at=timezone.now()
                )

        # 8. Create Offers
        self.stdout.write("Creating sample offers...")
        all_users = User.objects.filter(is_superuser=False)
        
        # We need at least two locations for pickup and delivery
        if len(locations) < 2:
            self.stdout.write(self.style.ERROR("Not enough locations to create offers."))
            return

        for _ in range(15):
            sender = random.choice(all_users)
            
            # Select two different locations
            pickup = random.choice(locations)
            delivery = random.choice([loc for loc in locations if loc != pickup])

            try:
                Offer.objects.create(
                    sender=sender,
                    package_type=random.choice(['small', 'medium', 'large']),
                    description=fake.paragraph(nb_sentences=2),
                    pickup_location=pickup,
                    delivery_location=delivery,
                    receiver_name=fake.name(),
                    receiver_phone=f"090{random.randint(10000000, 99999999)}",
                    base_price=Decimal(random.randint(2000, 15000)),
                    is_urgent=random.choice([True, False]),
                    status='posted',
                    current_step='posted'
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipped an offer: {e}"))

        self.stdout.write(self.style.SUCCESS("\n✅ Seeding complete!"))