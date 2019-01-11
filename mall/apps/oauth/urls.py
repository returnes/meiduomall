#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-10
from django.conf.urls import url
from oauth import views

urlpatterns=[
    # 获取qq url，http://api.meiduo.site:8000/oauth/qq/statues/?state=/
    url(r'^qq/statues/$',views.QQAuthURLView.as_view(),name='qq_statues'),
    # 获取 code，http://api.meiduo.site:8000/oauth/qq/users/?code=5F548719D03A0BFBC3A5FB632C0F198B
    url(r'^qq/users/$',views.QQAuthUserView.as_view(),name='qq_users'),
]
