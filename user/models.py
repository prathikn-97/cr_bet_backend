import arrow
import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField

from cr_bet_backend.base import tokens
from cr_bet_backend.base.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(email=self.normalize_email(email), password=password, **kwargs)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Personal Info
    username = models.CharField(max_length=256, verbose_name=_("Username"), blank=True, null=True)
    email = models.EmailField(verbose_name=_("Email"), max_length=60, unique=True)
    first_name = models.CharField(max_length=256, verbose_name=_("First Name"), blank=True, null=True)
    last_name = models.CharField(max_length=256, verbose_name=_("Last Name"), blank=True, null=True)
    mobile = models.CharField(max_length=15, verbose_name=_("Mobile Number"), blank=True, null=True)

    # Extra Info
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        ordering = ("-id",)

    def save(self, *args, **kwargs):
        if not self.username:
            if self.mobile:
                self.username = self.mobile
            else:
                self.username = self.email
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.email)

    @property
    def get_short_name(self):
        return self.username

    @property
    def get_full_name(self):
        if self.first_name and self.last_name:
            full_name = "{} {}".format(str(self.first_name), str(self.last_name))
        elif self.first_name and not self.last_name:
            full_name = self.first_name
        elif self.last_name and not self.first_name:
            full_name = self.last_name
        elif self.username:
            full_name = self.username
        else:
            full_name = self.email
        return full_name

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    @property
    def created_on_arrow(self):
        return arrow.get(self.date_joined).humanize()


TOKEN_GENERATOR_CLASS = tokens.get_token_generator()


class GenerateToken(models.Model):
    class Meta:
        verbose_name = _("Password Reset Token")
        verbose_name_plural = _("Password Reset Tokens")

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return TOKEN_GENERATOR_CLASS.generate_token()

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='password_reset_tokens', on_delete=models.CASCADE,
                             verbose_name=_("The User which is associated to this password reset tokens"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("When was this tokens generated"))
    key = models.CharField(_("Key"), max_length=64, db_index=True, unique=True)
    ip_address = models.GenericIPAddressField(_("The IP address of this session"), default="", blank=True, null=True, )
    user_agent = models.CharField(max_length=256, verbose_name=_("HTTP User Agent"), default="", blank=True, )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(GenerateToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset tokens for user {user}".format(user=self.user)


def get_password_reset_token_expiry_time():
    return getattr(settings, 'DJANGO_REST_MULTI_TOKEN_AUTH_RESET_TOKEN_EXPIRY_TIME', 24)


def get_password_reset_lookup_field():
    return getattr(settings, 'DJANGO_REST_LOOKUP_FIELD', 'email')


def clear_expired(expiry_time):
    GenerateToken.objects.filter(created_at__lte=expiry_time).delete()


def eligible_for_reset(self):
    if not self.is_active:
        return False

    if getattr(settings, 'DJANGO_REST_MULTI_TOKEN_AUTH_REQUIRE_USABLE_PASSWORD', True):
        return self.has_usable_password()
    else:
        return True


class Profile(BaseModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    phone = PhoneNumberField(null=True, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_of_joining = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        unique_together = (("user",),)
        ordering = ("-id",)


User.add_to_class("eligible_for_reset", eligible_for_reset)