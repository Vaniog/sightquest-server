from django.db import models


class Subscriber(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=255, unique=True)
    telegram = models.CharField(max_length=255, null=True)
    approved = models.BooleanField(default=False)


class Mail(models.Model):
    subject = models.TextField(blank=False, null=True)
    message = models.TextField(blank=False, null=True)
    html_message = models.TextField(blank=False, null=True)
    text = models.TextField(blank=False, null=True)


class Mailing(models.Model):
    from_email = models.EmailField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField(Subscriber, related_name="mailings")
    mail = models.OneToOneField(Mail, related_name="mailing", on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ("PROCESSING", "Processing"),
        ("SUCCEEDED", "Succeeded"),
        ("FAILED", "Failed"),
    ]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="PROCESSING"
    )
