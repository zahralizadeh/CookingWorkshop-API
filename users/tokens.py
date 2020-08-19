import six

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    """
    This TokenGenrator is used for generating account activation token,
    for activation links. 
    Tokens generated ragarding to the user_id, timestamp and is_active status 
    of the user.
    """

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()
