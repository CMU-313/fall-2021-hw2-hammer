from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin


class AjaxRedirect(MiddlewareMixin):
    def process_request(self, request):
        ajax_referer = request.META.get('HTTP_X_ALT_REFERER')

        if ajax_referer:
            request.META['HTTP_REFERER'] = ajax_referer

        return None

    def process_response(self, request, response):
        if request.is_ajax():
            if type(response) == HttpResponseRedirect:
                response.status_code = getattr(
                    settings, 'AJAX_REDIRECT_CODE', 302
                )
        return response
