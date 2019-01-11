#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-11
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature

from mall import settings

#加密
def generic_verify_url(user_id):
    serializer=Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    data={
        'id':user_id
    }
    token=serializer.dumps(data)

    return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()
#解密
def check_token(token):
    serializer=Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    try:
        result = serializer.loads(token)
    except BadSignature:
        return None

    #3.返回user_id
    return result.get('id')