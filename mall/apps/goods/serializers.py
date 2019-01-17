#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-15
from rest_framework import serializers
from .search_indexes import SKUIndex
from goods.models import SKU
from drf_haystack.serializers import HaystackSerializer


class SKUListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'id', 'name', 'price', 'default_image_url', 'comments')