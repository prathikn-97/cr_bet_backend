from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.conf import settings
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status, exceptions
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView, TokenRefreshView
from rest_framework import viewsets, status, parsers, filters
from utils.helpers import get_user
from . import models
from . import serializers
from . import signals
from cr_bet_backend.base.auth import BaseViewSet, AppBaseViewSet
from cr_bet_backend.base.auth.baseViewSet import CustomResultsSetPagination
import stripe
import requests

User = get_user_model()

HTTP_USER_AGENT_HEADER = getattr(
    settings, 'DJANGO_REST_PASSWORD_RESET_HTTP_USER_AGENT_HEADER', 'HTTP_USER_AGENT')
HTTP_IP_ADDRESS_HEADER = getattr(
    settings, 'DJANGO_REST_PASSWORD_RESET_IP_ADDRESS_HEADER', 'REMOTE_ADDR')


class UserAuthenticationView(TokenObtainPairView):
    serializer_class = serializers.UserAuthenticationSerializer

    def post(self, request, *args, **kwargs):
        super(UserAuthenticationView, self).post(request, *args, **kwargs)

        device_token = request.data.get("device_token", None)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # if device_token:
        #     if not FCMDevice.objects.filter(registration_id=device_token, user_id=user.id).exists():
        #         FCMDevice.objects.create(
        #             user_id=user.id, registration_id=device_token)
        refresh = self.serializer_class.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'email': user.email,
            'user_id': user.id,
            'username': user.username,
        }
        return Response({
            'data': data,
            "error": False,
            "message": "User Authenticated Successfully.",
        }, status=status.HTTP_201_CREATED)


class UserViewSet(AppBaseViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ('email',)

    def list(self, request, *args, **kwargs):
        orgs_users = models.Profile.objects.filter(
            role="STAFF").values_list('user')
        user_ids = []
        for user_id in orgs_users:
            user_ids.append(user_id[0])
            
        queryset = self.filter_queryset(self.queryset.filter(id__in=user_ids))
        serializer = self.get_serializer(queryset, org=request.org, context={
            'request': request}, many=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, org=request.org, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'data': serializer.data,
            "error": False,
            "message": "User Created Successfully.",
        }, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=True, url_path='user-exists')
    def check_user_exists(self, request, pk=None):
        response = models.User.objects.filter(mobile=pk).exists()
        return Response({
            'success': response},
            status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='change-password')
    def set_password(self, request, pk=None):
        serializer = serializers.PasswordSetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = models.User.objects.get(mobile=pk)
        response.set_password(request.data['password'])
        response.save()
        return Response({
            'message': 'successfully reset password.',
            'success': True},
            status=status.HTTP_200_OK)


class ResetPasswordValidateToken(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    serializer_class = serializers.ResetTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'status': 'OK'})


class UserTokenVerifyView(TokenVerifyView):
    serializer_class = serializers.UserTokenVerifySerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = serializers.CustomTokenRefreshSerializer


class ResetPasswordConfirm(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    serializer_class = serializers.PasswordTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        token = serializer.validated_data['token']

        reset_password_token = models.GenerateToken.objects.filter(
            key=token).first()

        if reset_password_token.user.eligible_for_reset():
            signals.pre_password_reset.send(
                sender=self.__class__, user=reset_password_token.user)
            try:
                validate_password(
                    password,
                    user=reset_password_token.user,
                    password_validators=get_password_validators(
                        settings.AUTH_PASSWORD_VALIDATORS)
                )
            except ValidationError as e:
                raise exceptions.ValidationError({
                    'password': e.messages
                })

            reset_password_token.user.set_password(password)
            reset_password_token.user.save()
            signals.post_password_reset.send(
                sender=self.__class__, user=reset_password_token.user)

        models.GenerateToken.objects.filter(
            user=reset_password_token.user).delete()

        return Response({'status': 'OK'})


class ResetPasswordRequestToken(GenericAPIView):
    throttle_classes = ()
    permission_classes = ()
    serializer_class = serializers.ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        password_reset_token_validation_time = models.get_password_reset_token_expiry_time()
        now_minus_expiry_time = timezone.now(
        ) - timedelta(hours=password_reset_token_validation_time)
        models.clear_expired(now_minus_expiry_time)

        users = User.objects.filter(
            **{'{}__iexact'.format(models.get_password_reset_lookup_field()): email})
        active_user_found = False

        for user in users:
            if user.eligible_for_reset():
                active_user_found = True

        if not active_user_found and not getattr(settings, 'DJANGO_REST_PASSWORD_RESET_NO_INFORMATION_LEAKAGE', False):
            raise exceptions.ValidationError({
                'email': [_(
                    "We couldn't find an account associated with that mobile. Please try a different email.")],
            })

        for user in users:
            if user.eligible_for_reset():
                if user.password_reset_tokens.all().count() > 0:
                    token = user.password_reset_tokens.all()[0]
                else:
                    token = models.GenerateToken.objects.create(
                        user=user,
                        user_agent=request.META.get(
                            HTTP_USER_AGENT_HEADER, ''),
                        ip_address=request.META.get(
                            HTTP_IP_ADDRESS_HEADER, ''),
                    )
                signals.reset_password_token_created.send(
                    sender=self.__class__, instance=self, reset_password_token=token
                )
        return Response({'status': 'OTP sent to Registered Mobile Number'})
