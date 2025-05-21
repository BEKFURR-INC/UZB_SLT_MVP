import os
import django

# Set up Django first before importing any Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sign_language_project.settings')
django.setup()  # This is the key line that was missing

# Now import the rest after Django is set up
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import translator.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            translator.routing.websocket_urlpatterns
        )
    ),
})
