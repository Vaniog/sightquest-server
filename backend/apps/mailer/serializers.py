from rest_framework import serializers
from .models import Subscriber


class MailSerializer(serializers.Serializer):
    text = serializers.CharField()
    subject = serializers.CharField()
    message = serializers.CharField()
    html_message = serializers.CharField()


class MailingSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(), required=True)
    mail = MailSerializer(required=True)


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ["id", "email", "telegram"]
