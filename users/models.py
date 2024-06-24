from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


# class Category(models.Model):
#     """
#     a category to which a product can belong
#     """
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True, null=True)
#
#     def __str__(self):
#         return self.name
#
#
# class Product(models.Model):
#     """
#     an item for sale in store.
#     has a foreign key relationship with 'Category'.
#     """
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True, null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     stock = models.IntegerField(default=0)
#
#     def __str__(self):
#         return self.name
#

class User(AbstractUser):
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)


class Order(models.Model):
    """
    customer's order
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    # id field added automatic by django

    def __str__(self):
        return f'Order {self.id} by {self.user}'


class OrderItem(models.Model):
    """
    individual item on a customer's order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

# class CustomUser(AbstractUser):
#    pass
