from django.db import models


class ProductManager(models.Manager):
    def create_product(self, name, description, price, category, stock):
        return self.create(
            name=name, description=description, price=price, category=category)

    def update_product(self, name, **kwargs):
        try:
            product = self.get(name=name)
            for key, value in kwargs.items():
                setattr(product, key, value)
                product.save()
                return product
        except self.model.DoesNotExist:
            return None


class CategoryManager(models.Manager):
    def create_category(self, name, description):
        return self.create(name=name, description=description)

    def update_category(self, name, **kwargs):
        try:
            category = self.get(name=name)
            for key, value in kwargs.items():
                setattr(category, key, value)
                category.save()
                return category
        except self.model.DoesNotExist:
            return None


