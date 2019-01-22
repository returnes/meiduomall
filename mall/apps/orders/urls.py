# Author Caozy
from django.conf.urls import url

from orders import views

urlpatterns=[
    url('^places/$',views.OrderSettlementView.as_view(),name='placeorder'),# 订单页查询
    url('^$',views.OrderView.as_view(),name='commitorder'),# 订单提交

]