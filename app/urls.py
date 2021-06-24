from django.urls import path

from .views import (
    home,
    hostusage,
    instances,
    networks
)

app_name='app'
urlpatterns = [
    path('',home,name='home'),
    path('vmachines',instances,name='vmachines'),
    path("hostusage", hostusage.as_view(), name="hostusage"),
    path("networks", networks, name="networks")
]