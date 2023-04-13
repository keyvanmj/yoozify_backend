from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Blog


class BlogSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedIdentityField(view_name='blog_detail')

    class Meta:
        model = Blog
        fields = ['id','title','short_descriptions','descriptions','image','url','created','updated','detail']


    def __init__(self,*args,**kwargs):
        super(BlogSerializer, self).__init__(*args,**kwargs)
        request = self.context.get('request')
        if request.path_info == reverse('blog_list'):
            self.Meta.fields = ['id','title','image','short_descriptions','detail']
