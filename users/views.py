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
from .utils import send_welcome_email

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            send_welcome_email(username, email)
            messages.success(request, f'Your account has been created! Welcome {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})
@login_required
def profile(request, id):
    user = get_object_or_404(User, id=id)
    
    try:
        user_profile = user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=user)

    return render(request, 'users/profile.html', {'user_profile': user_profile})


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')

from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def update_settings(request):
    user = request.user

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

        elif form_type == 'change_email':
            new_email = request.POST.get('email')
            if new_email and new_email != user.email:
                user.email = new_email
                user.save()
                messages.success(request, "Email updated.")
            else:
                messages.warning(request, "Please enter a new and different email.")

                

    try:
        profile = user.userprofile
    except ObjectDoesNotExist:
        profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # PROFİL RESMİ GÜNCELLEME
        if form_type == 'profile_picture' and request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            messages.success(request, 'Your profile photo has been updated.')
            return redirect('profile', user.id)

        # ŞİFRE GÜNCELLEME
        elif form_type == 'change_password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password and confirm_password and current_password:
                if new_password == confirm_password:
                    if user.check_password(current_password):
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)  
                        messages.success(request, 'Your password has been changed successfully.')
                        return redirect('settings_page')
                    else:
                        messages.error(request, 'Your current password is incorrect.')
                else:
                    messages.error(request, 'The new passwords do not match.')

    return redirect('settings_page')


def settings_page(request):
    user = request.user

    try:
        profile = user.userprofile
    except ObjectDoesNotExist:
        profile = UserProfile.objects.create(user=user)

    if request.method == 'POST':

        if 'current_password' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('settings_page')


        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            return redirect('settings_page')

    return render(request, 'users/settings.html', {
        'user_profile': profile,
    })