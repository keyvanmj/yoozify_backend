from dj_rest_auth.views import LoginView
from django.contrib.auth.tokens import default_token_generator
from django.utils.text import format_lazy

from .models import PhoneOTP, ChangePhone, Profile
from .permissions import IsOwnerOrAdmin, UpdateOwnProfile
from .serializers import (CreateUserSerialzier,
                          ChangePasswordSerializer,
                          LoginUserSerializer,
                          ForgotPasswordSerializer, SendOTPSerializer)
from rest_framework import generics, status

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import permissions,parsers
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from Accounts.models import User
from .serializers import PhoneNumberSerializer, UserSerializer, ProfileSerializer
from django.utils.translation import gettext_lazy as _
from .utils import send_otp, send_after_seconds


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password1', 'password2'),
)


class UserView(generics.ListAPIView):
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]


    def get_queryset(self):
        qs = User.objects.filter(is_staff=True)
        return qs


class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (permissions.AllowAny,)
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]


    def get_queryset(self):
        queryset = None
        try:
            queryset = get_object_or_404(Profile,user_id=self.kwargs.get('pk',None))
        except:
            pass
        return queryset

    def get_object(self):
        profile_qs = self.get_queryset()
        profile_serializer = ProfileSerializer(profile_qs,context={'request':self.request})
        return Response(profile_serializer.data)

    def retrieve(self, request, *args, **kwargs):
        object_detail = self.get_object().data
        return Response(data=object_detail)


