#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-6
from rest_framework import serializers
from django_redis import get_redis_connection
from redis.exceptions import RedisError
import logging

logger = logging.getLogger('memiduo')


class RegisterSMSCodeSerializer(serializers.Serializer):
    # 校验字段
    text = serializers.CharField(min_length=4, max_length=4, required=True, label='验证码')
    image_code_id = serializers.UUIDField(label='验证码唯一性id')

    # 对两个值进行判断
    def validate(self, attrs):
        text = attrs['text']
        image_code_id = attrs['image_code_id']
        redis_conn = get_redis_connection('code')
        redis_text = redis_conn.get('img_%s' % image_code_id)  # redis中获取验证码
        if not redis_text:  # 判断redis中是否获取到
            raise serializers.ValidationError('验证码过期')
        try:
            redis_conn.delete('img_%s' % image_code_id)  # 获取到将验证码记录删除
        except RedisError as e:
            logger.error(e)

        if redis_text.decode().lower() != text.lower():  # 比较redis中验证码和接收前端验证码
            raise serializers.ValidationError('验证码错误')
        return attrs
