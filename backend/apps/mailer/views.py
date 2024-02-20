from django.template.loader import render_to_string
from rest_framework.generics import CreateAPIView
from .serializers import MailingSerializerWriteOnly
from rest_framework import generics
from .models import Subscriber, Mailing, Mail
from .serializers import SubscriberSerializer
from .tasks import send_mailing, send_mail


class MailingView(CreateAPIView):
    serializer_class = MailingSerializerWriteOnly
    queryset = Mailing.objects.all()

    def perform_create(self, serializer: MailingSerializerWriteOnly):
        mailing = serializer.save()
        emails: list = serializer.validated_data.get('emails')
        send_mailing.delay(emails, mailing.id)


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
