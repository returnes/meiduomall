from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin

from goods.models import SKU
from goods.serializers import SKUListSerializer, SKUIndexSerializer


class HomeView(APIView):
    pass


from rest_framework.generics import ListAPIView


class HotSKUListAPIView(ListCacheResponseMixin,ListAPIView):

    # queryset = SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]
    # queryset = SKU.objects.all()
    serializer_class = SKUListSerializer
    pagination_class = None

    def get_queryset(self):
        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]

class SKUListView(ListAPIView):
    '''商品列表'''
    serializer_class =SKUListSerializer
    # pagination_class = None

    #通过定义过滤后端，实现排序行为
    filter_backends =[OrderingFilter]
    ordering_fields=['create_time','price','sale'] # 前端对应默认/价格/人气

    def get_queryset(self):
        category_id=self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id,is_launched=True)


from drf_haystack.viewsets import HaystackViewSet

class SKUSearchViewSet(HaystackViewSet):
    '''SKU搜索'''
    index_models = [SKU]

    serializer_class = SKUIndexSerializer