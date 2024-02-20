from django.template.loader import render_to_string
from .serializers import MailingSerializerWriteOnly, MailingSerializerReadOnly
from rest_framework import generics
from .models import Subscriber, Mailing
from .serializers import SubscriberSerializer
from .tasks import send_mailing, send_mail


class MailingCreateView(generics.CreateAPIView):
    serializer_class = MailingSerializerWriteOnly
    queryset = Mailing.objects.all()

    def perform_create(self, serializer: MailingSerializerWriteOnly):
        mailing = serializer.save()
        emails: list = serializer.validated_data.get('emails')
        send_mailing.delay(emails, mailing.id)


class MailingListView(generics.ListAPIView):
    serializer_class = MailingSerializerReadOnly
    queryset = Mailing.objects.all()


class MailingRetrieveView(generics.RetrieveAPIView):
    serializer_class = MailingSerializerReadOnly
    queryset = Mailing.objects.all()


class SubscriberListCreateView(generics.ListCreateAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer

    def perform_create(self, serializer):
        subscriber = serializer.save()
        mail_data = {
            "subject": "SightQuest БетаТест",
            "html_message": render_to_string("email-message.html"),
        }
        send_mail.delay([subscriber.email], mail_data)
