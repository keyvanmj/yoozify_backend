from rest_framework import serializers
from rest_framework.reverse import reverse

from ContactUs.models import ContactUs


class ContactUsSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.HyperlinkedIdentityField(view_name='contact_us_detail',)

    class Meta:
        model = ContactUs
        fields = ['id','title','message','date','absolute_url','author']
        read_only_fields = ['id']

