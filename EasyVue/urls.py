"""EasyVue URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import (url, include)

from django.views import static
from proxy import views as proxy_views

urlpatterns = [
    url(r'^login/', proxy_views.login),
    url(r'^logout/', proxy_views.logout),
    url(r'^', proxy_views.index),
]
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
else:
    urlpatterns += [url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static')]
