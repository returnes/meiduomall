#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-11
from rest_framework import serializers

from areas.models import Area


class AreaInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name']


class AreaSubInfoSerializer(serializers.ModelSerializer):
    subs = AreaInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['subs','id','name']
