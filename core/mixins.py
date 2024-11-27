from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import logging
from django.db.models import QuerySet
from django.db.models.expressions import result
from django.http import HttpResponseForbidden, Http404
from django.template.context_processors import request
from django.views import View
from django.views.generic import CreateView
from django.views.generic.detail import SingleObjectMixin

from ecommerce.constants import EXCEPTION_LOG_LEVELS
from orders.models import Order

logger = logging.getLogger('django')

class SafeGetObjectMixin:
    """
    Mixin to handle object retrieval with DoesNotExist exception handling.
    """
    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset=queryset)
        except self.model.DoesNotExist:
            raise Http404("Object does not exist")
            # will be catched by middleware and resent as 403


class OwnershipRequiredMixin:
    # ownership check only for this groups
    enforce_for_groups = ['customers']

    def is_in_enforce_group(self, request):
        return any(group.name in self.enforce_for_groups for group in request.user.groups.all())

    def get_object_owner(self, **kwargs):
        try:
            if hasattr(self.model, 'objects'):
                if hasattr(self.model.objects, 'get_owner_user'):
                    # special case, use helper method in manager
                    logger.debug(f"trying to fetch owner using get_owner_user() in model {self.model}"
                                 f"with pk= {kwargs.get('pk')}")
                    result = self.model.objects.get_owner_user(kwargs.get('pk'))
                    return result

                # default - return user field
                logger.debug(f"trying to fetch owner using default get_object().user")
                obj = self.get_object()
                return obj.user

        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"Error retrieving owner: {str(e)}", exc_info=True)
            return None

    def dispatch(self, request, *args, **kwargs):
        logger.debug(f"Checking ownership for request...")
        if self.is_in_enforce_group(request):
            try:
                request_user = request.user
                object_owner = self.get_object_owner(pk=self.kwargs.get('pk'))
                if request_user != object_owner:
                    logger.error(f"Permission denied: request_user {request_user} is not the same as object_owner {object_owner}")
                    raise Http404
            except Http404 as e:
                logger.warning(f"Ownership enforcement triggered Http404: {str(e)}")
                raise
            except Exception as e:
                log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
                logger.log(log_level, f"Unexpected error in ownership check: {str(e)}", exc_info=True)
                raise Http404("Ownership validation failed.")

        logger.debug(f"... ownership check finished without errors!")
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
