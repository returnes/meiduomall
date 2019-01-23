# Author Caozy
from django.conf.urls import url

from pay import views

urlpatterns=[
    # url(r'^orders/?P<order_id>\d{20}/$',name='payment'),
    url(r'^orders/(?P<order_id>\d+)/$', views.PaymentView.as_view(), name='pay'),
    url(r'^status/$', views.PaymentStatusView.as_view(), name='status'),

]