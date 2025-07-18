from django.urls import path
from . import views
from .views import CustomPasswordResetConfirmView
from django.contrib.auth import views as auth_views
app_name = 'users'

urlpatterns = [
    path('verify-email/<uidb64>/<token>/', views.verify_email_confirm, name='verify_email_confirm'),
    path('resend-verification-email/', views.resend_verification_email, name='resend_verification_email'),
    path('reset-password-confirm/<uidb64>/<token>/', 
            CustomPasswordResetConfirmView.as_view(), 
            name='password_reset_confirm'),

    path('reset-password-complete/', 
            auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
            name='password_reset_complete'),
]