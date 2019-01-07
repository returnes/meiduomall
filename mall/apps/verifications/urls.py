#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-6
from django.conf.urls import url

from verifications import views

urlpatterns=[
    url(r'^imagecodes/(?P<image_code_id>.+)/$',views.RegisterCaptchaView.as_view(),name='imagecodes'),
    url(r'^smscodes/(?P<mobile>[1][3,4,5,7,8][0-9]{9})/$',views.RegisterSMSCodeView.as_view(),name='smscodes'),
]