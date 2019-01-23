from django.db import models

# Create your models here.
from orders.models import OrderInfo
from utils.models import BaseModel


class Payment(BaseModel):
    order=models.ForeignKey(OrderInfo,on_delete=models.PROTECT,verbose_name='订单编号')
    payment_id=models.CharField(max_length=100,unique=True,null=True,blank=True,verbose_name='支付编号')
    class Meta:
        db_table='tb_payment'