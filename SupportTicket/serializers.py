from rest_framework import serializers
from rest_framework.reverse import reverse
from django.utils.translation import gettext_lazy as _
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField(source='get_detail_url')
    class Meta:
        model = Ticket
        fields = ('id', 'title', 'ticket_id', 'status', 'content','image', 'created', 'modified','detail_url')
        read_only_fields = ('ticket_id','status')

    def get_fields(self, *args, **kwargs):
        fields = super(TicketSerializer, self).get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "POST":
            fields['title'].required = True
            fields['title'].allow_blank = False
            fields['title'].allow_null = False

            fields['content'].required = True
            fields['content'].allow_blank = False
            fields['content'].allow_null = False
        return fields

    def get_detail_url(self, obj):
        request = self.context.get('request',None)
        return reverse('ticket-detail',request=request,kwargs={'pk':obj.pk})


    def validate(self, attrs):
        max_size_upload_image = 1024 * 1024
        try:
            if attrs.get('image').size > max_size_upload_image:
                raise serializers.ValidationError({'Size Error':_('Image File Size Too Large (Max Size : 1mb)')})
        except:
            pass
        return attrs
