from smtplib import SMTPException

from bs4 import BeautifulSoup
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail as django_send_mail

from .models import Mailing


@shared_task
def send_mailing(emails: list, mailing_id: int):
    mailing: Mailing = Mailing.objects.filter(id=mailing_id).first()
    mail = mailing.mail
    html_message = mail.html_message
    soup = BeautifulSoup(html_message, "html.parser")
    html_message = str(soup)

    try:
        django_send_mail(
            subject=mail.subject,
            message=mail.message,
            from_email=mailing.from_email,
            recipient_list=emails,
            html_message=html_message,
        )
    except SMTPException:
        mailing.status = "FAILED"
        mailing.save()
        raise

    mailing.status = "SUCCEEDED"
    mailing.save()


@shared_task
def send_mail(emails: list, mail: dict):
    html_message = mail.get("html_message")
    soup = BeautifulSoup(html_message, "html.parser")
    html_message = str(soup)
    print(html_message)

    django_send_mail(
        mail.get("subject"),
        mail.get("message"),
        settings.EMAIL_HOST_USER,
        emails,
        html_message=html_message,
    )
