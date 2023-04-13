from django.db import models
from rest_framework.reverse import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class ContactUs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,verbose_name=_("user"))
    title = models.CharField(max_length=150,verbose_name=_("title"))
    message = models.TextField(verbose_name=_("message"))
    active = models.BooleanField(default=False,verbose_name=_("active"))
    date = models.DateTimeField(auto_now_add=True,verbose_name=_("created"))
    is_question = models.BooleanField(default=False,verbose_name=_("question"))

    # for reply
    is_reply = models.BooleanField(default=False,verbose_name=_("reply"))
    parent = models.ForeignKey('self',on_delete=models.CASCADE, blank=True,null=True,verbose_name=_('parent'),related_name='reply_to')

    def __str__(self):
        return f'{self.title} : {self.user}'

    @property
    def short_message(self):
        if len(self.message) > 30:
            return _(self.message[:30]) + str('...')
        else:
            return _(self.message[:30])

    @property
    def get_absolute_url(self):
        return reverse('contact_us_detail',kwargs={'pk':self.pk})

    @property
    def author(self):
        return self.user.username


    def get_reply(self):
        # return ' _ '.join([f'{r.title}' for r in self.parent.title])
        if self.parent:
            return self.parent.title
        return ''


    class Meta:
        verbose_name_plural = _('contact us')
