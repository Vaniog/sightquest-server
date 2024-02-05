from django.db import models


class Subscriber(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=255)
    telegram = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
