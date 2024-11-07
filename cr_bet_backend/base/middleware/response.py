from django.utils.deprecation import MiddlewareMixin


class CustomResponseMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        super(CustomResponseMiddleware, self).__init__(self)
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        CONTENT_TYPE = request.META.get('CONTENT_TYPE')
        
        if CONTENT_TYPE == "application/json":
            response["Content-Type"] = "application/json; charset=utf-8"
        return response
