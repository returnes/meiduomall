from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection

from goods.models import SKU
from orders.serializers import CartSKUSerializer, OrderSettlementSerializer, OrderCommitSerializer


class OrderSettlementView(APIView):
    '''订单结算视图'''
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user=request.user
        #redis中获取购物车信息
        redis_conn=get_redis_connection('cart')
        # 获取当前用户购物车信息
        redis_carts=redis_conn.hgetall('cart_%s'%user.id)
        carts_selected=redis_conn.smembers('cart_selected_%s'%user.id)
        # 获取选中的商品信息
        order_cart={}
        # 方式一
        for sku_id,count in redis_carts.items():
            if sku_id in carts_selected:
                order_cart[int(sku_id)]=int(count)
        skus=SKU.objects.filter(id__in=[int(skuid) for skuid in carts_selected])
        for sku in skus:
            sku.count=order_cart[sku.id]
        # 方式二
        # for sku_id in carts_selected:
        #     order_cart[int(sku_id)]=int(redis_carts[sku_id])
        # skus=SKU.objects.filter(id__in=order_cart.keys())
        # for sku in skus:
        #     sku.count=redis_carts[sku.id]

        freight = Decimal('10.00')
        serializer=OrderSettlementSerializer({'freight':freight,'skus':skus})
        return Response(serializer.data)


class OrderView(CreateAPIView):
    '''订单提交视图'''
    permission_classes = [IsAuthenticated]
    serializer_class=OrderCommitSerializer
