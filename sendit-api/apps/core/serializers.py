from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .services.media_service import CloudinaryService
from .models import Location, Notification, Media

class MediaSerializer(serializers.ModelSerializer):
    # file = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = Media
        fields = ['id', 'file_url', 'tag', 'order', 'uploaded_at']
        # fields = [
        #     'id',
        #     # 'file',
        #     'file_url',
        #     'media_type',
        #     'tag',
        #     'object_id',
        #     'content_type',
        #     'order'
        # ]
        # read_only_fields = ['file_url']

    # def create(self, validated_data):
    #     file = validated_data.pop('file')

    #     # upload to cloudinary
    #     file_url, public_id = CloudinaryService.upload(file)

    #     return Media.objects.create(
    #         file_url=file_url,
    #         public_id=public_id,
    #         **validated_data
    #     )

    # def update(self, instance, validated_data):
    #     file = validated_data.pop('file', None)

    #     # 🔥 Replace image if new one comes
    #     if file:
    #         if instance.public_id:
    #             CloudinaryService.delete(instance.public_id)

    #         file_url, public_id = CloudinaryService.upload(file)
    #         instance.file_url = file_url
    #         instance.public_id = public_id

    #     return super().update(instance, validated_data)

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
        fields = ['id', 'user', 'type', 'is_read', 'created_at', 'title', 'message', "object_id"]