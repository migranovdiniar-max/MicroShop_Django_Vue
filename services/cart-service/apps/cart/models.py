from django.db import models
from decimal import Decimal

class Cart(models.Model):
    user_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for User {self.user_id}"
    
    @property
    def total_amount(self):
        """The total amount of the cart."""
        return (
            sum(item.subtotal for item in self.items.all())
        )

    @property
    def total_items(self):
        """The total number of items in the cart."""
        return (
            sum(item.quantity for item in self.items.all())
        )
    
    def clear(self):
        """Clear the cart."""
        self.items.all().delete()

    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    product_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product_id']

    def __str__(self):
        return (
            f"{self.quantity} x {self.product_name} "
        )

    @property
    def subtotal(self):
        """Subtotal for the cart item."""
        return self.price * self.quantity