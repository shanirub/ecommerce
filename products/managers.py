from django.db import models


class ProductManager(models.Manager):
    def create_product(self, name, description, price, category, stock):
        return self.create(
            name=name, description=description, price=price, category=category, stock=stock)

    def update_product(self, name, **kwargs):
        try:
            product = self.get(name=name)
            for key, value in kwargs.items():
                setattr(product, key, value)
                product.save()
                return product
        except self.model.DoesNotExist:
            return None

    def get_product(self, name):
        try:
            product = self.get(name=name)
            return product
        except self.model.DoesNotExist:
            return None

    def delete_product(self, name):
        """
        :param name:
        :return: If category exists: number of objects deleted and a dictionary with the number of deletions per object type
        else returns None
        """
        try:
            product = self.get(name=name)
            num_of_items_deleted = product.delete()
            return num_of_items_deleted
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

    def get_category(self, name):
        try:
            category = self.get(name=name)
            return category
        except self.model.DoesNotExist:
            return None

    def delete_category(self, name):
        """
        :param name:
        :return: If category exists: number of objects deleted and a dictionary with the number of deletions per object type
        else returns None
        """
        try:
            category = self.get(name=name)
            num_of_items_deleted = category.delete()
            return num_of_items_deleted
        except self.model.DoesNotExist:
            return None


