from billiard.common import pickle
from django.shortcuts import render

# Create your views here.
import base64
from mutagen.id3 import USER
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializers import CartSerializer,CartSKUSerializer
from django_redis import get_redis_connection

from goods.models import SKU

'''
post:/cart/   购物车添加商品
get:/cart/   获取购物车列表
put 修改购物车物件数量 
delete 删除购物车商品
'''

class CartView(APIView):
    '''
    购物车使用redis方式存储，购物车添加实现用户登陆和用户未登陆，登陆情况下保存数据到redis，未登陆保存到cookie中
    重写用户在验证方法，取消验证
    '''
    def perform_authentication(self, request):
        pass

    def post(self,request):
        '''
        添加购物车：
        1.获取前端提交数据，商品id:sku_id,商品数量：count,是否选中默认为true:selelcted
        2.通过序列化器校验数据
        3.视图获取校验后的数据，判断如果登陆用户保存数据到redis，未登陆保存到cookie中
        3.1登陆用户判断redis中是否有该商品，没有则添加，有则数量累加
        3.2未登陆用户接收前端请求中的cookie，没有则添加，有则解码转字典，累加数量，转字符串编码set_cookie
        :param request:
        :return:
        '''
        data=request.data
        serializer=CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        sku_id=serializer.data['sku_id']
        count=serializer.data.get('count')
        selected=serializer.data.get('selected')
        try:
            user=request.user
        except Exception:
            user=None
        if user!=None and user.is_authenticated:
            '''redis操作'''
            redis_conn=get_redis_connection('cart')
            redis_conn.hset('cart_%s'%user.id,sku_id,count)#hash方式写入redis
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            return Response(serializer.data)



        else:
            '''cookie操作'''

            cart_str=request.COOKIES.get('cart')
            if cart_str is not None:
                cart_dict=pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict={}
            if sku_id in cart_dict:
                origin_count=cart_dict[sku_id]['count']
                count+=origin_count
            cart_dict[sku_id]={
                'count':count,
                'selected':selected
            }
            response=Response(serializer.data)
            cookie_cart=base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart',cookie_cart)
            return response
    def get(self,request):
        '''
        查询购物车
        1.前端get方式请求
        2.接收前端请求
        3.登录用户redis中获取数据
        1）链接redis
        2）hash cat_userid: {sku_id: count}, set selected: {sku_id, sku_id}
        3) 根据商品id获取商品详情信息
        4.未登录用户从cookie中获取数据
        1）判断cookie中是否存在购物车数据
        2）存在解码转换字典
        3）返回数据
        :param request:
        :return:
        '''
        try:
            user=request.user
        except Exception:
            user=None
        if user is not None:
            redis_conn=get_redis_connection('cart')
            if user is not None and user.is_authenticated:
                redis_cart_select=redis_conn.smembers('cart_selected_%s'%user.id)
                redis_cart=redis_conn.hgetall('cart_%s'%user.id)
                cart={}
                for sku_id,count in redis_cart.items():
                    cart[int(sku_id)] = {
                        'count': int(count),
                        'selected': sku_id in redis_cart_select
                    }

        else:
            # 非登录用户,从cookie中获取数据
            cart_str = request.COOKIES.get('cart')

            if cart_str is not None:
                cart = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart = {}

        # 获取所有商品的信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']
        # 序列化数据,并返回响应
        serializer = CartSKUSerializer(skus, many=True)

        return Response(serializer.data)