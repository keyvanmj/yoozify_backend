import datetime
import os
from django.utils.translation import gettext_lazy as _
from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

status = (
    (_("pending"), _("pending")),
    (_("closed"), _("closed")),
)

def generate_ticket_id():
    return str(uuid.uuid4()).split("-")[-1]


def user_ticket_image_upload_file_path(instance, filename):
    """Generates file path for uploading user tickets"""
    extension = filename.split('.')[-1]
    file_name = f'{uuid.uuid4()}.{extension}'
    date = datetime.date.today()
    initial_path = f'pictures/uploads/ticket/{date.year}/{date.month}/{date.day}/'
    full_path = os.path.join(initial_path, file_name)

    return full_path



class Ticket(models.Model):
    title = models.CharField(max_length=255,verbose_name=_("title"))
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name=_("user"))
    content = models.TextField(verbose_name=_("content"))
    image = models.ImageField(
        _('Image'), upload_to=user_ticket_image_upload_file_path,
        null=True, blank=True, max_length=1024
    )
    ticket_id = models.CharField(max_length=255, blank=True,verbose_name=_("ID"))
    status = models.CharField(choices=status, max_length=155, default=status[0][0],verbose_name=_("status"))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True,)


    def __str__(self):
        return "{} - {}".format(self.title, self.ticket_id)

    def save(self, *args, **kwargs):
        if len(self.ticket_id.strip(" ")) == 0:
            self.ticket_id = generate_ticket_id()

        super(Ticket, self).save(*args, **kwargs)


    def get_ticket_image(self):
        if self.image:
            return self.image.url
        else:
            return None

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = _("tickets")
