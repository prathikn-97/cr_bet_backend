# from rest_framework_simplejwt.authentication import JWTAuthentication
# from threading import local

# _thread_locals = local()


# def set_current_instance_field(name, value):
#     setattr(_thread_locals, name, value)


# class JSONWebTokenAuthentication(JWTAuthentication):

#     def authenticate(self, request):
#         authorization = request.META.get("HTTP_AUTHORIZATION", None)
#         # self.org = request.META.get("HTTP_COMPANY", None)
#         header = self.get_header(request)
#         if header is None:
#             return None

#         raw_token = self.get_raw_token(header)
#         if raw_token is None:
#             return None

#         validated_token = self.get_validated_token(raw_token)
#         set_current_instance_field("authorization", True)
#         return self.get_user(validated_token), validated_token

from threading import local
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BasicAuthentication
from utils.helpers import get_user_from_token

_thread_locals = local()


def set_current_instance_field(name, value):
    setattr(_thread_locals, name, value)


class JSONWebTokenAuthentication(BasicAuthentication):

    def authenticate(self, request):
        header = request.headers
        if header is None:
            return None
        uuid = None
        if request.COOKIES.get("uuid"):
            uuid = request.COOKIES.get("uuid")
        else:
            authorization = header.get("Authorization")
            if authorization:
                uuid = authorization.split()[1]
        return get_user_from_token(uuid, request), uuid