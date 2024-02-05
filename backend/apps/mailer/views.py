from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from .tasks import send_mailing
from .serializers import MailingSerializer, MailSerializer
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework import generics
from .models import Subscriber
from .serializers import SubscriberSerializer
from .tasks import send_mailing


class MailingView(CreateAPIView):
    serializer_class = MailingSerializer

    @staticmethod
    def post(request, *args, **kwargs):
        serializer = MailingSerializer(data=request.data)
        if serializer.is_valid():
            emails: list = serializer.validated_data.get('emails')
            mail: MailSerializer = serializer.validated_data.get('mail')

            send_mailing.delay(emails, mail)

            return Response({'success': True}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class SubscriberListCreateView(generics.ListCreateAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer

    def perform_create(self, serializer):
        subscriber = serializer.save()
        mail_data = {
            "subject": "Beta test",
            "message": "Welcome to beta test",
            "html_message": "<h1>Welcome to beta test</h1>",
        }
        send_mailing.delay([subscriber.email], mail_data)
