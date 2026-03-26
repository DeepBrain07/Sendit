import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.auth import exceptions as google_exceptions # Add this
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt # Use exempt for login
from apps.account.utils import set_auth_cookies 
from apps.account.serializers import UserSerializer, GoogleLoginSerializer
from apps.account.documentation.account.schemas import google_login_doc, google_auth_config_doc
from apps.account.utils import send_login_or_logout_email

User = get_user_model()

@google_login_doc
@method_decorator(csrf_exempt, name='dispatch') # Ensure CSRF doesn't block the login
class GoogleLogin(APIView):
    serializer_class = GoogleLoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        token_str = request.data.get("id_token") or request.data.get("access_token")
        
        if not token_str:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        idinfo = None

        # 1. Attempt to verify as ID Token (JWT)
        # Check if it looks like a JWT (contains dots) to avoid MalformedError
        if isinstance(token_str, str) and token_str.count('.') == 2:
            try:
                idinfo = id_token.verify_oauth2_token(
                    token_str,
                    google_requests.Request(),
                    settings.GOOGLE_CLIENT_ID
                )
            except (ValueError, google_exceptions.GoogleAuthError):
                pass # Fall through to access_token check

        # 2. Fallback: Verify as Access Token
        if not idinfo:
            try:
                user_info_res = requests.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    params={'access_token': token_str},
                    timeout=5 # Add timeout to prevent protocol hanging
                )
                if user_info_res.status_code == 200:
                    idinfo = user_info_res.json()
                else:
                    return Response(
                        {"error": "Invalid Google token or expired"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except requests.exceptions.RequestException:
                return Response(
                    {"error": "Failed to connect to Google services"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        email = idinfo.get("email")
        # Google returns 'given_name' and 'family_name' in userinfo, 
        # but 'name' is common in both.
        name = idinfo.get("name") or f"{idinfo.get('given_name', '')} {idinfo.get('family_name', '')}".strip()

        if not email:
            return Response({"error": "Email not found in Google profile"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": idinfo.get('given_name') or (name.split(" ")[0] if name else ""),
                "last_name": idinfo.get('family_name') or (" ".join(name.split(" ")[1:]) if name else ""),
                "is_active": True
            }
        )

        if created:
            user.set_unusable_password()
            user.save()
            # Explicitly trigger profile creation if not handled by hooks
            if hasattr(user, 'create_profile'):
                user.create_profile()
        
        send_login_or_logout_email(user, request, 'login')

        # 4. Generate Tokens
        tokens = user.get_jwt_tokens 
        
        # Check if tokens is a Response object (from your model property error handling)
        if isinstance(tokens, Response):
            return tokens

        data = {
            'status': 'Success',
            'message': 'Authenticated successfully!',
            'data': UserSerializer(user).data,
            'token': tokens
        }
        
        response = Response(data=data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return set_auth_cookies(response, tokens)
    
@google_auth_config_doc
class GoogleAuthConfig(APIView):
    """
    Returns the Google Client ID for the frontend to initialize the OAuth provider.
    """
    def get(self, request):
        return Response({
            'client_id': settings.GOOGLE_CLIENT_ID,
        }, status=status.HTTP_200_OK)