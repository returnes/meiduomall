#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:caozy time:19-1-10
from rest_framework_jwt.settings import api_settings


def token_jwt(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token
