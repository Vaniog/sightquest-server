from apps.sockets.views import game_socket
from django.contrib import admin

# Docs
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="API for NoLabelAPI hackyhon",
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
    path("admin/", admin.site.urls),
    path("api/", include("apps.api.urls")),
    path("api/", include("apps.mailer.urls")),
    path("", game_socket),
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
