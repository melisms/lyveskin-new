from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

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