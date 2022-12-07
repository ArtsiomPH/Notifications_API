from rest_framework.request import Request
from django.db.models import Count
from rest_framework.serializers import (
    ModelSerializer,
    IntegerField,
    SerializerMethodField,
)
from .models import Distribution, Client, Message


class DistributionSerializer(ModelSerializer):
    messages = SerializerMethodField("get_msgs")

    class Meta:
        model = Distribution
        fields = [
            "id",
            "mailing_start",
            "message_text",
            "filter",
            "mailing_stop",
            "messages",
        ]
        read_only_fields = ["id", "messages"]

    def get_msgs(self, member):
        request: Request = self.context["request"]

        if not str(member.id) in request.path:
            messages = (
                Message.objects.values("status")
                .filter(distribution_id=member.id)
                .annotate(count=Count("pk"))
            )
            return messages

        messages = Message.objects.filter(distribution_id=member.id)

        return (MessageSerializer(msg).data for msg in messages)


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "tel_number", "operator_code", "tag", "utc"]
        read_only_fields = ["id"]


class MessageSerializer(ModelSerializer):
    distribution_id = IntegerField()
    client_id = IntegerField()

    class Meta:
        model = Message
        fields = ["id", "distribution_id", "client_id", "creating_date", "status"]
        read_only_fields = ["id"]
