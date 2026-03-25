# views.py
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from apps.account.serializers import UserSerializer, GoogleLoginSerializer
from apps.account.documentation.account.schemas import google_login_doc, google_auth_config_doc
from apps.account.utils import send_login_or_logout_email
from apps.wallets.services.wallet_services import WalletService


User = get_user_model()

@google_login_doc
class GoogleLogin(APIView):
    serializer_class = GoogleLoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'
    """
    Google Login View
    Endpoint: /google/login/
    Method: POST
    Request Body:
        {
            "id_token": "string"

        }
    Response:
     
        {
            'status': 'Success',
            'message': 'Authenticated successfully!',
            'data': {
            "id":"uuid","first_name":"string","last_name":"string","email":"string"},
            'token': {
                "access_token": "jwt-access-token",
                "refresh_token": "jwt-refresh-token",
            }
    
    """
    def post(self, request):
        id_token_str = request.data.get("id_token") or request.data.get("code")
        if not id_token_str:
            return Response({"error": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify token with Google
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            email = idinfo.get("email")
            name = idinfo.get("name")
            # picture = idinfo.get("picture")
            if not email:
                return Response({"error": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "email": email,
                "first_name": name.split(" ")[0] if name else "",
                "last_name": " ".join(name.split(" ")[1:]) if name else "",
            }
        )

        if created:
            user.set_unusable_password()
            user.is_active = True
            user.save()
            user.create_profile()
            WalletService.create_wallet_account(user)
        send_login_or_logout_email(user, request,'login')


        # Issue JWT
        data = {
                'status': 'Success',
                'message': 'Authenticated successfully!',
                'data': UserSerializer(user).data,
                'token': user.get_jwt_tokens
            }
        return Response(data = data, status=status.HTTP_201_CREATED)

@google_auth_config_doc
class GoogleAuthConfig(APIView):
    def get(self, request):
        return Response({
            'client_id': settings.GOOGLE_CLIENT_ID,
        }, status=status.HTTP_200_OK)
