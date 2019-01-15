#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-15
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from mall import settings

from django.utils.deconstruct import deconstructible


@deconstructible
class FastDFSStorage(Storage):
    def __init__(self, fdfs_url=None,fdfs_client_conf=None):
        if not fdfs_url:
            self.fdfs_url = settings.FDFS_URL
        if not fdfs_client_conf:
            self.fdfs_client_conf=settings.FDFS_CLIENT_CONF

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        #创建client对象
        client=Fdfs_client(self.fdfs_client_conf)
        #获取文件
        file_data=content.read()
        #上传
        result=client.upload_by_buffer(file_data)
        #判断上传结果
        if result.get('Status')=='Upload successed.':
            return result.get('Remote file_id')
        else:
            raise Exception('上传失败')


    def exists(self, name):
        # 不判断重复上传
        return False

    def url(self, name):
        # 返回完整的url路径
        return self.fdfs_url+name
