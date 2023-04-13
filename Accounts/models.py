import datetime
import os
import uuid
from django.core.validators import RegexValidator
from django.contrib.auth.base_user import BaseUserManager
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _,gettext
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models



def user_image_upload_file_path(instance, filename):
    """Generates file path for uploading user images"""
    extension = filename.split('.')[-1]
    file_name = f'{uuid.uuid4()}.{extension}'
    date = datetime.date.today()
    initial_path = f'pictures/uploads/user/{date.year}/{date.month}/{date.day}/'
    full_path = os.path.join(initial_path, file_name)

    return full_path


class UserManager(BaseUserManager):

    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError(_("The Phone Number must be set"))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(**extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{11,13}$',
                                 message=_("phone number must be entered in the format: '09***' or '+989***. up to 11 or 13 digits allowed."))
    phone = models.CharField(_("phone"),validators=[phone_regex], max_length=17, unique=True)
    email = models.EmailField(_("email address"), unique=True,blank=True,null=True)
    username = models.CharField(_("username"),max_length=40,unique=True)
    is_staff = models.BooleanField(_("staff"),default=False)
    is_active = models.BooleanField(_("active"),default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    key = models.CharField(max_length=100, unique=True, blank=True)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['phone',]

    objects = UserManager()

    def __str__(self):
        if self.username:
            return self.username
        else:
            return '-'

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def profile(self):
        return self.profile_set.all()

    def images(self,request):
        try:
            image = [request.build_absolute_uri(x.image.url) for x in self.profile()]
        except:
            image = None
        return image

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name=_("user"))
    first_name = models.CharField(_("first name"),max_length=255, blank=True, null=True)
    last_name = models.CharField(_("last name"),max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    image = models.ImageField(_('Image'),upload_to=user_image_upload_file_path,null=True,blank=True,max_length=1024
    )
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")


    def get_profile_image(self,request):
        if self.image:
            return request.build_absolute_uri(self.image.url)
        else:
            return None



class PhoneOTP(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{11,13}$', message=_("phone number must be entered in the format: '09***' or '+989***. Up to 11 or 13 digits allowed."))
    phone = models.CharField(_("phone"),validators=[phone_regex], max_length=17)
    otp = models.CharField(blank=True, null=True,max_length=9,verbose_name=_("otp"))
    count = models.IntegerField(_("count"),default=0, help_text=_("number of otp sent"))
    logged = models.BooleanField(_("logged"),default=False, help_text=_("if otp verification got successful"))
    forgot = models.BooleanField(_("forgot"),default=False, help_text=_("only true for forgot password"))
    forgot_logged = models.BooleanField(_("forgot logged"),default=False, help_text=_("only true if validate otp forgot get successful"))
    created_at = models.DateTimeField(auto_now=True,verbose_name=_("created"))

    def __str__(self):
        return f' کد {self.otp} برای شماره {self.phone}'


    class Meta:
        verbose_name = _("phone otp")
        verbose_name_plural = _("phone otp")


class ChangePhone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name=_("user"))
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=200, unique=True,verbose_name=_("code"))
    phone_regex = RegexValidator(regex=r'^\+?1?\d{11,13}$', message=_("Phone number must be entered in the format: '09***' or '+989***. Up to 11 or 13 digits allowed."))
    phone = models.CharField(verbose_name=_("phone"), validators=[phone_regex], max_length=17)

    def __str__(self):
        return f"{self.user} : {self.phone}"


    class Meta:
        verbose_name_plural = _('change phone')