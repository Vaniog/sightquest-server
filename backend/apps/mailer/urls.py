from django.urls import path
from .views import MailingCreateView, SubscriberListCreateView, MailingListView, MailingRetrieveView

urlpatterns = [
    path('send-mailing/', MailingCreateView.as_view(), name='send-mailing'),
    path('mailings/', MailingListView.as_view(), name='get-mailings'),
    path('mailings/<int:pk>/', MailingRetrieveView.as_view(), name='get-mailing-by-id'),
    path('subscribers/', SubscriberListCreateView.as_view(), name='subscriber-list-create'),
]
