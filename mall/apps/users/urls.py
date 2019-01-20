#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-6
from django.conf.urls import url

from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameCountView.as_view(),name='usernames'),#用户名验证
    url(r'^phones/(?P<mobile>[1][3,4,5,7,8][0-9]{9})/count/$',views.RegisterMobileCountView.as_view(),name='mobiles'),#手机号验证
    url(r'^$',views.RegisterView.as_view(),name='register'),#注册功能
    # url(r'^auths/$', obtain_jwt_token,name='auths'),
    url(r'^auths/$', views.UserAuthorizationView.as_view(),name='auths'),
    url(r'^infos/$',views.UserCenterInfoView.as_view(),name='infos'),
    url(r'^emails/$',views.UserEmailInfoView.as_view(),name='emails'),
    url(r'^emails/verification/$',views.UserEmailVerifyView.as_view(),name='verify'),
    url(r'^browerhistories/$', views.UserBrowsingHistoryView.as_view(), name='history'),

]

# app_name='users'
from rest_framework.routers import DefaultRouter
router=DefaultRouter()
router.register(r'addresses',views.AddressViewSet,base_name='address')
# router.register(r'addresses/title',views.AddressViewSet,base_name='title')

urlpatterns+=router.urls
