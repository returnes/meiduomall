from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView

from users.models import User
from django_redis import get_redis_connection

from users.serializers import RegisterModelSerializers, UserCenterInfoModelSerializer, UserEmailInfoSerializer
from users.utils import check_token


class RegisterUsernameCountView(APIView):
    '''
    注册用户名验证
    http://127.0.0.1:8000/users/usernames/username/count/
    '''
    def get(self,request,username):
        #通过模型查询,获取用户名个数
        count = User.objects.filter(username=username).count()
        #组织数据
        context = {
            'count':count,
            'username':username
        }
        return Response(context)

class RegisterMobileCountView(APIView):
    '''
    注册手机号验证
     http://127.0.0.1:8000/users/mobile/mobile/count/
    '''
    def get(self,request,mobile):
        count=User.objects.filter(mobile=mobile).count()
        context={
            'count':count,
            'mobile':mobile
        }
        return Response(context)
#
# class RegisterView(APIView):
#     '''
#     注册功能
#     post:http://127.0.0.1:8000/users/
#     '''
#     def post(self,request):
#         data=request.data #获取前端提交数据
#         serializer=RegisterModelSerializers(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         return Response(serializer.data)

class RegisterView(CreateAPIView):
    # queryset = User.objects.all()
    serializer_class = RegisterModelSerializers


from rest_framework.permissions import IsAuthenticated

# 个人中心信息页 http://127.0.0.1:8080/user_center_info.html
# 一级视图实现方法
# class UserCenterInfoView(APIView):
#     '''
#     个人中心信息
#     1.可用过前端传输userid获取用户信息
#     2.可通过request.user获取当前用户
#     3.无论那种都需要权限认证
#     :return
#     '''
#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#         serializer=UserCenterInfoModelSerializer(instance=request.user)
#         return Response(serializer.data)

# 三级视图实现方法，获取单条信息
class UserCenterInfoView(RetrieveAPIView):
    '''获取单个用户集，使用重写get_object方法'''
    permission_classes = [IsAuthenticated]
    serializer_class = UserCenterInfoModelSerializer
    def get_object(self):
        return self.request.user

#邮箱认证：http://api.meiduo.site:8000/users/emails/
#一级视图实现
# class UserEmailInfoView(APIView):
#     '''
#     0.权限认证
#     1.接收前端数据
#     2.校验数据
#     3.更新数据，更新邮箱/更新邮箱状态
#     4.返回数据
#     '''
#     permission_classes = [IsAuthenticated]
#     def put(self,request):
#         data=request.data
#         serializer=UserEmailInfoSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#三级视图实现

class UserEmailInfoView(UpdateAPIView):
    '''
    0.权限认证
    1.获取序列化器
    2.获取queryset，这里之获取当前用户，所以需要重写方法
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmailInfoSerializer
    def get_object(self):
        return self.request.user


# 接收邮箱验证信息
#http://www.meiduo.site:8080/success_verify_email.html?token=

#一级视图是实现
class UserEmailVerifyView(APIView):
    '''
    0.
    1.接收参数token
    2.token校验解密
    3.数据库邮箱状态更改
    4.返回数据
    '''
    # permission_classes = [IsAuthenticated]
    def get(self,request):
        params=request.query_params
        token=params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_id=check_token(token)
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user=User.objects.get(id=user_id)
        user.email_active=True
        user.save()
        return Response({'msg':'ok'})



























