#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-10
from QQLoginTool.QQtool import OAuthQQ
from mall import settings


def get_qq_obj(state='/'):
    '''
    1.获取qq登陆的url
    2.获取qq登陆的token
    3.获取qq登陆的openid
    :return: oauth对象
    '''
    oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                    redirect_uri=settings.QQ_REDIRECT_URI, state=state)
    return oauth


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature


def generic_open_id(openid):
    print(openid)
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()


def check_access_token(access_token):
    print(access_token)
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    # 对数据进行loads操作
    try:
        data = serializer.loads(access_token)
    except BadSignature:
        return None
    return data['openid']
