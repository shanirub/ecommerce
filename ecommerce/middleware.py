from django.http import HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.staticfiles import finders
import logging
logger = logging.getLogger('django')


class CustomErrorMiddleware:
    # TODO revisit when adding permissions
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            # Log the error
            logger.error(f'Error occurred: {str(e)}')

            # Check for static file
            if 'css/styles.css' in str(e):
                # Try to serve the static file instead of returning a 500
                return HttpResponseRedirect(settings.STATIC_URL + 'css/styles.css')

            # Return a generic 500 error
            return HttpResponseServerError("Internal Server Error")

        return response
