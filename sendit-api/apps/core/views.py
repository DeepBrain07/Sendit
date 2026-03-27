from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action  # Added for custom actions
from apps.core.pagination import NotificationPagination
from apps.core.serializers import (
    NotificationListSerializer, 
    NotificationSerializer, 
    MediaSerializer,
    ChatRoomSerializer,
    MessageSerializer  # Ensure you import your MessageSerializer
)
from .models import Media, Notification, ChatRoom, Message # Added Message model
from .services.cloudinary_service import CloudinaryService


class MediaViewSet(ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.public_id:
            CloudinaryService.delete(instance.public_id)
        instance.delete()


class ChatRoomViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving chat rooms the user is part of.
    """
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Prefetching participants and messages to avoid N+1 queries
        return ChatRoom.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants', 
            'messages'
        ).order_by('-updated_at')

    @action(detail=True, methods=['get'])
    def messages(self, request, id=None):
        """
        Returns the message history for a specific chat room.
        Endpoint: GET /chats/{id}/messages/
        """
        room = self.get_object()
        # Fetch messages for this room, newest first
        messages = room.messages.all().order_by('-timestamp')

        # Check if pagination is needed (optional but recommended)
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True)
        return Response({
            "results": serializer.data
        })


class NotificationListView(ReadOnlyModelViewSet):
    queryset = Notification.objects.all() 
    lookup_field = 'id'
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        unread_count = queryset.filter(is_read=False).count()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "results": serializer.data,
                "unread_count": unread_count
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "results": serializer.data,
            "unread_count": unread_count
        })

    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])

        serializer = self.get_serializer(notification)
        return Response(data={
            "message": "Notification retrieved successfully",
            "notification": serializer.data
        }, status=200)