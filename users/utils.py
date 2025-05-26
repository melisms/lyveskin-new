from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

def send_welcome_email(username, email):
    subject = 'Welcome to LyveSkin!'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [email]
    
    context = {
        'username': username,
    }

    html_content = render_to_string('users/welcome_email.html', context)
    text_content = f"Hi {username},\nThank you for registering with LyveSkin. We're thrilled to have you!"

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
    
def verify_email(user):
    subject = 'Email Verification'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]
    
    context = {
        'email': user.email,
    }

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = reverse('users:verify_email_confirm', kwargs={'uidb64': uid, 'token': token})
    verify_link = f"{settings.SITE_URL}{verify_url}"

    context = {
        'username': user.username,
        'verify_link': verify_link
    }

    html_content = render_to_string('users/verify_email.html', context)
    text_content = f"Hi {user.username},\nPlease verify your email: {verify_link}"

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)