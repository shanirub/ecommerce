from django.db import models
from .managers import ProductManager, CategoryManager
from django.core.validators import MinValueValidator, MinLengthValidator
import decimal

from ecommerce.constants import EXCEPTION_LOG_LEVELS
import logging

logger = logging.getLogger('django')


class Category(models.Model):
    """
    a category to which a product can belong
    """
    name = models.CharField(max_length=100, validators=[MinLengthValidator(1)])
    description = models.TextField(blank=True, null=True)

    objects = CategoryManager()

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            super().save(*args, **kwargs)
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            raise

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    an item for sale in store.
    has a foreign key relationship with 'Category'.
    """
    name = models.CharField(max_length=100, validators=[MinLengthValidator(1)], unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    objects = ProductManager()

    # TODO: performance potential issue: assure price (or other when comparing) is not a Decimal
    # TODO: before casting it. If it is a Decimal, just need to handle decimal places issue

    def save(self, *args, **kwargs):
        try:
            # Ensure the price is formatted correctly according to decimal_places
            decimal_places = self._meta.get_field('price').decimal_places
            self.price = decimal.Decimal(self.price).quantize(
                decimal.Decimal(f'1.{"0" * decimal_places}'),
                rounding=decimal.ROUND_DOWN
            )
            self.full_clean()
            super().save(*args, **kwargs)
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            raise

    # def __eq__(self, other):
    #     decimal_places = self._meta.get_field('price').decimal_places
    #     other = decimal.Decimal(other).quantize(
    #         decimal.Decimal(f'1.{"0" * decimal_places}'),
    #         rounding=decimal.ROUND_DOWN
    #     )
    #
    #     return self.price == other

    def __str__(self):
        return self.name
