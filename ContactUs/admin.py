from django.utils.text import format_lazy
from Accounts.mixins import BaseStaffReadonlyAdminMixin
from .models import ContactUs
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _, ngettext


class ContactAdmin(BaseStaffReadonlyAdminMixin,admin.ModelAdmin):
    list_display = ['user','title','get_short_message','date','active','is_question','is_reply','reply']

    actions = ['active_contact','deactive_contact']

    def reply(self,obj):
        return obj.get_reply()
    reply.short_description = format_lazy('{} {}',_("reply"),_("question"))

    def active_contact(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request,format_lazy('{} {} {} {}',_("activate"),_("message"),_(f'{updated}'),_("contact")))

    active_contact.short_description = format_lazy('{} {} {}',_("activate"),_("messages"),_("contact"))


    def deactive_contact(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request,format_lazy('{} {} {} {}',_("deactivate"),_("message"),_(f'{updated}'),_("contact")))
    deactive_contact.short_description = format_lazy('{} {} {}',_("deactivate"),_("messages"),_("contact"))

    def save_model(self, request, obj, form, change):
        try:
            if obj.parent:
                obj.is_reply = True
                obj.is_question = False
                obj.parent.active = True
                obj.parent.save()

                obj.save()
            else:
                obj.is_question = True
                obj.is_reply = False
            obj.save()
        except:
            pass
        return super(ContactAdmin, self).save_model(request, obj, form, change)

    def get_short_message(self,obj):
        return obj.short_message
    get_short_message.short_description = format_lazy('{} {}',_("short"),_("message"))





admin.site.register(ContactUs,ContactAdmin,)


