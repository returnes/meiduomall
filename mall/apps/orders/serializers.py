# Author Caozy
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from django_redis import get_redis_connection


class CartSKUSerializer(serializers.ModelSerializer):
    '''订单页面购物车序列化器'''
    count=serializers.IntegerField(label='数量',read_only=True)
    class Meta:
        model=SKU
        fields=['id','name','price','default_image_url','count']


class OrderSettlementSerializer(serializers.Serializer):
    '''结算订单序列化器'''
    freight=serializers.DecimalField(label='运费',max_digits=10,decimal_places=2)
    skus=CartSKUSerializer(many=True)



class OrderCommitSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderInfo
        fields=['order_id','address','pay_method']
        read_only_fields=('order_id',)
        extra_kwargs={
            'address':{
                'required':True,
                'write_only':True
            },
            'pay_method':{
                'required':True,
                'write_only':True
            }
        }
    def create(self, validated_data):
        '''
        1.获取当前下单用户
        2.生成下单编号
        3.保存订单数据到orderinfo
        4.获取结算单商品数据，redis
        5.遍历结算商品
            5.1.判断商品库存
            5.2.减少库存、增加销量
            5.3.保存订单商品信息
            5.4.删除redis中计算后的商品信息
        :param validated_data:
        :return:
        '''
        # 保存订单数据OrderInfo
        user=self.context['request'].user
        order_id=timezone.now().strftime('%Y%m%d%H%M%S')+('%06d'%user.id)
        address=validated_data['address']
        pay_method=validated_data['pay_method']

        with transaction.atomic():
            #创建一个保存点
            save_id = transaction.savepoint()
            try:
                order=OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0'),
                    freight=Decimal('10.0'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )
                #保存商品订单数据
                redis_conn= get_redis_connection('cart')
                redis_cart=redis_conn.hgetall('cart_%s'%user.id)
                redis_selected=redis_conn.smembers('cart_selected_%s'%user.id)
                cart={}
                for sku_id in redis_selected:
                    cart[int(sku_id)]=int(redis_cart[sku_id])
                sku_id_list=cart.keys()
                skus=SKU.objects.filter(pk__in=sku_id_list)
                for sku in skus:
                    count=cart[sku.id]
                    if sku.stock<count:
                        raise serializers.ValidationError('库存不足')
                    #原库存
                    origin_stock=sku.stock
                    origin_sales=sku.sales

                    new_stock=origin_sales-count
                    new_sales=origin_sales-count

                    ret=SKU.objects.filter(pk=sku.id,stock=origin_stock).update(stock=new_stock,sales=new_sales)

                    if ret==0:
                        continue
                    order.total_count+=count
                    order.total_amount+=(sku.price*count)
                    OrderGoods.objects.create(
                        order=order,
                        sku = sku,
                        count = count,
                        price = sku.price,
                    )
                    break
                order.save()
            except ValueError:
                raise
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('下单失败')
            transaction.savepoint_commit(save_id)

            # 清除购物车中已经结算的商品
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, *redis_selected)
            pl.srem('cart_selected_%s' % user.id, *redis_selected)
            pl.execute()

            return order