from django.db import models
from django.conf import settings
from .managers import OrderManager, OrderItemManager
from ecommerce.constants import EXCEPTION_LOG_LEVELS
import logging

logger = logging.getLogger('django')


class Order(models.Model):
    """
    customer's order
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    is_paid = models.BooleanField(default=False)

    objects = OrderManager()

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            if not self.pk:  # Check if it's a new instance
                logger.debug(f'Creating Order: {self}')
            super().save(*args, **kwargs)
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            raise

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

    objects = OrderItemManager()

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            if not self.pk:  # Check if it's a new instance
                logger.debug(f'Creating OrderItem: {self}')
            super().save(*args, **kwargs)
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            raise

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

