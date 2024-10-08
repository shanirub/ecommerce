from django.db import models
from django.http import Http404
from django.views.generic import View


class SafeGetObjectMixin(View):
    def get_object(self, queryset=None):
        """
        Safe get_object() to assure a DoesNotExist exception will be translated to a 404 page
        :param queryset:
        :return:
        """
        try:
            if queryset is None:
                queryset = self.get_queryset()
            return super().get_object(queryset)
        except self.model.DoesNotExist:
            raise Http404(f"{self.model.__name__} does not exist")


def compare_model_instances(instance1, instance2):
    """
    Compares the fields of two Django model instances and returns a dictionary
    with the differences. Keys are field names, and values are tuples of the form
    (value_in_instance1, value_in_instance2).

    Args:
        instance1 (models.Model): The first model instance.
        instance2 (models.Model): The second model instance.

    Returns:
        dict: A dictionary with differences.
    """
    if not isinstance(instance1, models.Model) or not isinstance(instance2, models.Model):
        raise ValueError("Both arguments must be Django model instances.")

    if type(instance1) is not type(instance2):
        raise ValueError("Both model instances must be of the same type.")

    differences = {}
    for field in instance1._meta.get_fields():
        if field.concrete and not field.many_to_many and not field.one_to_many:
            value1 = getattr(instance1, field.name)
            value2 = getattr(instance2, field.name)
            if value1 != value2:
                differences[field.name] = (value1, value2)

    return differences
