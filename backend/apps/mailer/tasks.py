from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from bs4 import BeautifulSoup


@shared_task
def send_mailing(emails: list, mail: dict):
    html_message = mail.get("html_message")
    soup = BeautifulSoup(html_message, 'html.parser')
    html_message = str(soup)
    print(html_message)

    send_mail(
        mail.get("subject"),
        mail.get("message"),
        settings.EMAIL_HOST_USER,
        emails,
        html_message=html_message,
    )
