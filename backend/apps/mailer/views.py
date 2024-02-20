from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from rest_framework import generics
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from .models import Subscriber
from .serializers import MailingSerializer, MailSerializer, SubscriberSerializer
from .tasks import send_mailing


class MailingView(CreateAPIView):
    serializer_class = MailingSerializer

    @staticmethod
    def post(request, *args, **kwargs):
        serializer = MailingSerializer(data=request.data)
        if serializer.is_valid():
            emails: list = serializer.validated_data.get("emails")
            mail: MailSerializer = serializer.validated_data.get("mail")

            send_mailing.delay(emails, mail)

            return Response({"success": True}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class SubscriberListCreateView(generics.ListCreateAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer

    def perform_create(self, serializer):
        subscriber = serializer.save()
        mail_data = {
            "subject": "SightQuest БетаТест",
            "html_message": render_to_string("email-message.html"),
        }
        send_mailing.delay([subscriber.email], mail_data)


def mailing_admin(request):
    return render(request, "mailer-admin/send-mail-page.html")
