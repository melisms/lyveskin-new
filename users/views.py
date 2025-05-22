from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from item.models import Item
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .utils import send_welcome_email, verify_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import logout

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
    
    try:
        user_profile = user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=user)

    email_verified = getattr(user_profile, 'email_verified', False)
    return render(request, 'users/profile.html', {'user_profile': user_profile, 'email_verified': email_verified})

def resend_verification_email(request):
    user = request.user
    if not user.userprofile.email_verified:
        verify_email(user)
        messages.success(request, 'Verification email has been resent.')
    return redirect('settings_page')

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')


    user = request.user

    try:
        profile = user.userprofile
    except ObjectDoesNotExist:
        profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'change_username':
            new_username = request.POST.get('username')
            if new_username and new_username != user.username:
                user.username = new_username
                user.save()
                messages.success(request, "Username updated.")
            else:
                messages.warning(request, "Please enter a new and different username.")

        elif form_type == 'change_firstname':
            new_firstname = request.POST.get('firstname')
            if new_firstname and new_firstname != user.first_name:
                user.first_name = new_firstname
                user.save()
                messages.success(request, "Firstname updated.")
            else:
                messages.warning(request, "Please enter a new and different firstname.")

        
        elif form_type == 'change_lastname':
            new_lastname = request.POST.get('last_name')
            if new_lastname and new_lastname != user.last_name:
                user.last_name = new_lastname
                user.save()
                messages.success(request, "Lastname updated.")
            else:
                messages.warning(request, "Please enter a new and different lastname.")

        # E-POSTA GÜNCELLEME
        elif form_type == 'change_email':
            new_email = request.POST.get('email')
            if new_email and new_email != user.email:
                user.email = new_email
                user.save()
                messages.success(request, "Email updated.")
            else:
                messages.warning(request, "Please enter a new and different email.")

        # PROFİL RESMİ GÜNCELLEME
        elif form_type == 'profile_picture':
            picture = request.FILES.get('profile_picture')
            if picture:
                profile.profile_picture = picture
                profile.save()
                messages.success(request, 'Your profile photo has been updated.')

        # ŞİFRE GÜNCELLEME
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
                    else:
                        messages.error(request, 'Your current password is incorrect.')
                else:
                    messages.error(request, 'New passwords do not match.')

    return redirect('settings_page')

def update_settings(request):
    user = request.user

    try:
        profile = user.userprofile
    except ObjectDoesNotExist:
        profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'change_username':
            new_username = request.POST.get('username')
            if new_username and new_username != user.username:
                user.username = new_username
                user.save()
                messages.success(request, "Username updated.")
            else:
                messages.warning(request, "Please enter a new and different username.")

        elif form_type == 'change_firstname':
            new_firstname = request.POST.get('firstname')
            if new_firstname and new_firstname != user.first_name:
                user.first_name = new_firstname
                user.save()
                messages.success(request, "Firstname updated.")
            else:
                messages.warning(request, "Please enter a new and different firstname.")

        elif form_type == 'change_lastname':
            new_lastname = request.POST.get('last_name')
            if new_lastname and new_lastname != user.last_name:
                user.last_name = new_lastname
                user.save()
                messages.success(request, "Lastname updated.")
            else:
                messages.warning(request, "Please enter a new and different lastname.")

        elif form_type == 'change_email':
            new_email = request.POST.get('email')
            if new_email and new_email != user.email:
                user.email = new_email
                user.save()
                profile.email_verified = False
                profile.save()
                verify_email(user)
                messages.success(request, "Email updated. Please verify your new email.")
            else:
                messages.warning(request, "Please enter a new and different email.")

        elif form_type == 'profile_picture':
            picture = request.FILES.get('profile_picture')
            if picture:
                profile.profile_picture = picture
                profile.save()
                messages.success(request, 'Your profile photo has been updated.')

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
                    else:
                        messages.error(request, 'Your current password is incorrect.')
                else:
                    messages.error(request, 'New passwords do not match.')

    return redirect('settings_page')

def settings_page(request):
    user = request.user

    try:
        profile = user.userprofile
    except ObjectDoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    email_verified = getattr(profile, 'email_verified', False)

    return render(request, 'users/settings.html', {
        'user_profile': profile,
        'email_verified': email_verified,
        'user': user,
    })
