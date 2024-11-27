import factory
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from products.tests.factories import UserFactory, GroupFactory, ProductFactory, CategoryFactory
import logging
logger = logging.getLogger('django')


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    created_at = factory.Faker('date_time_this_year')
    updated_at = factory.Faker('date_time_this_year')
    is_paid = False

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        # If 'user' is not provided, create a new one with UserFactory
        if 'user' not in kwargs:
            kwargs['user'] = UserFactory()

        return kwargs

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        logger.debug(f'OrderFactory called with args: {args}, kwargs: {kwargs}')
        instance = super()._create(model_class, *args, **kwargs)
        logger.debug(f'OrderFactory finished generating: {instance}')
        return instance



class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    # price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        # If 'order' is not provided, create a new one with OrderFactory
        if 'order' not in kwargs:
            kwargs['order'] = OrderFactory()
        if 'quantity' not in kwargs:
            kwargs['quantity'] = factory.Faker('random_int', min=1, max=10)
        if 'product' not in kwargs:
            kwargs['product'] = factory.SubFactory(ProductFactory)

        product_price = kwargs['product'].price
        kwargs['price'] = product_price * kwargs['quantity']
        return kwargs

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        logger.debug(f'OrderItemFactory called with args: {args}, kwargs: {kwargs}')
        instance = super()._create(model_class, *args, **kwargs)
        logger.debug(f'OrderItemFactory finished generating: {instance}')
        return instance

