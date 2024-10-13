from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import logging

from django.http import HttpResponseForbidden, Http404

from orders.models import Order

logger = logging.getLogger('django')

class GroupRequiredMixin(UserPassesTestMixin):
    # override with allowed groups
    allowed_groups = []

    # override when enforcing ownership
    enforce_customer_owner = False

    def test_func(self):
        user = self.request.user

        # First, check if user belongs to any allowed groups
        user_groups = user.groups.values_list('name', flat=True)
        if not any(group in self.allowed_groups for group in user_groups):
            return False

        # If user is in the 'customers' group and ownership enforcement is required
        if self.enforce_customer_owner and 'customers' in user_groups:
            try:
                obj = self.get_object()  # Fetch the object (could be Order, OrderItem, etc.)
                obj_owner = obj.user
                return user == obj_owner
            except Http404:
                # not returning 404, but 403, as to not reveal the resource is missing
                logger.error("Resource does not exist and user has no permissions. Returning 403 instead of 404 to hide the fact the resource is missing")
                return False

        # Otherwise, allow access if they are in allowed groups
        return True

    def handle_no_permission(self):
        # Optionally handle unauthorized access
        logger.error("You do not have permission to access this view.")
        return HttpResponseForbidden("You do not have permission to access this page.")
