from django.conf import settings
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
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
    if request.user.is_authenticated:
        user = request.user

        change_user_url = reverse("admin:users_customuser_change", args=[user.id])

        content = {
            "user": user,
            "site_settings": settings.JAZZMIN_SETTINGS,
            "change_user_url": change_user_url,
            "admin_url": reverse("admin:index"),
        }

        return render(request, "mailer-admin/send-mail-page.html", content)
    else:
        return redirect("admin:index")
