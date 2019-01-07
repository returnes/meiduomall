from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from users.models import User
from django_redis import get_redis_connection

from users.serializers import RegisterModelSerializers


class LoginView(View):
    def get(self):
        return HttpResponse('hello')

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