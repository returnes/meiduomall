#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-15
from rest_framework import serializers

from goods.models import SKU


class HotSKUListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')
