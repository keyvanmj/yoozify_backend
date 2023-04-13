from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics,permissions
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from Blog.parser import MultiPartJSONParser
from Blog.views import ListPagination
from .serializers import ContactUsSerializer
from .models import ContactUs
from django.utils.translation import gettext_lazy as _


class ContactUsView(generics.ListCreateAPIView):
    parser_classes = (MultiPartJSONParser, JSONParser, FormParser)
    renderer_classes = [JSONRenderer]
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.filter(Q(active=True) & Q(is_question=True)).order_by('-date')
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post','get']

    pagination_class = ListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter,]

    search_fields = (
        'title',
        'message',
    )

    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data.get('title')
        message = serializer.validated_data.get('message')
        contact = ContactUs.objects.create(title=title,message=message,user=request.user)
        contact.save()
        return Response({"detail":_("your message has been sent.")})


class ContactUsDetailView(generics.RetrieveAPIView):
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.filter(active=True)
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartJSONParser, JSONParser, FormParser)
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        object_ = self.get_object()
        reply = object_.reply_to.values('title','message','date')
        data = {
            'title':object_.title,
            'message':object_.message,
            'data':object_.date,
            'user':object_.user.username,
            'reply':reply
        }
        return Response(data)

    def get_object(self):
        contact_detail = get_object_or_404(self.queryset.all(),pk=self.kwargs['pk'])
        return contact_detail
