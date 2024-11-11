from django.shortcuts import render
import logging
from django.core.exceptions import PermissionDenied
from django.http import Http404

logger = logging.getLogger('django')

class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            if response.status_code in [403, 404]:
                # Return the same page for both forbidden and not found cases
                return render(request, 'access_denied.html', status=403)
            return response
        except PermissionDenied:
            # Handle specific 403 errors due to permissions
            logger.warning("Permission denied: user tried to access a forbidden resource.")
            return render(request, 'access_denied.html', status=403)
        except Http404:
            # Handle 404 errors
            logger.warning("Resource not found: user tried to access a non-existent resource.")
            return render(request, 'access_denied.html', status=403)
        except Exception as e:
            # Catch all other exceptions, log them, and show a 500 error page
            logger.error(f"Unhandled exception occurred: {str(e)}", exc_info=True)
            return render(request, '500.html', status=500)

