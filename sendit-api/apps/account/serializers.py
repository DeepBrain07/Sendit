from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.core.services.media_service import MediaService
from apps.core.serializers import MediaSerializer, LocationSerializer
from apps.core.models import Location
from .models import Profile, Verification

User = get_user_model()

# --- Auth Serializers ---

class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

class PasswordResetSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        try:
            validate_password(password=attrs['new_password'])
        except Exception as e:
            raise serializers.ValidationError(f"Password error: {e}")
        return attrs

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(max_length=30, write_only=True)
    confirm_password = serializers.CharField(max_length=30, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'agree_to_privacy_policy', 'password', 'confirm_password',)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        try:
            validate_password(attrs.get('password'))
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        attrs.pop('confirm_password', None)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(is_active=False, **validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=30, write_only=True)

    def validate(self, attrs):
        email, password = attrs.get('email'), attrs.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            return attrs
        raise serializers.ValidationError('Invalid Email or password!')

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class PhoneOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    otp = serializers.CharField(max_length=6)

class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()

# --- Profile Serializer ---

class ProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, write_only=True)
    id = serializers.UUIDField(source='user_id', read_only=True)
    age = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    location = serializers.JSONField(write_only=True, required=False)
    location_details = LocationSerializer(source="location", read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'email', 'first_name', 'type', "image", 'avatar', 'last_name', 'date_of_birth', 'age', 'is_new_user',
                  'gender', 'bio', 'phone_number', 'phone_verified', "location_details", "location", 'created_at', 'updated_at')
        read_only_fields = ["phone_verified", "is_verified", "email", "is_new_user"]

    def get_age(self, instance) -> int:
        return instance.get_age()

    def get_avatar(self, obj):
        avatar = obj.avatar
        return MediaSerializer(avatar).data if avatar else None

    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)
        location_data = validated_data.pop("location", None)

        if image is not None:
            # Use .pk here as well to be safe, though 
            # fixing the MediaService is the root cure.
            MediaService.attach_file(image, instance, tag="avatar")

        # Update location logic...
        if location_data is not None:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)

        # Standard DRF update logic
        return super().update(instance, validated_data)
# --- Verification Serializers ---

class VerificationSerializer(serializers.ModelSerializer):
    document = serializers.FileField(write_only=True, required=False)
    selfie = serializers.ImageField(write_only=True, required=False)
    documents = serializers.SerializerMethodField(read_only=True)
    selfie_image = serializers.SerializerMethodField(read_only=True)
    verification_id = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Verification
        fields = [
            'verification_id', 'profile', 'verification_type', 'id_number',
            'document', "documents", 'selfie', "selfie_image",
            'is_verified', 'note', 'verified_by', 'verified_at'
        ]
        read_only_fields = ['is_verified', 'note', 'verified_by', 'verified_at', 'profile']

    def get_documents(self, obj):
        return MediaSerializer(obj.documents, many=True).data

    def get_verification_id(self, obj):
        return obj.id 

    def get_selfie_image(self, obj):
        media = obj.selfie_image
        return MediaSerializer(media).data if media else None

    def create(self, validated_data):
        document = validated_data.pop('document', None)
        selfie = validated_data.pop('selfie', None)
        profile = self.context['request'].user.profile

        if Verification.objects.filter(profile=profile, is_verified=False).exists():
            raise serializers.ValidationError("You already have a pending verification")

        verification = Verification.objects.create(profile=profile, **validated_data)

        if document:
            # FIX: Using .pk
            MediaService.attach_file(document, verification, tag='document')
        else:
            raise serializers.ValidationError({"document": "This field is required."})

        if selfie:
            # FIX: Using .pk
            MediaService.attach_file(selfie, verification, tag='selfie')
        else:
            raise serializers.ValidationError({"selfie": "This field is required."})

        return verification
    
    def update(self, instance, validated_data):
        document_file = validated_data.pop('document', None)
        selfie_file = validated_data.pop('selfie', None)

        instance = super().update(instance, validated_data)

        if document_file:
            MediaService.attach_file(document_file, instance, tag='document')
        if selfie_file:
            MediaService.attach_file(selfie_file, instance, tag='selfie')

        return instance

class ReviewVerificationSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(required=True)
    class Meta:
        model = Verification
        fields = ['is_verified', 'note']

    def validate(self, attrs):
        if attrs.get('is_verified') is False and not attrs.get('note', '').strip():
            raise serializers.ValidationError({'note': 'You must provide a note when un-verifying.'})
        return attrs