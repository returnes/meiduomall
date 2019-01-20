#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-18
from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    '''
    购物车序列化器
    1.定义参数：sku_id,count,selected
    2.校验参数：sku_id,数据库中是否存在，count库存是否充足

    '''

    sku_id=serializers.IntegerField(label='商品',required=True,min_value=1)
    count=serializers.IntegerField(label='数量',min_value=1,required=True)
    selected=serializers.BooleanField(label='是否选中',default=True,required=False)

    def validate(self, attrs):
        sku_id=attrs['sku_id']
        count=attrs.get('count')
        # 判断商品是否存在
        try:
            sku=SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        # 判断库存是否充足

        if sku.stock<count:
            raise serializers.ValidationError('库存不足')

        return attrs


class CartSKUSerializer(serializers.ModelSerializer):
    '''序列化器用于查询购物车商品'''
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')

class CartDeleteSerializer(serializers.Serializer):
    '''购物车信息删除'''
    sku_id=serializers.IntegerField(label='商品id',required=True)
    def validated_sku_id(self,value):
        try:
            sku=SKU.objects.get(pk=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value