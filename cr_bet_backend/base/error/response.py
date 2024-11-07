from django.http import HttpResponseBadRequest
import json


class HttpResponseError:
    @classmethod
    def http_response_400(cls, **kwargs):
        errors = {"errors": kwargs['errors']} if 'errors' in kwargs else {"errors": {"message": "error not provided!"}}
        
        return HttpResponseBadRequest(content_type="application/JSON", content=json.dumps(errors))
