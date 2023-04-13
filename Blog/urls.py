from django.urls import path
from . import views

urlpatterns = [
    path('list/',views.BlogListView.as_view(),name='blog_list'),
    path('detail/<int:pk>/',views.BlogDetail.as_view(),name='blog_detail'),
]