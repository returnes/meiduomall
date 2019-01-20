from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework_jwt.views import ObtainJSONWebToken

from carts.utils import merge_cart_cookie_to_redis
from goods.models import SKU
from users.models import User, Address
from django_redis import get_redis_connection

from users.serializers import RegisterModelSerializers, UserCenterInfoModelSerializer, UserEmailInfoSerializer, \
    AddressSerializer, TitleSerializer, UserBrowsingHistorySerializer, UserBrowsingHistoryListSerializer
from users.utils import check_token


class RegisterUsernameCountView(APIView):
    '''
    注册用户名验证
    http://127.0.0.1:8000/users/usernames/username/count/
    '''

    def get(self, request, username):
        # 通过模型查询,获取用户名个数
        count = User.objects.filter(username=username).count()
        # 组织数据
        context = {
            'count': count,
            'username': username
        }
        return Response(context)


class RegisterMobileCountView(APIView):
    '''
    注册手机号验证
     http://127.0.0.1:8000/users/mobile/mobile/count/
    '''

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        context = {
            'count': count,
            'mobile': mobile
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


# 邮箱认证：http://api.meiduo.site:8000/users/emails/
# 一级视图实现
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

# 三级视图实现

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
# http://www.meiduo.site:8080/success_verify_email.html?token=

# 一级视图是实现
class UserEmailVerifyView(APIView):
    '''
    0.
    1.接收参数token
    2.token校验解密
    3.数据库邮箱状态更改
    4.返回数据
    '''

    # permission_classes = [IsAuthenticated]
    def get(self, request):
        params = request.query_params
        token = params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_id = check_token(token)
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=user_id)
        user.email_active = True
        user.save()
        return Response({'msg': 'ok'})


from rest_framework.viewsets import ModelViewSet

# class AddressViewSet(mixins.ListModelMixin, mixins.CreateModelMixin):
class AddressViewSet(ModelViewSet):
    '''
    收货信息保存视图
    0.权限认证的用户才能调用
    1.序列化器定义
    2.查询集定义，只能查询表中未被逻辑删除的数据,重写方法
    3.重写create（post）方法，限制用户保存地址条数
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.filter(is_delete=False)


    def create(self, request, *args, **kwargs):
        '''地址创建'''
        if self.request.user.addresses.count() >= 20:
            return Response({'message': '保存数量达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(self.request,*args,**kwargs)


    def list(self, request, *args, **kwargs):
        """
        获取用户地址列表
        """
        # 获取所有地址
        queryset = self.get_queryset()
        # 创建序列化器
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        # 响应
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    def destroy(self, request, *args, **kwargs):
        '''地址删除'''
        address=self.get_object()
        address.is_delete=True
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'],detail=True)
    def title(self,request,pk=None,address_id=None):
        '''修改标题'''
        address=self.get_object()
        serializer=TitleSerializer(instance=address,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    @action(methods=['put'],detail=True)
    def status(self,request,pk=None):
        '''设置默认地址'''
        address=self.get_object()
        request.user.default_address=address
        request.user.save()
        return Response({'message':'ok'},status=status.HTTP_200_OK)

class UserBrowsingHistoryView(CreateAPIView,ListAPIView):
    '''
    历史记录存储，查询
    此处历史记录存储到redis中
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = UserBrowsingHistorySerializer

    def get(self, request, *args, **kwargs):
        user=request.user # 获取用户
        redis_conn = get_redis_connection('history')
        history_sku_ids=redis_conn.lrange('history_%s' % user.id, 0, -1) #redis中获取浏览历史
        skus = []
        for sku_id in history_sku_ids:
            sku = SKU.objects.get(pk=sku_id)
            skus.append(sku)
        serializer=UserBrowsingHistoryListSerializer(skus,many=True)
        return Response(serializer.data)

class UserAuthorizationView(ObtainJSONWebToken):
    '''
    登录验证重写方法，实现登录时候合并购物车，cookie-》redis
    '''
    def post(self, request, *args, **kwargs):
        '''重写post方法'''
        response=super().post(request)
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            response=merge_cart_cookie_to_redis(request,user,response)

            return response