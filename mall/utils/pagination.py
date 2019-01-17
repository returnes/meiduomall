#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-16
from rest_framework.pagination import PageNumberPagination
class StandardResultsSetPagination(PageNumberPagination):
    '''分页配置类'''

    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 20