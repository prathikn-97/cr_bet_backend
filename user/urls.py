from django.urls import path, include
from rest_framework import routers

from . import views
from .views import UserTokenVerifyView

app_name = 'user'

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.UserAuthenticationView.as_view()),
    path('token/verify/', UserTokenVerifyView.as_view()),
    path('token/refresh/', views.CustomTokenRefreshView.as_view()),
    path('password_reset/request/', views.ResetPasswordRequestToken.as_view()),
    path('password_reset/confirm/', views.ResetPasswordConfirm.as_view()),
    path('password_reset/validate_token/', views.ResetPasswordValidateToken.as_view()),
]
