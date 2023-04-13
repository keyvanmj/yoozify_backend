from django.contrib import admin
from django.forms import Textarea

from Accounts.mixins import BaseStaffReadonlyAdminMixin
from .models import Blog
from django.db import models


class BlogAdmin(BaseStaffReadonlyAdminMixin,admin.ModelAdmin):
    list_display = ['title','active','created','user']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 12, 'cols': 130})},
    }


admin.site.register(Blog,BlogAdmin)