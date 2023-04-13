from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Accounts'
    verbose_name = _("account & profile")

    def ready(self):
        import Accounts.signals