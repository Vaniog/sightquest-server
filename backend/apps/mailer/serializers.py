from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import ValidationError

from .models import Mail, Mailing, Subscriber


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ["id", "email", "telegram"]


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = ["id", "subject", "message", "html_message", "text"]


class MailingSerializerReadOnly(serializers.ModelSerializer):
    mail = MailSerializer(many=False, read_only=True)
    recipients = SubscriberSerializer(many=True, read_only=True)

    class Meta:
        model = Mailing
        fields = ["id", "from_email", "created_at", "recipients", "mail", "status"]
        read_only_fields = fields


class MailingSerializerWriteOnly(serializers.ModelSerializer):
    mail = MailSerializer(many=False, write_only=True, required=True)
    emails = serializers.ListField(
        child=serializers.EmailField(), required=True, write_only=True
    )

    class Meta:
        model = Mailing
        fields = ["id", "emails", "mail"]
        write_only_fields = ["emails", "mail"]

    def create(self, validated_data):
        validated_data["from_email"] = settings.EMAIL_HOST_USER

        mail_data = validated_data.pop("mail", None)
        emails_data = validated_data.pop("emails", None)

        mail_instance = Mail.objects.create(**mail_data)

        validated_data["mail"] = mail_instance

        mailing_instance = Mailing.objects.create(**validated_data)

        for email in emails_data:
            subscriber = Subscriber.objects.filter(email=email).first()
            if subscriber is not None:
                mailing_instance.recipients.add(subscriber)

        return mailing_instance
