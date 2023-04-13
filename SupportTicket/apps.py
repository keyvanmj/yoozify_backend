from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SupportticketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SupportTicket'
    verbose_name = _("support")

