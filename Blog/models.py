import datetime
import os
import uuid
from django.db import models
from django.urls import reverse
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

def blog_image_upload_file_path(instance, filename):
    """Generates file path for uploading blog images"""
    extension = filename.split('.')[-1]
    file_name = f'{uuid.uuid4()}.{extension}'
    date = datetime.date.today()
    initial_path = f'pictures/uploads/blog/{date.year}/{date.month}/{date.day}/'
    full_path = os.path.join(initial_path, file_name)

    return full_path



class Blog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,verbose_name=_('user'))
    title = models.CharField(max_length=100,verbose_name=_("title"))
    descriptions = models.TextField(verbose_name=_("descriptions"))
    active = models.BooleanField(default=False,verbose_name=_("active"))
    image = models.ImageField(upload_to=blog_image_upload_file_path,blank=True,null=True,verbose_name=_("image"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    url = models.URLField(blank=True,null=True,verbose_name=_("url"))

    class Meta:
        verbose_name = _("blog")
        verbose_name_plural = _("blogs")

    def __str__(self):
        return self.title

    def short_descriptions(self):
        value = self.descriptions
        try:
            length = int(20)
        except ValueError:
            return value
        return Truncator(value).words(length, truncate=' …')

    def get_absolute_url(self):
        url = reverse('blog_detail',kwargs={'pk':self.pk})
        return url

    def get_image(self):
        try:
            return self.image.url
        except:
            return ''

