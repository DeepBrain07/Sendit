from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Location, Notification, Media, Message, ChatRoom

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'avatar']

    def get_avatar(self, obj):
        try:
            profile = getattr(obj, 'profile', None)
            if profile:
                avatar_media = profile.avatar 
                if avatar_media:
                    return avatar_media.file_url
        except Exception:
            pass
        return None

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file_url', 'tag', 'order', 'uploaded_at']

class MessageSerializer(serializers.ModelSerializer):
    # Updated to use email since username is None in your CustomUser
    sender_name = serializers.ReadOnlyField(source='sender.first_name')

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'sender_name', 'text', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 
            'participants', 
            'last_message', 
            'unread_count', 
            'updated_at', 
            'offer_id'
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            # Safely use email here as well
            return {
                'text': last_msg.text,
                'sender': last_msg.sender.email if last_msg.sender else "System",
                'timestamp': last_msg.timestamp
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'area', 'street', 'landmark', 'latitude', 'longitude']

class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', "title",'is_read', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'is_read', 'created_at', 'title', 'message']