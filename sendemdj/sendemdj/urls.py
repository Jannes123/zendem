#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL configuration for sendemdj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from . import settings
from django.urls.resolvers import URLResolver
from django.conf.urls.static import static
from rest_framework import routers
import logging
LOGGER = logging.getLogger('coasterx.request')

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('sendem-rest-auth/', include('sendemauth.urls', namespace='sendemauth')),
    path('', include(router.urls)),
    path('api-general/', include('rest_framework.urls', namespace="rest_framework"), name='rest_framework'),
]
if settings.DEBUG:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


LOGGER.debug('urlpatterns:')
LOGGER.debug(urlpatterns)
for x in urlpatterns:
    if type(x) == URLResolver:
        LOGGER.debug(x.url_patterns)
    else:
        LOGGER.debug(x)

