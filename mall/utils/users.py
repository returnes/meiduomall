#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-9
import re

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


from django.contrib.auth.backends import ModelBackend
from rest_framework.mixins import CreateModelMixin

def get_user_by_account(account):

    try:
        if re.match(r'1[345789]\d{9}',account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        user = None

    return user

class UsernameMobileAuthBackend(ModelBackend):
    '''
    继承django自带的认证类，自带默认只能用户名登陆
    重写以下方法,实现用户名手机号都能登陆
    :return user
    '''

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
        return None


# 扩展的
# class MyBackend(object):
#     def authenticate(self, request, username=None, password=None):
#         user = get_user_by_account(username)
#         # 2. 验证码用户密码
#         if user is not None and user.check_password(password):
#             return user
#         # 必须返回数据
#         return None
#
#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None
