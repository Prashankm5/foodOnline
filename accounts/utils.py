from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def detectUser(user):
    if user.role == 1:
        redirecturl = "vendorDashboard"
    elif user.role == 2:
        redirecturl = "custDashboard"
    elif user.role == None and user.is_superadmin:
        redirecturl = "/admin"
    return redirecturl


def send_verification_email(request, user, email_subject, email_template):
    current_site = get_current_site(request)
    message = render_to_string(email_template,{
        'user':user,
        'domain':current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user)
    })
    to_email = user.email
    mail = EmailMessage(email_subject, message, to=[to_email])
    mail.send()

def send_notification(email_subject, email_template, context):
    message = render_to_string(email_template,context)
    to_email = context['user'].email
    mail = EmailMessage(email_subject, message, to=[to_email])
    mail.send()



