from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount,SocialToken,SocialApp
from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy


from .models import User,Profile,PhoneOTP,ChangePhone
from .mixins import BaseStaffReadonlyAdminMixin


class UserAdmin(BaseStaffReadonlyAdminMixin,admin.ModelAdmin):
    list_display = ['username','email','is_staff','is_active','phone','is_superuser']
    readonly_fields = ['password']


class ProfileAdmin(BaseStaffReadonlyAdminMixin,admin.ModelAdmin):
    list_display = ['first_name','last_name','user']


class PhoneOTPAdmin(BaseStaffReadonlyAdminMixin,admin.ModelAdmin):
    list_display = ['phone','otp','count','logged','forgot','forgot_logged','created_at']


class ChangePhoneAdmin(BaseStaffReadonlyAdminMixin,admin.ModelAdmin):
    list_display = ['user','code','phone']


class GroupAdmin(BaseStaffReadonlyAdminMixin,admin.ModelAdmin):
    pass



admin.site.register(User,UserAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(PhoneOTP,PhoneOTPAdmin)
admin.site.register(ChangePhone,ChangePhoneAdmin)
admin.site.unregister(EmailAddress)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)
admin.site.register(Group,GroupAdmin)

