from apps.sockets import routing as sockets_routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Если нужно будет добавить еще паттернов, добавлять их через +
all_websocket_urlpatterns = sockets_routing.websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(all_websocket_urlpatterns)
        ),
    }
)
