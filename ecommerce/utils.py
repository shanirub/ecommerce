from django.db import models


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

'''
view

from django.shortcuts import render
from .models import Order
from .utils import compare_model_instances

def compare_orders_view(request, order_id1, order_id2):
    order1 = Order.objects.get(id=order_id1)
    order2 = Order.objects.get(id=order_id2)
    
    differences = compare_model_instances(order1, order2)
    
    return render(request, 'compare_orders.html', {'differences': differences})

html

<!-- compare_orders.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Compare Orders</title>
</head>
<body>
    <h1>Differences between Orders</h1>
    <ul>
        {% for field, values in differences.items %}
            <li>{{ field }}: {{ values.0 }} != {{ values.1 }}</li>
        {% endfor %}
    </ul>
</body>
</html>
'''