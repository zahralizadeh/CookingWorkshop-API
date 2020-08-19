from django.contrib.auth import get_user_model, logout
from django.core.exceptions import ImproperlyConfigured
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .utils import (activate_user_account, change_password,
                    check_password_reset_permission, create_user_account,
                    get_and_authenticate_user, send_reset_password_email)
from .variables import ACTIVATE_YOUR_ACCOUNT, RESET_PASSWORD_LINK_EMAILED

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """
    actions:
    - login
    - register and  activate account
    - logout
    - change password
    - forgot password (including initial request + verify request + reset password)
    At the first step the serializer class would be an empty serializer.
    The serializer_classes is a list of corresponding serializer of each action,
    and get_serializer_class helps to find the regarding class of each action 
    function. 
    """
    permission_classes = [AllowAny, ]
    serializer_class = serializers.EmptySerializer
    serializer_classes = {
        'login': serializers.UserLoginSerializer,
        'register': serializers.RegisterSerializer,
        'activate': serializers.TokenSerializerDone,
        'change_password': serializers.ChangePasswordSerializer,
        'forgot_password': serializers.ForgotPasswordSerializer,
        'forgot_password_done': serializers.TokenSerializerDone,
        'reset_password': serializers.ResetPasswordSerializer,
    }

    @action(methods=['POST', ], detail=False)
    def login(self, request):
        """
        Fill the UserLoginSerializer with the user sent data (email + password)
        if the serializer is valid then authenticate the user and send the proper
        response using AuthUserSerializer.
        Check the API documentaion for more informtion.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(request, **serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def register(self, request):
        """
        Fill the RegisterSerializer with the user data, and if the serializer is
        valid the create the user (but deactivate user) and if the process is 
        successful then inform user to check her email to activate her account.
        Check the API documentaion for more informtion.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = ACTIVATE_YOUR_ACCOUNT
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST', ], detail=False)
    def activate(self, request):
        """
        Get the encoded user_id(uidb64) and token form the request and check the validation,
        and send the user response via AuthUserSerializer.
        Check the API documentaion for more informtion.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = activate_user_account(request, **serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', 'GET', ], detail=False)
    def logout(self, request):
        """
        Since we don’t require any serializer for logout action, we haven’t
        defined any in serializer_classes dictionary. It will fall back to use 
        the EmptySerializer which does not accept anything.  I used Django’s 
        logout method for logging out from the current session and provide a 
        successful 200 OK response.
        Check the API documentaion for more informtion.
        """
        logout(request)
        data = {'success': 'Successfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def change_password(self, request):
        """
        Validate recieved data from user, if the data was valid then update the 
        user's password.
        Check the API documentaion for more informtion.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password(request, serializer.validated_data['new_password'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', ], detail=False)
    def forgot_password(self, request):
        """
        Get an email as a request of resetting the password, and if the serializer
        is valid then send an email to user to reset her password.
        Check the API documentaion for more informtion.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_reset_password_email(**serializer.validated_data)
        data = RESET_PASSWORD_LINK_EMAILED
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def forgot_password_done(self, request):
        """
        Get the encoded user_id(uidb64) and token and if the serializer is valid,
        then send the OK response via AuthUserSerializer tell Frontend that it is
        possible to reset the password as well as publish the token required for
        reset the password.
        Check the API documentaion for more informtion.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = check_password_reset_permission(
            request, **serializer.validated_data)
        data = serializers.AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False, permission_classes=[IsAuthenticated, ])
    def reset_password(self, request):
        """
        User should be Authorized by token for this  action, if so reset the user's
        password.
        Check the API documentaion for more informtion.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        """
        This function helps to find the regarding class of each action function.
        """
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured(
                "serializer_classes should be a dict mapping")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]

        return super().get_serializer_class()
