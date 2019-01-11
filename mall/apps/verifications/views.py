from random import randint

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from verifications.serializers import RegisterSMSCodeSerializer
from rest_framework import status
from rest_framework.response import Response
from libs.captcha.captcha import captcha #导入验证码生成模块
from django_redis import get_redis_connection
from libs.yuntongxun.sms import CCP


class RegisterCaptchaView(APIView):
    '''
    图形验证码生成
    http://127.0.0.1:8000/verifications/imagecodes/image_code_id/
    '''
    def get(self,request,image_code_id):
        if not image_code_id:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        code_id,text,image=captcha.generate_captcha() #获取验证码
        print('image_code:',text)
        #保存uuid_code和image_code_id对应存储到redis中
        redis_conn=get_redis_connection('code')
        redis_conn.setex('img_%s'%image_code_id,60,text)
        #返回给前段image_text图片
        return HttpResponse(image,content_type='image/jpeg')

class RegisterSMSCodeView(GenericAPIView):
    '''
    短信验证码
    http://127.0.0.1:8000/verifications/smscodes/mobile/?text=xxx&image_code_id=xxx
    '''
    serializer_class = RegisterSMSCodeSerializer


    def get(self,request,mobile):
        #接收参数，验证参数
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        redis_conn=get_redis_connection('code')
        if redis_conn.get('sms_flag_%s'%mobile): #是否频繁获取
           return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        sms_code='%06d'%randint(0,999999)
        print('sms_code:',sms_code)
        redis_conn.setex('sms_%s'%mobile,5*60,sms_code)
        redis_conn.setex('sms_flag_%s'%mobile,60,1)

        # result=CCP().send_template_sms(mobile, ['sms_code', 5], 1)
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code)
        return Response({'message':'ok'})

