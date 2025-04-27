from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from item.models import Item
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! Welcome {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})
@login_required
def profile(request, id):
    user = get_object_or_404(User, id=id)
    return render(request, 'users/profile.html', {'user_profile': user})


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')

from django.shortcuts import render, redirect
from django.contrib import messages


def update_settings(request):
    if request.method == 'POST':
        user = request.user

        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']

        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and confirm_password and current_password:
            if new_password == confirm_password:
                if user.check_password(current_password):
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Şifreniz başarıyla değiştirildi.')
                    return redirect('login')
                else:
                    messages.error(request, 'Mevcut şifreniz yanlış.')
            else:
                messages.error(request, 'Yeni şifreler eşleşmiyor.')

        user.save()
        return redirect('profile', user.id)
    else:
        return redirect('profile', request.user.id)

def settings_page(request):
    return render(request, 'users/settings.html', {'user_profile': request.user})
