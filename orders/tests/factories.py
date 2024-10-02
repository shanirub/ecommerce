import factory
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from products.tests.factories import UserFactory, GroupFactory, ProductFactory, CategoryFactory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    created_at = factory.Faker('date_time_this_year')
    updated_at = factory.Faker('date_time_this_year')
    is_paid = factory.Faker('boolean')


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Faker('random_int', min=1, max=10)
    price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
