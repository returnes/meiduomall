#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-18
from django.conf.urls import url

from carts import views

urlpatterns=[
    url(r'^$',views.CartView.as_view(),name='cart')
]