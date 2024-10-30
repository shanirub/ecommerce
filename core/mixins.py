from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import logging

from django.db.models import QuerySet
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


from django.http import Http404
import logging

logger = logging.getLogger(__name__)


class OwnershipRequiredMixin:
    enforce_for_groups = ['customers']

    def is_in_enforce_group(self, request):
        """
        Checks if the user belongs to any of the groups for which ownership checks are enforced.
        """
        return any(group.name in self.enforce_for_groups for group in request.user.groups.all())

    def get_owner_user(self, obj_or_queryset=None, **kwargs):
        """
        Determines the owner of an object or the first object in a queryset.
        Uses the custom get_owner_user method from the object's manager if available.
        """
        try:
            # Handle queryset by selecting the first object in it
            # obj = obj_or_queryset.first() if isinstance(obj_or_queryset, QuerySet) else obj_or_queryset
            obj = obj_or_queryset

            # Ensure obj is not None
            if obj is None:
                return None

            # Get the model's manager by referencing the class of the object
            model_class = obj.__class__  # This gets the class of the instance
            if hasattr(model_class, 'objects') and hasattr(model_class.objects, 'get_owner_user'):
                return model_class.objects.get_owner_user(kwargs['pk'])

            # Fallback to default behavior
            return getattr(obj, 'user', None)  # Return user attribute if it exists
        except Exception as e:
            log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
            logger.log(log_level, f"Error retrieving owner: {str(e)}", exc_info=True)
            return None

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method to enforce ownership check for specific groups.
        Raises Http404 if the user is not the owner.
        """
        if self.is_in_enforce_group(request):
            try:
                obj = self.get_object()
                if request.user != self.get_owner_user(obj, **kwargs):
                    raise Http404("User does not own all items in this query.")

                #import ipdb; ipdb.set_trace()

                # For multiple items, check if all items belong to the current user
                '''
                if isinstance(objects, QuerySet):
                    for obj in objects:
                        if request.user != self.get_owner_user(obj, **kwargs):
                            raise Http404("User does not own all items in this query.")
                else:
                    # For single object views, validate ownership of the single object
                    if request.user != self.get_owner_user(objects, **kwargs):
                        raise Http404("User does not own this item.")
                '''


            except Http404 as e:
                logger.warning(f"Ownership enforcement triggered Http404: {str(e)}")
                raise
            except Exception as e:
                log_level = EXCEPTION_LOG_LEVELS.get(type(e), logging.ERROR)
                logger.log(log_level, f"Unexpected error in ownership check: {str(e)}", exc_info=True)
                raise Http404("Ownership validation failed.")

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
