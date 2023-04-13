from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from Blog.views import ListPagination
from .models import Ticket
from .serializers import TicketSerializer


class TicketViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin):

    serializer_class = TicketSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = ListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = (
        'title',
        'content',
    )

    def get_queryset(self):
        queryset = ''
        try:
            queryset = Ticket.objects.filter(user=self.request.user)
        except:
            pass
        return queryset

    def retrieve(self,request,*args,**kwargs):
        obj = get_object_or_404(self.get_queryset(),user=request.user,pk=self.kwargs['pk'])
        data = {
            'title':obj.title,
            'ticket_id':obj.ticket_id,
            'status':obj.status,
            'content':obj.content,
            'image':obj.get_ticket_image(),
            'created':obj.created,
            'modified':obj.modified,

        }
        return Response(data)

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data,context={'request':request})

        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content')
        image = serializer.validated_data.get('image')
        ticket = Ticket.objects.create(title=title,content=content,image=image,user=request.user)
        ticket.save()
        return Response({'detail':_('your ticket has been successfully sent')})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.image:
            storage, path = instance.image.storage, instance.image.path
            storage.delete(path)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()