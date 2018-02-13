from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create$', views.create),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]|1[0-2])$', views.index),
    url(r'^expense/(?P<id>[0-9]+)$', views.get_expense),
    url(r'^delete$', views.delete)
]
