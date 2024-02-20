from django.urls import path

from .views import MailingView, SubscriberListCreateView

urlpatterns = [
    path("send-mailing/", MailingView.as_view(), name="send-mailing"),
    path(
        "subscribers/",
        SubscriberListCreateView.as_view(),
        name="subscriber-list-create",
    ),
]
