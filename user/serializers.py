import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer, TokenVerifySerializer, TokenRefreshSerializer
)
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import AccessToken

from . import models

User = get_user_model()


class UserAuthenticationSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = self.user
        return data


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'mobile', 'first_name', 'last_name',
            'password', 'role'
        ]
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def __init__(self, *args, **kwargs):
        self.org = kwargs.pop("org", None)
        super(UserSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        role = validated_data.pop('role')
        try:
            with transaction.atomic():
                user = get_user_model().objects.create_user(**validated_data)
                profile, created = models.Profile.objects.get_or_create(user=user)
                if created:
                    profile.org = self.org
                    profile.date_of_joining = timezone.now()
                    profile.role = role
                    profile.save()
        except Exception as error:
            raise error
        return user

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user

    def validate_email(self, email):
        if self.instance:
            if self.instance.email != email:
                if not models.Profile.objects.filter(
                        user__email=email, org=self.org).exists():
                    return email
                raise serializers.ValidationError("Email already exists")
            return email
        else:
            if not models.Profile.objects.filter(user__email=email.lower(), org=self.org).exists():
                return email
            raise serializers.ValidationError('Given Email id already exists')


class ProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    @staticmethod
    def get_user_details(obj):
        return UserSerializer(obj.user).data

    class Meta:
        model = models.Profile
        fields = ("role", "phone", "alternate_phone", 'user_details')

    def __init__(self, *args, **kwargs):
        super(ProfileSerializer, self).__init__(*args, **kwargs)
        self.fields["alternate_phone"].required = False
        self.fields["role"].required = True
        self.fields["phone"].required = True


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=200)

    def validate(self, data):
        email = data.get("email")
        user = User.objects.filter(email__iexact=email).last()
        if not user:
            raise serializers.ValidationError(
                "You don't have an account. Please create one."
            )
        return data


class PasswordValidateMixin:

    @staticmethod
    def validate(data):
        token = data.get('token')
        password_reset_token_validation_time = models.get_password_reset_token_expiry_time()

        try:
            reset_password_token = _get_object_or_404(models.GenerateToken, key=token)
        except (TypeError, ValueError, ValidationError, Http404, models.GenerateToken.DoesNotExist):
            raise Http404(_("The OTP entered is not valid. Please check and try again."))

        expiry_date = reset_password_token.created_at + timedelta(
            hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
            reset_password_token.delete()
            raise Http404(_("The tokens has expired"))
        return data


class ResetTokenSerializer(PasswordValidateMixin, serializers.Serializer):
    token = serializers.CharField()


class PasswordTokenSerializer(PasswordValidateMixin, serializers.Serializer):
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})
    token = serializers.CharField()


class PasswordSetSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100)
    new_password = serializers.CharField(max_length=100)
    retype_password = serializers.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super(PasswordSetSerializer, self).__init__(*args, **kwargs)

    def validate_old_password(self, pwd):
        if not check_password(pwd, self.context.get('user').password):
            raise serializers.ValidationError("old password entered is incorrect.")
        return pwd

    def validate(self, data):
        if len(data.get('new_password')) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long!")
        if data.get('new_password') == data.get('old_password'):
            raise serializers.ValidationError(
                "New_password and old password should not be the same")
        if data.get('new_password') != data.get('retype_password'):
            raise serializers.ValidationError(
                "New_password and Retype_password did not match.")
        return data


def find_urls(string):
    website_regex = "^https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$"
    website_regex_port = "^https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,63}:[0-9]{2,4}$"
    url = re.findall(website_regex, string)
    url_port = re.findall(website_regex_port, string)
    if url and url[0] != "":
        return url
    return url_port


class UserTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        data = super(UserTokenVerifySerializer, self).validate(attrs)
        access_token_obj = AccessToken(attrs['token'])
        user_id = access_token_obj['user_id']
        try:
            user = User.objects.filter(id=user_id).first()
            if user is None:
                raise serializers.ValidationError({"data":"User not exist"})
        except:
            raise serializers.ValidationError('User not exist')
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    error_msg = 'No active account found with the given credentials'

    def validate(self, attrs):
        token_payload = token_backend.decode(attrs['refresh'])
        try:
            user = get_user_model().objects.get(pk=token_payload['user_id'])
        except get_user_model().DoesNotExist:
            raise exceptions.AuthenticationFailed(
                self.error_msg, 'no_account'
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                self.error_msg, 'no_active_account'
            )

        return super().validate(attrs)