class PhoneView(generics.RetrieveUpdateAPIView):

    queryset = User.objects.all()
    serializer_class = PhoneNumberSerializer
    permission_classes = (IsOwnerOrAdmin,permissions.IsAuthenticated)
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):

        """user current phone number """

        old_phone = request.user.phone
        return Response({'phone number ': old_phone})

    def put(self, request, *args, **kwargs):

        """updating phone number using confirmation link"""

        serializer = self.serializer_class(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        new_phone = request.data.get('phone')
        all_users = User.objects.all()
        user = self.get_object()
        if new_phone in all_users.values_list('phone', flat=True):
            return Response({'detail': _("phone number not available for use")})
        confirmation_token = default_token_generator.make_token(user)
        confirmation_link = f'{reverse("change_phone", request=request)}?user_id={user.id}&confirmation_token={confirmation_token}'
        message = f' برای ثبت شماره تلفن همراه خود بر روی زیر لینک کلیک کنید: \n{confirmation_link}'
        # send_sms_code(phone=new_phone,otp=confirmation_link,message=message)
        change = ChangePhone()
        change.user = user
        change.phone = new_phone
        change.code = confirmation_token
        change.save()

        if confirmation_link:
            request.user.phone = new_phone
            return Response({"confirmation link":confirmation_link})
        else:
            return Response({'detail': _('something went wrong')})


class SubmitChangePhoneNumber(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def get(self, *args, **kwargs):
        """submit confirmation link"""

        user_id = self.request.GET.get('user_id', '')
        confirmation_token = self.request.GET.get('confirmation_token', '')
        change = get_object_or_404(ChangePhone, code=confirmation_token)
        try:
            user = User.objects.get(pk=user_id)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is None:
            return Response('User not found', status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, confirmation_token):
            return Response(
                _('Token is invalid or expired. Please request another confirmation phone number by signing in.'),
                status=status.HTTP_400_BAD_REQUEST)
        self.request.user.phone = change.phone
        self.request.user.save()
        all_change = ChangePhone.objects.filter(user=user)
        all_change.delete()
        change.delete()
        return Response({
            'message': _('your number changed successfully'),
        })


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def get_object(self):
        """users can change their password"""
        return self.queryset.get(id=self.request.user.id)


class ProfileView(generics.RetrieveUpdateAPIView):

    permission_classes = (UpdateOwnProfile, permissions.IsAuthenticated)
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]


    def get_queryset(self):
        qs = User.objects.get(id=self.request.user.pk)
        return qs

    def retrieve(self, request, *args, **kwargs):
        profile = Profile.objects.get(user_id=self.request.user.pk)
        data = {
            'username': request.user.username,
            'phone': request.user.phone,
            'email': request.user.email,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'image': profile.get_profile_image(request=request),
        }
        return Response({'profile': data, 'change phone number': reverse('phones_view', request=request)})

    def put(self, request, *args, **kwargs):
        """update user profile"""
        data = request.data
        user_serializer = self.serializer_class(
            data=data,
            instance=request.user,
            context={'request': request},
            partial=True
        )

        user_serializer.is_valid(raise_exception=True)
        self.perform_update(user_serializer)

        profile_serializer = ProfileSerializer(
            data=data,
            instance=request.user,
            context={'request': request},
            partial=True
        )

        profile_serializer.is_valid(raise_exception=True)
        self.perform_update(profile_serializer)
        return Response(data={'message': _('your profile has been updated.')}, )



class SendPhoneOTP(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def post(self, *args, **kwargs):

        """ Before registering, users must send their one-time password (otp) to the phone number """

        request = self.request
        phone_number = None
        # try:
        serializer = SendOTPSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get('phone')
        if phone_number:

            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)

            if user.exists():  # this means that the user already exists, no new OTP for them
                return Response({'status': False, 'detail': 'user already exist.'})

            else:
                # if the user doesn't exist
                otp = send_otp(phone)
                if otp:  # if the otp already exists, then we'll increase the PhoneOTP.count by 1, max_limit is 10
                    otp = str(otp)
                    old_otp = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old_otp.exists():
                        old_otp = old_otp.first()
                        otp_count = old_otp.count

                        if otp_count > 10:
                            return Response({
                                'status': False,
                                'detail': _('you have exceeded the OTP sending limit. please contact the admin for support.')
                            })

                        old_otp.count = otp_count + 1
                        old_otp.otp = otp
                        if not send_after_seconds(59,old_otp.created_at):
                            return Response({'status': False, 'detail': format_lazy('{} {} {}',_("try after"),60,_("second"),)})
                        else:
                            message = "کد فعال سازی شما : " + otp
                            # send_sms_code(phone=phone, otp=otp, message=message)
                            old_otp.save()
                            return Response({
                                'status': True,
                                'detail': _('OTP sent successfully.'),
                                'verify_phone': reverse('validate_otp')
                            })
                    else:
                        phone_otp = PhoneOTP.objects.create(
                            phone=phone,
                            otp=otp,
                        )
                        message = "کد فعال سازی شما : " + otp
                        # send_sms_code(phone=phone, otp=otp, message=message)
                        phone_otp.save()
                        return Response({
                            'status': True,
                            'detail': _('OTP sent successfully.'),
                            'verify_phone': reverse('validate_otp', request=request)
                        })


                else:
                    return Response({
                        'status': False,
                        'detail': _('OTP sending error. please try after some time.')
                    })


        else:
            return Response({
                'status': False,
                'detail': _('please enter your phone number.')
            })


class ValidateOTP(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def post(self, *args, **kwargs):
        """validating users phone numbers"""
        phone = self.request.data.get('phone')
        otp_sent = self.request.data.get('otp')

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)

            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp) == str(otp_sent):
                    old.logged = True
                    old.save()
                    return Response({
                        'status': True,
                        'detail': _('OTP code matched. you can proceed to register'),
                        'register_url': reverse('register_otp')
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': _('OTP incorrect. please try again')
                    })

            else:
                return Response({
                    'status': False,
                    'detail': _('incorrect phone number.')
                })

        else:
            return Response({
                'status': 'False',
                'detail': _('phone and otp are required')
            })


