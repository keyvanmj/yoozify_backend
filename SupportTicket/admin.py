from django.contrib import admin, messages
from django.utils.html import format_html

from Accounts.mixins import BaseStaffReadonlyAdminMixin
from .models import Ticket

class TicketAdmin(BaseStaffReadonlyAdminMixin,admin.ModelAdmin):

    def image_tag(self, obj):
        return format_html(f'<img src="{obj.get_ticket_image()}" width=100 alt="{obj.title}" />')


    list_display = ['user','title','ticket_id','status','image_tag']

admin.site.register(Ticket,TicketAdmin)
