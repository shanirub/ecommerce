from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
import logging

from django.http import HttpResponseForbidden

logger = logging.getLogger('django')


class GroupRequiredMixin(UserPassesTestMixin):
    allowed_groups = []

    def test_func(self):
        # Check if user belongs to any of the allowed groups
        return self.request.user.groups.filter(name__in=self.allowed_groups).exists()

    def handle_no_permission(self):
        # Optionally handle unauthorized access
        logger.error("You do not have permission to access this view.")
        return HttpResponseForbidden("You do not have permission to access this page.")
