"""flat_api_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from flat_api_django.graphql_view import FlatGraphQLView

from django.http import HttpResponse


def ok(request):
    return HttpResponse('ok')


urlpatterns = [
    url(r'^$', ok),
    url(r'^counter/', include('counters.urls')),
    url(r'^session/', include('session.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', FlatGraphQLView.as_view(graphiql=True)),
    url('', include('django_prometheus.urls')),
]
