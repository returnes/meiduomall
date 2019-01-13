from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from areas.models import Area
from areas.serializers import AreaInfoSerializer, AreaSubInfoSerializer


# 视图集实现
class AreaInfoViewSet(ReadOnlyModelViewSet):
    '''
    1.省级，下属地区分别调用自己序列化器
    2.获取查询集，由于查询自关联需要获取省级别/下属地区，所以需要重写获取查询集方法
    '''
    pagination_class = None# 不分页

    def get_queryset(self):
        '''提供数据集'''
        if self.action=='list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()
    def get_serializer_class(self):
        if self.action=='list':
            return AreaInfoSerializer
        else:
            return AreaSubInfoSerializer

