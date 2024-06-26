from django.db import models


class Category(models.Model):
    """
    a category to which a product can belong
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    an item for sale in store.
    has a foreign key relationship with 'Category'.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name
