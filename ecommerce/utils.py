from django.db import models
from django.http import Http404
from django.views.generic import View
from django.db import models


def check_permission(testcase_object, url, user, expected_status, method='get', data=None):
    """
    helper method for permission view tests
    :param testcase_object: TestCase object (that contains the tests)
    :param url: for generating request
    :param user: for generating request
    :param expected_status: expected status code for response
    :param method: request method 'post' or 'get' (default is 'get')
    :param data: additional data to send with request
    :return:
    """
    testcase_object.client.login(username=user.username, password='password')

    if method == 'post':
        response = testcase_object.client.post(url, data=data)
    else:
        response = testcase_object.client.get(url)

    testcase_object.assertEqual(response.status_code, expected_status)

def validate_raw_bool_value(value):
    """
    helper method to assure a value is True or False, and not just truthy or falsy
    used in various views to validate bool values
    (in model level, raw value is already processed by django as a truthy / falsy.
        for example: int(15) will be processed as False)

    :param value: raw value (given as str in view)
    :return: True if value is indeed a bool, False otherwise
    """
    return value in ['True', 'False']


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
