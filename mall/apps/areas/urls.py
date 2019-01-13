#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-11
from django.conf.urls import url

from areas import views
from rest_framework.routers import DefaultRouter
router=DefaultRouter()
router.register(r'infos',views.AreaInfoViewSet,base_name='area')

urlpatterns=[

]
urlpatterns+=router.urls
