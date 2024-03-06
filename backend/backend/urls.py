from apps.mailer.views import mailing_admin
from apps.sockets.views import game_socket, game_v2
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views

# Docs
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="API for SightQuest",
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    # Docs
    # path(
    #    "api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    # ),
    # Custom
    path("api/admin/", admin.site.urls),
    path("api/mailing-admin/", mailing_admin, name="mailing-admin"),
    path("api/mailing-admin/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("api/", include("apps.api.urls")),
    path("api/", include("apps.mailer.urls")),
    path("game/", game_socket),
    path("game/v2/", game_v2),
]

swagger_patterns = [
    path(
        "api/swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += swagger_patterns
