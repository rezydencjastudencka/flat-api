from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create$', views.create),
    url(r'^check$', views.check),
    url(r'^remove$', views.remove)
]
