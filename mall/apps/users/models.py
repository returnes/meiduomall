from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.models import BaseModel


# Create your models here.

class User(AbstractUser):
    '''用户信息表'''
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱激活状态')
    default_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='users', verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModel):
    '''收货地址'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_address',verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_address', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_address',verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='收货地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='邮箱')
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '地址信息'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
