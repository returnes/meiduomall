from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# from QQLoginTool.QQtool import OAuthQQ
from carts.utils import merge_cart_cookie_to_redis
from oauth.serializers import QQAuthUserSerializer
from oauth.utils import generic_open_id
from . import utils
from oauth.models import OAuthQQUser

class QQAuthURLView(APIView):
    '''获取qq登陆的url'''
    def get(self,request):
        state=request.query_params.get('state')# 需要登陆的界面
        # oauth=OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        login_url=utils.get_qq_obj(state=state).get_qq_url()# 调用公共方法获取oauth对象
        return Response({'login_url':login_url})


class QQAuthUserView(APIView):
    '''
    获取qq用户
    1.获取code
    2.获取token
    3.获取openid
    '''
    def get(self,request):
        params=request.query_params
        code=params.get('code')
        if not code:
            return Response({'message':'lost code'},status=status.HTTP_400_BAD_REQUEST)
        try:
            access_token = utils.get_qq_obj().get_access_token(code)  # 调用公共方法获取oauth对象调用获取token的方法
            openid=utils.get_qq_obj().get_open_id(access_token) # 调用公共方法获取oauth对象调用获取openid的方法
        except Exception:
            return Response({'message':'qq server err'},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            token=generic_open_id(openid)
            return Response({'access_token':token})
        else:
            # 存在,应该让用户登陆

            # from rest_framework_jwt.settings import api_settings
            # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # payload = jwt_payload_handler(qquser.user)
            # token = jwt_encode_handler(payload)

            from utils.token_jwt import token_jwt
            token = token_jwt(qquser.user)

            response= Response({
                'token':token,
                'username':qquser.user.username,
                'user_id':qquser.user.id
            })
            response=merge_cart_cookie_to_redis(request,qquser.user,response)
            return response

    def post(self,request):
        '''openid和帐号绑定'''
        serializer=QQAuthUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qquser=serializer.save()
        #token
        from utils.token_jwt import token_jwt
        token = token_jwt(qquser.user)
        response=Response({
            'token':token,
            "user_id":qquser.user.id,
            'username':qquser.user.username,
        })
        response = merge_cart_cookie_to_redis(request, qquser.user, response)
        return response
