# Author Caozy
from django.conf.urls import url

from orders import views

urlpatterns=[
    url('^places/$',views.OrderSettlementView.as_view(),name='places'),# 订单页查询
    url('^$',views.OrderView.as_view(),name='order'),# 订单提交

]