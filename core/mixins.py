from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import logging

from django.http import HttpResponseForbidden, Http404
from django.views import View
from django.views.generic import CreateView

from orders.models import Order

logger = logging.getLogger('django')


# TODO !!!!!!!!!!! find a way to handle fetching object with two pks, like updating an order item

class SafeGetObjectMixin(View):
    def get_safe_object(self, queryset=None):
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


class OwnershipRequiredMixin(SafeGetObjectMixin):
    """
    mixin to check if user sending the request is the owner of the relevant object
    """
    owner_field = 'user'  # The field to check ownership against the request user
    enforce_for_groups = ['customers']  # only enforce ownership for these groups, defaults to customers
    model_to_check = None # the model to check ownership on
    pk_url_kwarg = 'pk'  # Default URL keyword argument for the primary key

    def get_owner_object(self, **kwargs):
        """
        Default behavior: fetch the object for the view's model, identified by the URL parameter 'pk'.
        Can be overridden in the view for custom ownership checks.
        """

        # TODO !!!!!!!!!!! find a way to handle fetching object with two pks, like updating an order item
        if self.model_to_check is None:
            # default model to check is respective view model
            return self.get_safe_object(**kwargs)

        pk = self.kwargs.get(self.pk_url_kwarg)  # Get the primary key from URL kwargs
        if pk is None:
            raise ValueError(f"{self.pk_url_kwarg} must be provided in the URL parameters.")

        # Use the model_to_check to get the safe object
        queryset = self.model_to_check.objects.all()  # Get the queryset for the model
        return self.get_safe_object(queryset=queryset.filter(pk=pk))  # Filter by primary key


    def dispatch(self, request, *args, **kwargs):
        if any(group.name in self.enforce_for_groups for group in request.user.groups.all()):
            # user in group that demand ownership's check
            owner_object = self.get_owner_object()
            if getattr(owner_object, self.owner_field) != request.user:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class GroupRequiredMixin(UserPassesTestMixin):
    """
    mixin to check if user sending the request has the required permissions
    """
    # override with allowed groups
    allowed_groups = []

    def test_func(self):
        user = self.request.user
        user_groups = user.groups.values_list('name', flat=True)
        if not any(group in self.allowed_groups for group in user_groups):
            # user is not a member of any allowed group
            return False

        return True

    def handle_no_permission(self):
        # Optionally handle unauthorized access
        logger.error("You do not have permission to access this view.")
        return HttpResponseForbidden("You do not have permission to access this page.")
