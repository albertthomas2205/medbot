"""
ASGI config for asgi_uk_medical_bot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import robot_management.routing
# from starlette.staticfiles import StaticFiles

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asgi_uk_medical_bot.settings')

# # plain Django ASGI app for HTTP
# django_asgi_app = get_asgi_application()

# # Wrap only the HTTP app with WhiteNoise
# media_app = StaticFiles(directory="/app/media")

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     'websocket':AuthMiddlewareStack(
#         URLRouter(
#             robot_management.routing.websocket_urlpatterns
#         )
#     )
# })




import os
from pathlib import Path

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from starlette.staticfiles import StaticFiles
import robot_management.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asgi_uk_medical_bot.settings')

# Django ASGI application
django_asgi_app = get_asgi_application()

# Get BASE_DIR from settings or calculate manually
BASE_DIR = Path(__file__).resolve().parent.parent



application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            robot_management.routing.websocket_urlpatterns
        )
    ),
})
