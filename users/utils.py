from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

from .tokens import account_activation_token
from .variables import (ACTIVATE_EMAIL_SUBJECT, BAD_ACTIVATION, BAD_LOGIN,
                        BAD_RESET_PASSWORD_LINK, BAD_USER_ACCOUNT,
                        RESET_PASSWORD_EMAIL_SUBJECT)

User = get_user_model()


def send_email(subject, template, content, to):
    """
    Email template is specified and content (variables) will render in it.
    It will send an email due to the parameters by using django mail backend.
    """
    t = get_template(template)
    message = t.render(content)
    email = EmailMessage(subject, message, to=[to, ])
    email.content_subtype = "html"
    email.send()
    # pass


def send_activation_account_email(user):
    """
    Prepare email variable: mail subject + email template (content) + to(receiver email)
    Email data includes user(firstname) and activation link.
    Activation link consists decode user_id and a generated token.
    Token will generate by django PasswordResetTokenGenerator which is configured in
    token.py. After Collecting required data, it calls the function that is responsible
    for sending emails.
    """
    mail_subject = ACTIVATE_EMAIL_SUBJECT.get('en')
    token = account_activation_token.make_token(user)
    email_data = {
        'user': user,
        'domain': settings.FRONTEND_ACCOUNT_ACTIVATION_BASE_ADDRESS,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token,
    }

    template = 'acc_active_email.html'
    send_email(mail_subject, template, email_data, user.email)


def get_and_authenticate_user(request, email, password):
    """
    Authenticate user according the received email and password.
    If Authentication is successful return user, otherwise raise a bad request error.
    """
    user = authenticate(username=email, password=password)
    if user is None:
        raise serializers.ValidationError(BAD_LOGIN)
    login(request, user)
    return user


def create_user_account(
        email, password, first_name="", last_name="", **extra_fields):
    """
    Create a user according to the paramethers but set the activation status to
    the False, and send a activation link via email for confirming the email address.
    """
    user = User.objects.create_user(username=email,
                                    email=email,
                                    password=password,
                                    first_name=first_name,
                                    last_name=last_name,
                                    **extra_fields)
    user.is_active = False
    user.save()
    send_activation_account_email(user)
    return user


def activate_user_account(request, uidb64, token):
    """
    uidb64 is encoded user_id.
    For activation we need to decode uidb42 to get the user.
    If user is valid, then check the token (account activation token is generated
    with TokenGenerator()). So if the userid and timestamp and is_active status
    are the same the token is valid and we can set is_active to True, otherwise the
    token has revoked and it will raise an Error Response.
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
    else:
        raise serializers.ValidationError(BAD_ACTIVATION)
    return user


def send_reset_password_email(email):
    """
    Sends a reset password link via email for confirming the email address.
    """
    user = User.objects.get(username=email)
    mail_subject = RESET_PASSWORD_EMAIL_SUBJECT.get('en')
    token = PasswordResetTokenGenerator().make_token(user)
    email_data = {
        'user': user,
        'domain': settings.FRONTEND_RESET_PASSWORD_BASE_ADDRESS,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token,
    }
    template = 'reset_password_email.html'
    send_email(mail_subject, template, email_data, user.email)


def check_password_reset_permission(request, uidb64, token):
    """
    uidb64 is encoded user_id.
    For activation we need to decode uidb42 to get the user.
    If user is valid, then check the token (reset password token). So if the token
    is not valid it will raise an Error Response, otherwise we can return user to 
    send required token needed for reset password authorization.
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        return user
    else:
        raise serializers.ValidationError(BAD_RESET_PASSWORD_LINK)


def change_password(request, new_password):
    try:
        request.user.set_password(new_password)
        request.user.save()
    except(User.DoesNotExist):
        raise serializers.ValidationError(BAD_USER_ACCOUNT)
