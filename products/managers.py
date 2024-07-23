from django.db import models
from typing import Union, Optional

from ecommerce.constants import EXCEPTION_LOG_LEVELS
import logging

logger = logging.getLogger('django')


class ProductManager(models.Manager):
    def create_product(self, name: str, description: str, price: Union['Decimal', float, str], category: 'Category',
                       stock: int) -> Optional['Product']:
        """
        create a new Product
        :param name:
        :param description:
        :param price:
        :param category:
        :param stock:
        :return: new Product object, or None if failed
        """
        try:
            new_product = self.create(
                name=name, description=description, price=price, category=category, stock=stock)
            logger.debug(f"new product was created successfully: {new_product}")
            return new_product
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            return None

    def update_product(self, product: 'Product', **kwargs) -> Optional['Product']:
        """
        update product's attributes
        :param product: Product object
            TODO: handle Product object and product's name (str). There's an open issue
        :param kwargs: attributes of product to update
        :return: updated Product object if successful. None otherwise
        """
        try:
            if isinstance(product, str):
                # product = self.get(name=product)
                raise Exception("Currently not allowing updating Product using name field")

            for key, value in kwargs.items():
                setattr(product, key, value)
                product.save()
                logger.debug(f"updated product {product}, {key}:{value}")
            return product
        except self.model.DoesNotExist:
            logger.error(f"Product was not found")
            return None
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            return None

    def get_product(self, name: str) -> Optional['Product']:
        try:
            product = self.get(name=name)
            return product
        except self.model.DoesNotExist:
            logger.error(f"Product {name} was not found")
            return None
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            return None

    def delete_product(self, name: str) -> Optional[dict]:
        """
        :param name:
        :return: If product exists: number of objects deleted and a dictionary with the number of deletions per object type
        else returns None
        """
        try:
            result = self.get(name=name).delete()
            return result
        except self.model.DoesNotExist:
            logger.error(f"Product {name} was not found")
            return None
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            return None


class CategoryManager(models.Manager):
    def create_category(self, name: str, description: str) -> Optional['Category']:
        try:
            new_category = self.create(name=name, description=description)
            logger.debug(f"new category was created successfully: {new_category}")
            return new_category
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            return None

    def update_category(self, name: str, **kwargs) -> Optional['Category']:
        try:
            category = self.get(name=name)
            for key, value in kwargs.items():
                setattr(category, key, value)
                category.save()
                logger.debug(f"updated category {category}, {key}:{value}")
            return category
        except self.model.DoesNotExist:
            logger.error(f"Category {name} does not exist.")
            return None
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            return None

    def get_category(self, name: str) -> Optional['Category']:
        try:
            category = self.get(name=name)
            return category
        except self.model.DoesNotExist:
            logger.error(f"Category {name} does not exist.")
            return None
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            return None

    def delete_category(self, name: str) -> Optional[dict]:
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
            logger.error(f"Category {name} does not exist.")
            return None
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"An error occurred: {str(e)}", exc_info=True)
            return None
