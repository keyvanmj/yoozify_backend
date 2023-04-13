from dj_rest_auth.serializers import LoginSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from .models import PhoneOTP, Profile
from Accounts.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
    from allauth.utils import email_address_exists, get_username_max_length
except ImportError:
    raise ImportError('allauth needs to be added to INSTALLED_APPS.')

User = get_user_model()


class PhoneNumberSerializer(serializers.Serializer):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{11,13}$', message=_(
        "Phone number must be entered in the format: '09***' or '+989***. Up to 11 or 13 digits allowed."))
    phone = serializers.CharField(validators=[phone_regex], max_length=17)


class CustomRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED,
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{11,13}$',
                                 message=_(
                                     "phone number must be entered in the format: '09***' or '+989***. up to 11 or 13 digits allowed."))
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_phone(self, phone):
        phone = get_adapter().clean_phone(phone)
        if phone == "":
            raise ValidationError(_("phone number can't be empty"))
        else:
            if User.objects.filter(phone=phone):
                raise ValidationError(_("phone number not available for use"))
        return phone

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _('A user is already registered with this e-mail address.'),
                )
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'phone': self.validated_data.get('phone', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)

        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class CreateUserSerialzier(serializers.HyperlinkedModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'email', 'password1', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise serializers.ValidationError(
                _('A user is already registered with this e-mail address.'),
            )
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):

        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'phone': self.validated_data.get('phone', '')
        }

    def save(self, request):
        from .adapter import CustomUserAccountAdapter
        # adapter = get_adapter()
        adapter = CustomUserAccountAdapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)

        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        setup_user_email(request, user, [])
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'image']

    def update(self, instance, validated_data):

        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        image = validated_data.get('image')
        if first_name:
            instance.profile.first_name = first_name
        if last_name:
            instance.profile.last_name = last_name
        if image:
            instance.profile.image = image
        instance.profile.save()
        instance.save()
        return super(ProfileSerializer, self).update(instance,validated_data)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['email', 'username', 'phone', 'profile']
        read_only_fields = ('phone',)

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        try:
            self.fields['username'].initial = request.user.username
            self.fields['email'].initial = request.user.email
            self.fields['phone'].initial = request.user.phone
        except:
            pass

    def to_representation(self, instance):
        request = self.context.get('request')
        ret = super(UserSerializer, self).to_representation(instance)
        profile_model = Profile.objects.filter(user_id=instance.pk)
        if request.path_info == reverse('users_view'):
            profile = reverse('profiles_view',kwargs={'pk':instance.pk},request=request)
            ret['image'] = instance.images(request)
            ret['profile'] = profile

        return ret

    def validate(self, attrs):
        phone = attrs.get('phone')
        if phone:
            if User.objects.filter(phone=phone).exists():
                if User.objects.filter(phone=phone).count() > 1:
                    msg = {'detail': 'Phone number is already associated with another user. Try a new one.',
                           'status': False}
                    raise serializers.ValidationError(msg)

        return attrs

    def get_fields(self, *args, **kwargs):
        fields = super(UserSerializer, self).get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        try:
            self.instance = request.user

            profile = Profile.objects.get(user_id=self.instance.pk)
            self.instance.profile = profile

            if request and getattr(request, 'method', None) == "PUT":
                fields['username'].required = False
                fields['phone'].required = False

        except:
            pass
        return fields

    def create(self, validated_data):
        return validated_data

    def update(self, instance, validated_data):
        request = self.context['request']
        try:
            username = validated_data.get('username')
            email = validated_data.get('email')
            if username:
                instance.username = username
            if email:
                instance.email = email

            instance.profile.save()
            instance.save()
        except:
            pass
        return super(UserSerializer, self).update(instance,validated_data)



class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    phone = serializers.SerializerMethodField()
    password = serializers.CharField(style={'input_type': 'password'})
    remember_me = serializers.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(LoginUserSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request.path_info == reverse('login_phone_otp'):
            phone_regex = RegexValidator(regex=r'^\+?1?\d{11,13}$', message=_(
                "phone number must be entered in the format: '09***' or '+989***. up to 11 or 13 digits allowed."))

            self.fields['phone'] = serializers.CharField(validators=[phone_regex], max_length=17)
            self.fields['username'] = serializers.HiddenField(default='')

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        phone = attrs.get('phone')
        user = None
        if username and password:
            if User.objects.filter(username=username).exists():
                user = self.authenticate(username=username, password=password)
                if not user:
                    msg = _('Unable to log in with provided credentials.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = {'detail': _('this username is not registered.'), 'login': False,
                       'register_url': reverse('register_otp',request=self.context.get('request'))}
                raise serializers.ValidationError(msg)

        elif phone and password:
            if User.objects.filter(phone=phone).exists():
                user = self.authenticate(phone=phone, password=password)
                if not user:
                    msg = _('Unable to log in with provided credentials.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = {'detail': _('this phone is not registered.'), 'login': False,
                       'register_url': reverse('register_otp',request=self.context.get('request'))}
                raise serializers.ValidationError(msg)

        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        self.validate_auth_user_status(user)
        attrs['user'] = user
        return attrs


    def authenticate(self, **kwargs):
        request = self.context['request']
        if not request.data.get('remember_me'):
            request.session.set_expiry(0)
        else:
            pass

        return authenticate(request, **kwargs)

    def _validate_email(self, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_phone(self, phone, password):

        if phone and password:
            user = self.authenticate(phone=phone, password=password)
        else:
            msg = _('Must include "phone" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email_phone(self, username, phone, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)

        elif phone and password:
            user = self.authenticate(phone=phone, password=password)

        else:
            if self.context['request'].path_info == reverse('login_phone_otp'):
                msg = _('Must include either "phone" and "password".')
            else:
                msg = _('Must include either "username" or "email" and "password".')

            raise exceptions.ValidationError(msg)

    def get_auth_user_using_orm(self, username, phone, email, password):
        if email:
            try:
                username = User.objects.get(email__iexact=email).get_username()
            except User.DoesNotExist:
                pass

        if username:
            return self._validate_username_email_phone(username, '', '', password)

        if phone:
            return self._validate_username_email_phone('', phone, '', password)

        return None

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.ValidationError(msg)




class ChangePasswordSerializer(serializers.HyperlinkedModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ('old_password', 'password')

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({'old_password': "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    otp = serializers.HiddenField(default='')

    def validate_new_password(self, password):
        return get_adapter().clean_password(password)

class SendOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone']


