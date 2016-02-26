from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<counter_name>\w+)$', views.index),
    url(r'^(?P<counter_name>\w+)/modify$', views.modify),
]
