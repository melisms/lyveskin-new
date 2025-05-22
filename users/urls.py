from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('verify-email/<uidb64>/<token>/', views.verify_email_confirm, name='verify_email_confirm'),
    path('resend-verification-email/', views.resend_verification_email, name='resend_verification_email'),
]