from allauth.account.auth_backends import AuthenticationBackend
from allauth.utils import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions


class CustomAuthenticationBackend(AuthenticationBackend):
    def authenticate(self, request, **credentials):
        ret = None
        username = credentials.get("username")
        phone = credentials.get("phone")
        password = credentials.get("password")
        email = credentials.get("email")
        if phone and password:
            ret = self._authenticate_by_phone(**credentials)

        elif username and password:
            ret = self._authenticate_by_username(**credentials)

        elif email and password:
            ret = self._authenticate_by_email(**credentials)


        return ret

    def _authenticate_by_phone(self, **credentials):
        phone = credentials.get("phone")
        password = credentials.get("password")
        User = get_user_model()

        if not phone or phone is None or password is None:
            return None
        try:
            user = User.objects.get(phone=phone)
            if self._check_password(user, password):
                return user
        except User.DoesNotExist:
            return None

    def _check_password(self, user, password):
        ret = user.check_password(password)
        if ret:
            ret = self.user_can_authenticate(user)
            if not ret:
                self._stash_user(user)
        return ret

    def user_can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None)
        if not is_active:
            msg = _('User account is disabled.')
            raise exceptions.ValidationError(msg)
        return is_active or is_active is None

