from .models import Order, OrderItem
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .serializers import (
    OrderSerializer, CreateOrderSerializer,
    UpdateOrderStatusSerializer
)
# from .services import (

# )
import logging


logger = logging.getLogger(__name__)

class IsAuthenticatedCustom:
    """Custom permission class for order views."""

    def has_permission(self, request, view):
        return (
            hasattr(request, 'user_id') and request.user is not None
        )

class OrderListView(generics.ListAPIView):
    serializers_class = OrderSerializer
    permission_classes = [IsAuthenticatedCustom]

    def get_queryset(self):
        return (
            Order.objects.filter(user_id=self.request.user_id)
        )


def OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedCustom]

    def get_object(self):
        return (
            get_object_or_404(
                Order, id=self.kwargs['pk'], user_id=self.request.user_id
            )
        )