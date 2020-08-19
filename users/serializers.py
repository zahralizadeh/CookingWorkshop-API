from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .variables import EMAIL_ALREADY_TAKEN, EMAIL_NOT_EXIST, INVALID_PASSWORD

User = get_user_model()


class UserLoginSerializer (serializers.Serializer):
    """
    A User Serializer for login the user
    """
    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    """
    A User Serializer for registring the user
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', ]

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if user:
            raise serializers.ValidationError(EMAIL_ALREADY_TAKEN)
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    We expect two fields for changing user's password, current and new psswords.
    For current_password, we make sure that it is the current password of the
    user, accessed through context(this is passed automatically through the view)
    and has a check_password method associated with it. If it doesn’t match, then 
    a ValidationError is raised. 
    The new_password is validated via django validate_password method. it Validates
    a password. If all validators find the password valid configuration
    (settings.py), returns None. If one or more validators reject the password, 
    raises a ValidationError with all the error messages from the validators.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(INVALID_PASSWORD)
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Validate the email address sent by the user, if there is a user associated with
    this email then it will be ok, otherwise a ValidationError is raised.
    """
    email = serializers.CharField(max_length=300, required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except:
            user = None
        if user is None:
            raise serializers.ValidationError(EMAIL_NOT_EXIST)
        return value


class TokenSerializerDone(serializers.Serializer):
    """
    This serializer is used for the Validation of links related to requesting 
    password reset or account activation.
    """
    uidb64 = serializers.CharField(max_length=20, required=True)
    token = serializers.CharField(max_length=100, required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """
    We expect a new password to reset user's password. 
    The new_password is validated via django validate_password method. It Validates
    a password. If all validators find the password valid configuration
    (settings.py), returns None. If one or more validators reject the password, 
    raises a ValidationError with all the error messages from the validators.
    """
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class AuthUserSerializer(serializers.ModelSerializer):
    """
    A User Serializer for sending response. In addition to User model,
    this serializer creates and publishes valid tokens (using DRF auth_token class).
    Later this token can be checked for authorizating user's requests.
    """
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name',
                  'last_name', 'is_active', 'is_staff', 'auth_token', 'last_login']
        read_only_fields = ['id', 'is_active', 'is_staff']

    def get_auth_token(self, obj):
        token = Token.objects.get_or_create(user=obj)[0]
        return token.key


class EmptySerializer(serializers.Serializer):
    pass
