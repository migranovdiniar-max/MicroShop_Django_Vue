from django.db import models
from decimal import Decimal


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user_id = models.IntegerField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, 
        default="pending"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, 
        default=Decimal("0.00")
    )
    shipping_address = models.TextField()
    user_email = models.EmailField(blank=True)
    user_name = models.CharField(
        max_length=200, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


    def __str__(self):
        return f"Order #{self.id} - {self.user_id}"

    @property
    def items_count(self):
        """Count of items in the order."""
        return self.items.count()
    
    @property
    def total_quantity(self):
        return sum(
            item.quantity for item in self.items.all()
        )
    
    def calculate_total(self):
        total = sum(
            item.subtotal for item in self.items.all()
        )
        self.total_amount = total
        return total
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order Item #{self.quantity} - {self.product_name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price