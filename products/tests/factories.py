import factory as factory
from django.contrib.auth.models import Group
from users.models import User
from products.models import Product, Category


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f'group{n}')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # Temporarily setting a placeholder for the username
    username = factory.LazyAttribute(lambda obj: f'user_default')
    password = factory.PostGenerationMethodCall('set_password', 'password')

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.groups.add(*extracted)
            # Use the name of the first group to update the username
            group_name = extracted[0].name if extracted else "default"
            self.username = f'user_{group_name}'
            self.save()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'category{n}')
    description = 'Default category description'


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('word')  # Generates a random word as the product name
    description = factory.Faker('word')
    price = 100.0
    stock = 10
    category = factory.SubFactory(CategoryFactory)
