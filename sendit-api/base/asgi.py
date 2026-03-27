import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# Set the settings module
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'base.settings.development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# --- NEW: Import your custom middleware ---
from base.middleware import JWTAuthMiddleware
# Import your routing
from apps.core.routing import websocket_urlpatterns 

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware( 
        URLRouter(
            websocket_urlpatterns
        )
    ),
})