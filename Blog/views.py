from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import permissions,generics
from .models import Blog
from .parser import MultiPartJSONParser
from .serializers import BlogSerializer


class ListPagination(PageNumberPagination):
    page_size = 12
    max_page_size = 100


class BlogListView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]
    parser_classes = (MultiPartJSONParser, JSONParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Blog.objects.filter(active=True).order_by('-created','-updated')
    serializer_class = BlogSerializer
    pagination_class = ListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = (
        'title',
        'descriptions',
    )


class BlogDetail(generics.RetrieveAPIView):
    renderer_classes = [JSONRenderer]
    parser_classes = (MultiPartJSONParser, JSONParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Blog.objects.filter(active=True).order_by('-created','-updated')
    serializer_class = BlogSerializer

    def get_object(self):
        blog = get_object_or_404(Blog,pk=self.kwargs['pk'])
        return blog

    def retrieve(self, request, *args, **kwargs):
        blog = self.get_object()
        data = {
            'id':blog.pk,
            'title':blog.title,
            'descriptions':mark_safe(blog.descriptions),
            'image':blog.get_image(),
            'reference url':blog.url,
            'created':blog.created,
            'updated':blog.updated,
            'author':blog.user.username
        }
        return Response(data)
