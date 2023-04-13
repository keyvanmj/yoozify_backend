from django.urls import path
from .views import ContactUsView,ContactUsDetailView


urlpatterns = [
    path('',ContactUsView.as_view(),name='contact_us'),
    path('<int:pk>/',ContactUsDetailView.as_view(),name='contact_us_detail'),
]
