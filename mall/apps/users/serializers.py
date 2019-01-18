#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-7
import re
from rest_framework import serializers, status

# from rest_framework.serializers import Serializer #适用于无模型序列化器
from rest_framework.response import Response

from goods.models import SKU
from mall import settings
from users.models import User, Address
from django_redis import get_redis_connection

from users.utils import generic_verify_url, check_token


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


class UserCenterInfoModelSerializer(serializers.ModelSerializer):
    '''
    用户中心序列化器定义
    查询用户信息
    '''
    class Meta:
        model=User
        fields=['id','username','mobile','email','email_active']

class UserEmailInfoSerializer(serializers.ModelSerializer):
    '''
    邮箱认证序列号器定义
    1.邮箱更新
    2.邮箱认证发送
    3.邮箱认证状态更新
    '''
    class Meta:
        model=User
        fields=['id','email']
        extra_kwargs={
            'email':{'required':True}
        }
    def update(self, instance, validated_data):
        email=validated_data['email']
        instance.email=email
        instance.save()
        # from django.core.mail import send_mail


        subject = '美多商场激活邮件'
        message=''# 内容
        from_email=settings.EMAIL_FROM
        # recipient_list,   收件人列表
        recipient_list = [email]

        # user_id = 8
        #对当前用户id进行加密
        verify_url = generic_verify_url(instance.id)
        # 邮件发送调用celery
        from celery_tasks.email.tasks import send_celery_email
        send_celery_email.delay(subject,message,from_email, email,verify_url,recipient_list)
        return instance

class AddressSerializer(serializers.ModelSerializer):
    '''
    1.定义字段
    2.复用model部分字段
    3.收货地址更新、保存
    '''
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district =serializers.StringRelatedField(read_only=True)
    province_id=serializers.IntegerField(label='省id',required=True)
    city_id=serializers.IntegerField(label='市id',required=True)
    district_id=serializers.IntegerField(label='区id',required=True)
    mobile=serializers.RegexField(label='手机号',regex=r'^1[3-9]\d{9}$')

    class Meta:
        model=Address
        exclude=['user','is_delete','create_time','update_time']


    def create(self, validated_data):
        validated_data['user']=self.context['request'].user
        return super().create(validated_data)

class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Address
        fields=['title']


class UserBrowsingHistorySerializer(serializers.Serializer):
    '''添加用户浏览记录序列化器'''
    sku_id=serializers.IntegerField(label='商品编号',min_value=1,required=True)

    def validate_sku_id(self, value):
        '''检测商品是否存在'''
        try:
            SKU.objects.get(pk=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value

    def create(self, validated_data):
        '''重写方法保存在redis中'''
        # 获取用户信息
        user_id=self.context['request'].user.id
        sku_id=validated_data['sku_id']
        redis_conn=get_redis_connection('history')
        # 删除之前数据
        redis_conn.lrem('history_%s'%user_id,0,sku_id)
        # 写入当前数据
        redis_conn.lpush('history_%s'%user_id,sku_id)
        # 保存5条记录
        redis_conn.ltrim('history_%s'%user_id,0,5)
        return validated_data

class UserBrowsingHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model=SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')