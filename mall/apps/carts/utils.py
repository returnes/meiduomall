# Author Caozy
import base64
import pickle
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(requst,user,response):
    '''
    此方法用于合并购物车，当用户登录时候，将用户cookie中的购物车合并到reids中
    :param request:当前请求对象
    :param user：当前登录对象
    :param response：用于清除cookie
    1.获取cookie数据
    2.如果存在
    3.获取redis数据
    4.保存redis数据
    5.删除cookie中的cart数据
    '''
    cookie_str=requst.COOKIES.get('cart')
    if cookie_str is not None:
        cookie_cart=pickle.loads(base64.b64decode(cookie_str.encode()))
        redis_conn=get_redis_connection('cart')
        redis_cart=redis_conn.hgetall('cart_%s'%user.id)
        # redis_selected=pl.smenbers('cart_selected_%s'%user.id)
        cart={}
        for sku_id,count in redis_cart.items():
            cart[int(sku_id)]=int(count)
        selected_sku_count_id=[]
        for sku_id,selected_count_dict in cookie_cart.items():
            cart[sku_id]=selected_count_dict['count']
            if selected_count_dict['selected']:
                selected_sku_count_id.append(sku_id)
        pl=redis_conn.pipeline()
        pl.hmset('cart_%s'%user.id,cart)
        pl.sadd('cart_selected_%s'%user.id,*selected_sku_count_id)
        pl.execute()
        response.delete_cookie('cart')
        return response
    else:
        return response