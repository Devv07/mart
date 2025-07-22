from django.db import models
from core.models import CustomUser
from vendor.models import Product

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'user'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.quantity})"

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'user'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"