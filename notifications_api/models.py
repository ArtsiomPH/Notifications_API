from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Q
from .tasks import send_message, error_handling
from datetime import timedelta


class Distribution(models.Model):
    mailing_start = models.DateTimeField()
    message_text = models.TextField()
    filter = models.JSONField()
    mailing_stop = models.DateTimeField()

    def get_clients(self):
        if len(self.filter) == 1:
            clients = Client.objects.filter(
                Q(operator_code=self.filter.get("code")) | Q(tag=self.filter.get("tag"))
            )
        if len(self.filter) == 2:
            clients = Client.objects.filter(
                operator_code=self.filter.get("code"), tag=self.filter.get("tag")
            )

        return clients

    def start_mailing(self, msg):
        start_mailing_datetime = self.mailing_start + timedelta(seconds=10)
        send_message.apply_async(
            (msg, self.mailing_stop),
            eta=start_mailing_datetime,
            link_error=error_handling.s(msg),
        )

    def add_messages(self):
        clients = self.get_clients()
        for client in clients:
            message, created = Message.objects.get_or_create(
                distribution=self,
                client=client,
                creating_date=self.mailing_start,
                status="mailing started",
            )
            if created:
                self.start_mailing(message)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.add_messages()


class Client(models.Model):
    tel_number = models.IntegerField(
        validators=[
            RegexValidator(regex=r"^7[0-9]{10}$", message="Invalid number format")
        ]
    )
    operator_code = models.PositiveIntegerField()
    tag = models.CharField(max_length=10)
    utc = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"UTC(|(\+|-)([0-9]|1{1}[0-4]{1}))$",
                message="Invalid timezone format. Example: UTC+10",
            )
        ],
    )


class Message(models.Model):
    distribution = models.ForeignKey(
        Distribution,
        related_name="msgs",
        related_query_name="msg",
        on_delete=models.CASCADE,
    )
    client = models.ForeignKey(
        Client, related_name="msgs", related_query_name="msg", on_delete=models.CASCADE
    )
    creating_date = models.DateTimeField()
    status = models.CharField(max_length=255)