class Register(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        phone = self.request.data.get('phone', False)
        username = self.request.data.get('username', False)
        email = self.request.data.get('email')
        password1 = self.request.data.get('password1', False)
        password2 = self.request.data.get('password2', False)

        if phone and password1 and password2:
            phone = str(phone)
            user = User.objects.filter(phone__iexact=phone)

            if user.exists():
                return Response({
                    'status': False,
                    'detail': _('phone number have account associated.')
                })

            else:
                old = PhoneOTP.objects.filter(phone__iexact=phone)
                if old.exists():
                    old = old.first()

                    if old.logged:
                        temp_data = {
                            'phone': phone,
                            'username': username,
                            'password1': password1,
                            'password2': password2,
                            'email': email
                        }
                        serializer = CreateUserSerialzier(data=temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save(self.request)

                        old.delete()
                        return Response({
                            'status': True,
                            'detail': _('your account has been created successfully.'),
                            'login_url': reverse('login_otp')
                        })

                    else:
                        return Response({
                            'status': False,
                            'detail': _('your otp was not verified. please go back and verify otp')

                        })

                else:
                    return Response({
                        'status': False,
                        'detail': format_lazy('{} {}',_("phone number not recognised."),_("for registration please record your phone number first")),
                        'send_otp_url': reverse('sent_otp', request=self.request, )
                    })

        else:
            serializer = CreateUserSerialzier(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            raise serializer.validate(self.request.data)


class DefaultLoginView(LoginView):
    serializer_class = LoginUserSerializer
    queryset = ''
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def get(self, request, *args, **kwargs):
        """login with username and password"""
        return Response({'login with phone number': reverse('login_phone_otp', request=request)})


class PhoneLoginView(LoginView):
    serializer_class = LoginUserSerializer
    queryset = ''
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def get(self, request, *args, **kwargs):
        """login with phone and password"""
        return Response({'login with username': reverse('login_otp', request=request)})





class ForgotPasswordOTP(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def post(self, *args, **kwargs):
        """sending otp to users phone number if users forget their password"""
        phone_number = self.request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)

            if user.exists():
                otp = send_otp(phone)

                if otp:
                    otp = str(otp)
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        old = old.first()
                        # count=old.count

                        if old.count >= 10:
                            return Response({
                                'status': False,
                                'detail': _(
                                    'you have exceeded the OTP sending limit. please contact the admin for support.'),
                            })
                        else:
                            if not send_after_seconds(59,old.created_at):

                                return Response({
                                    'status': False,
                                    'detail': format_lazy('{} {} {}',_("try after"),60,_("second"),),
                                    'password_rest_url': reverse('validate_forgot_password_otp', request=self.request)
                                })
                            else:
                                old.count = old.count + 1
                                old.otp = otp
                                old.save()
                                message = "کد فعال سازی برای تنظیم مجدد رمز عبور : " + otp
                                # send_sms_code(phone=phone, otp=otp, message=message)
                                return Response({
                                    'status': True,
                                    'detail': _('OTP has been sent for password reset.'),
                                    'password_reset_url': reverse('validate_forgot_password_otp', request=self.request),
                                    'request count': old.count,
                                    'max limit': 10
                                })

                    else:
                        count = 0
                        count = count + 1
                        phone_otp = PhoneOTP.objects.create(
                            phone=phone,
                            otp=otp,
                            count=count,
                            forgot=True, )
                        message = "کد فعال سازی برای تنظیم مجدد رمز عبور : " + otp
                        # send_sms_code(phone=phone, otp=otp, message=message)
                        return Response({
                            'status': True,
                            'detail': _('OTP has been sent for password reset.'),
                            'password_reset_url': reverse('validate_forgot_password_otp', request=self.request),
                            'request count': count,
                            'max limit': 10,
                        })

                else:
                    return Response({
                        'status': False, 'detail': _("OTP sending error. please try after some time.")
                    })


            else:
                return Response({
                    'status': False,
                    'detail': format_lazy('{} {}',_("phone number not recognised."),_("you can create a new account for this number."))
                })
        return Response({
            'status': False,
            'detail': _('please enter your phone number.')
        })


class ValidateForgotPasswordOTP(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def post(self, *args, **kwargs):
        """ Validating otp for change password """
        phone = self.request.data.get('phone', False)
        otp_sent = self.request.data.get('otp', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone=phone)

            if old.exists():
                old = old.first()

                if old.forgot == False:
                    return Response({
                        'status': False,
                        'detail': _(
                            'This phone has not received valid otp for forgot password. Request a new otp or contact to admin.')
                    })

                else:
                    otp = old.otp

                    if str(otp) == str(otp_sent):
                        old.forgot_logged = True
                        old.save()
                        return Response({
                            'status': True,
                            'detail': _('OTP matched. please proceed to create new password'),
                            'change_forgot_password': reverse('change_forgot_password_otp', request=self.request),
                        })

                    else:
                        return Response({
                            'status': False,
                            'detail': _('OTP incorrect. please try again')
                        })

            else:
                return Response({
                    'status': False,
                    'detail': _('phone number not recognised.')
                })

        else:
            return Response({
                'status': 'False',
                'detail': _('phone and otp are required')
            })


class ForgotPasswordChange(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]

    def put(self, *args, **kwargs):
        """changing password after phone validation"""
        serializer = ForgotPasswordSerializer(data=self.request.data, instance=self.request.user)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data.get('phone', False)
        otp = serializer.validated_data.get('otp', False)
        password = serializer.validated_data.get('new_password', False)
        otp_old = None
        if phone and password:
            try:
                otp_old = PhoneOTP.objects.get(phone__iexact=phone)
            except:
                return Response({
                    'status': False,
                    'detail': format_lazy("{} {}",_('incorrect phone number.'),_("otherwise, refer to this address")),
                    'url':reverse('forgot_password_otp',request=self.request)
                })
            otp = otp_old.otp
        if phone and password and otp:
            old = PhoneOTP.objects.filter(Q(phone__iexact=phone) & Q(otp__iexact=otp))
            if old.exists():

                old = old.first()
                if old.forgot_logged:

                    post_data = {
                        'phone': phone,
                        'new_password': password,
                        'otp': otp
                    }
                    user_obj = get_object_or_404(User, phone__iexact=phone)
                    serializer = ForgotPasswordSerializer(data=post_data, instance=self.request.user)

                    if serializer.is_valid(raise_exception=True):
                        if user_obj:
                            user_obj.set_password(password)
                            user_obj.is_active = True
                            user_obj.save()
                            old.delete()
                            return Response({
                                'status': True,
                                'detail': _('password changed successfully. please login'),
                                'login_url': reverse('login_otp', request=self.request)
                            })
                        return Response({
                            'status': False,
                            'detail': _("No user were found with this information")
                        })
                    else:
                        return Response({
                            'status': False,
                            'detail': _('OTP Verification failed. Please try again in previous step')
                        })
            else:
                return Response({
                    'status': False,
                    'detail': _(
                        'Phone and otp are not matching or a new phone has entered. Request a new otp in forgot password')
                })

        else:
            serializer = ForgotPasswordSerializer(data=self.request.data, instance=self.request.user)
            serializer.is_valid(raise_exception=True)
            return Response({
                'status': False,
                'detail': _('Post request have parameters missing.')
            })


# """ Not Found Error """
# def handler404(request, exception):
#     context = {}
    # return render(request,'errors/404.html',context,status=404)


# """ Internal Server Error """
# def handler500(request, exception=None):
#     context = {}
    # return render(request,'errors/500.html',context,status=500)


# """ Forbidden Error """
# def handler403(request, exception=None):
    # context = {}
    # return render(request, "errors/403.html", context)


# """ Bad Request Error """
# def handler400(request, exception=None):
    # context = {}
    # return render(request, "errors/400.html", context)


