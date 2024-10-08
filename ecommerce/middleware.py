from django.shortcuts import render
import logging

logger = logging.getLogger('django')


class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            if response.status_code == 500:
                return render(request, '500.html', status=500)
            elif response.status_code == 404:
                return render(request, '404.html', status=404)

            return response
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return render(request, '500.html', status=500)
