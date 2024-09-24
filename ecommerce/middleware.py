import logging
from django.http import HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('django')


class CustomErrorMiddleware(MiddlewareMixin):
    # TODO: revisit errors on deployment later
    def process_exception(self, request, exception):
        # Log the exception
        logger.error(f"An error occurred: {exception}", exc_info=True)
        # Return a 500 Internal Server Error response
        return HttpResponseServerError("Internal Server Error")
