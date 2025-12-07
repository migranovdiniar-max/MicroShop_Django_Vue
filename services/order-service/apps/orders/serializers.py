from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField(
        read_only=True, max_digits=10, decimal_places=2
    )

    class Meta:
        model = OrderItem
        fields = [
            "id", "product_id", "product_name", 
            "quantity", "price", "subtotal",
            "created_at"
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(
        read_only=True
    )
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user_id", "items", 
            "items_count", "total_quantity",
            "updated_at", "created_at", "status", 
            "total_amount", "shipping_address", "user_email",
            "user_name"
        ]
        read_only_fields = [
            "user_id", "total_amount",
            "user_email", "user_name"
        ]


class CreateOrderSerializer(serializers.ModelSerializer):
    shipping_address = serializers.CharField(max_length=500)

    def validate_shopping_address(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Shipping address must be at least 10 characters long."
            )
        return value.strip()
    

class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    status = serializers.ChoiceField(choices=STATUS_CHOICES)