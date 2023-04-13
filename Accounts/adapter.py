from django.utils.translation import gettext_lazy as _
from allauth.account.adapter import DefaultAccountAdapter,AbstractUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from Accounts.models import User


class CustomUserAccountAdapter(DefaultAccountAdapter):

    def clean_phone(self, phone):
        if phone == "":
            raise ValidationError(_("phone number can't be empty"))
        else:
            if User.objects.filter(phone=phone):
                raise ValidationError(_("phone number not available for use.please change your number."))
        return phone

    def save_user(self, request, user, form, commit=True):
        from allauth.account.utils import user_field
        user = super().save_user(request, user, form, False)

        user_field(user, 'username', request.data.get('username', ''))
        user_field(user, 'password1', request.data.get('password1', ''))
        user_field(user, 'password2', request.data.get('password2', ''))
        user_field(user, 'email', request.data.get('email', ''))
        user_field(user, 'phone', request.data.get('phone', ''))
        user.save()
        return user




