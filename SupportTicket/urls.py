from django.urls import path, include
from .models import Ticket
from rest_framework import routers
from .views import TicketViewSet

router = routers.DefaultRouter()

router.register(r'', TicketViewSet,basename='ticket')


urlpatterns = [
    path(r'', include(router.urls)),
]