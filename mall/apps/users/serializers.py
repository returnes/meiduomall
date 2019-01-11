#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-7
import re
from rest_framework import serializers

# from rest_framework.serializers import Serializer #适用于无模型序列化器
from users.models import User
from django_redis import get_redis_connection


class RegisterModelSerializers(serializers.ModelSerializer):
    '''注册序列化器定义'''
    # 数据库中不存在的字段定义校验
    # write_only 只在反序列化的时候使用
    # read_only 只在序列化的时候使用
    password2 = serializers.CharField(label='校验密码', allow_null=False, allow_blank=False, write_only=True)
    sms_code = serializers.CharField(label='验证码校验', max_length=6, min_length=6, allow_null=False, allow_blank=False,
                                     write_only=True)
    allow = serializers.CharField(label='是否同意协议', allow_null=False, allow_blank=False, write_only=True)
    token=serializers.CharField(label='验证token',read_only=True)

    # 数据库中存在的字段校验
    class Meta:
        model = User
        fields = ['id', 'token','username', 'password', 'mobile', 'password2', 'sms_code', 'allow']
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {'min_length': '仅允许5-20个字符的用户名', 'max_length': '仅允许5-20个字符的用户名'}
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {'min_length': '仅允许8-20个字符的密码', 'max_length': '仅允许8-20个字符的密码'}
            }
        }

    # 单个字段校验
    def validate_mobile(self, mobile):
        '''手机号格式校验'''
        if not re.match(r'1[3-9]\d{9}', mobile):
            raise serializers.ValidationError('手机号错误')
        return mobile

    def validate_allow(self, value):
        '''是否同意校验'''
        if value != "true":
            raise serializers.ValidationError('请同意条款')
        return value
    # 多个字段校验
    def validate(self, attrs):
        '''校验两次密码是否一直，手机验证码是否一致'''
        password1=attrs.get('password')
        password2=attrs.get('password2')
        if password1!=password2:
            raise serializers.ValidationError('两次输入的密码不一致')
        sms_code=attrs.get('sms_code')
        mobile=attrs.get('mobile')
        redis_conn=get_redis_connection('code')
        redis_sms_code=redis_conn.get('sms_%s'%mobile)
        if not redis_sms_code:
            raise serializers.ValidationError('验证码过期')
        if redis_sms_code.decode()!=sms_code:
            raise serializers.ValidationError('验证码一致')
        return attrs
    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        
        user=super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        #实现jwt token
        # from rest_framework_jwt.settings import api_settings
        # jwt_payload_handler=api_settings.JWT_PAYLOAD_HANDLER
        # jwt_encode_handler=api_settings.JWT_ENCODE_HANDLER
        # payload=jwt_payload_handler(user)
        # token=jwt_encode_handler(payload)
        from utils.token_jwt import token_jwt
        token=token_jwt(user)
        user.token=token
        return user