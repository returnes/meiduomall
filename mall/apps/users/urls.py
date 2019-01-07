#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-6
from django.conf.urls import url
from users import views

urlpatterns = [
    url(r'^login',views.LoginView.as_view(),name='login'),
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameCountView.as_view(),name='usernames'),#用户名验证
    url(r'^phones/(?P<mobile>[1][3,4,5,7,8][0-9]{9})/count/$',views.RegisterMobileCountView.as_view(),name='mobiles'),#手机号验证
    url(r'^',views.RegisterView.as_view(),name='register'),#注册功能

]
app_name='users'
