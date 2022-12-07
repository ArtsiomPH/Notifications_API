from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .models import Distribution, Client, Message
from .serialisers import DistributionSerializer, ClientSerializer, MessageSerializer
from rest_framework import mixins


class DistributionViewSet(ModelViewSet):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MessageViewSet(mixins.DestroyModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
