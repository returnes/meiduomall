#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-7
from celery_tasks.main import app
from libs.yuntongxun.sms import CCP

@app.task(name='send_sms_code')
def send_sms_code(mobile,sms_code):
    CCP().send_template_sms(mobile, [sms_code, 5], 1)
