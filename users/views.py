from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import update_session_auth_hash, logout
from .models import UserProfile
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from item.models import Item
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .utils import send_welcome_email, verify_email, send_password_reset_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.cache import cache
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse

CACHE_TIMEOUT = 60 * 5

def get_settings_cache_key(user_id):
    return f"settings_page_user_{user_id}"

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            send_welcome_email(username, email)
            verify_email(user)
            messages.success(request, f'Your account has been created! Please check your email to verify it.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

def verify_email_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.email_verified = True
        profile.save()
        messages.success(request, "Your email has been verified!")
        return redirect('login')
    else:
        messages.error(request, "Verification link is invalid or expired.")
        return redirect('login')

@login_required
def profile(request, id):
    user = get_object_or_404(User, id=id)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    email_verified = getattr(profile, 'email_verified', False)
    return render(request, 'users/profile.html', {'user_profile': profile, 'email_verified': email_verified})
@login_required
def resend_verification_email(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    if not profile.email_verified:
        verify_email(user)
        messages.success(request, 'Verification email has been resent.')
    return redirect('settings_page')

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')

@login_required
def update_settings(request):
    if request.method != 'POST':
        return redirect('settings_page')
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    form_type = request.POST.get('form_type')
    cache_key = get_settings_cache_key(user.id)
    
    def clear_cache():
        cache.delete(cache_key)
        
    if form_type == 'change_username':
        new_username = request.POST.get('username')
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                messages.warning(request, "Username already taken.")
            else:
                user.username = new_username
                user.save()
                messages.success(request, "Username updated.")
                clear_cache()
        else:
            messages.warning(request, "Please enter a new and different username.")

    elif form_type == 'change_fullname':
        new_firstname = request.POST.get('first_name')
        new_lastname = request.POST.get('last_name')

        updated = False

        if new_firstname and new_firstname != user.first_name:
            user.first_name = new_firstname
            updated = True

        if new_lastname and new_lastname != user.last_name:
            user.last_name = new_lastname
            updated = True

        if updated:
            user.save()
            messages.success(request, "Your name has been updated.")
            clear_cache()
        else:
            messages.warning(request, "Please enter a new and different name.")

    elif form_type == 'change_email':
        new_email = request.POST.get('email')
        if new_email and new_email != user.email:
            user.email = new_email
            user.save()
            profile.email_verified = False
            profile.save()
            verify_email(user)
            messages.success(request, "Email updated. Please verify your new email.")
            clear_cache()
        else:
            messages.warning(request, "Please enter a new and different email.")

    elif form_type == 'profile_picture':
        picture = request.FILES.get('profile_picture')
        if picture:
            profile.profile_picture = picture
            profile.save()
            messages.success(request, 'Your profile photo has been updated.')
            clear_cache()

    elif form_type == 'change_password':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if current_password and new_password and confirm_password:
            if new_password == confirm_password:
                if user.check_password(current_password):
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Your password has been changed successfully.')
                    clear_cache()
                else:
                    messages.error(request, 'Your current password is incorrect.')
            else:
                messages.error(request, 'New passwords do not match.')

    return redirect('settings_page')

@login_required
def settings_page(request):
    cache_key = get_settings_cache_key(request.user.id)
    user_data = cache.get(cache_key)
    
    if not user_data:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        email_verified = getattr(profile, 'email_verified', False)
        user_data = {
            'user_profile': profile,
            'email_verified': email_verified,
            'user': request.user,
        }
        cache.set(cache_key, user_data, CACHE_TIMEOUT)
    response = render(request, 'users/settings.html', user_data)
    list(get_messages(request))
    return response

def forgot_password_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email)
            for user in users:
                send_password_reset_email(user)
            messages.success(request, "If that email exists in our system, we've sent a reset link.")
            return redirect('forgot_password')
    else:
        form = PasswordResetForm()
    return render(request, "users/request_email.html", {"form": form})

from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/new_password.html'
    success_url = reverse_lazy('users:password_reset_complete')