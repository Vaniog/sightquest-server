from django.conf import settings
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from .serializers import MailingSerializerWriteOnly, MailingSerializerReadOnly
from .models import Mailing
from .tasks import send_mail
from django.urls import reverse
from rest_framework import generics

from .models import Subscriber
from .serializers import SubscriberSerializer
from .tasks import send_mailing


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
