from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from .authentication import JSONWebTokenAuthentication

from cr_bet_backend.base.middleware import CustomResultsSetPagination
from rest_framework import serializers


class CRUDPermission(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


"""
    Admin Base View Set
"""


class AdminBaseViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


"""
    App User ViewSet
"""


class CustomAuthenticated(IsAuthenticated):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        # print("from permission",request.user)
        if not request.user:
            raise serializers.ValidationError("token is invalid")
        return True


class AppBaseViewSet(viewsets.ModelViewSet):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = [CustomAuthenticated]
    pagination_class = CustomResultsSetPagination

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        return super(AppBaseViewSet, self).list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super(AppBaseViewSet, self).retrieve(request, *args, **kwargs)


"""
    ViewSet without token
"""


class BaseViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
