# -*- coding:utf-8 -*-
import os

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))

if os.path.exists(os.path.join(SERVER_DIR, '__test__')):
    Debug = True
else:
    Debug = False

AESKEY = "dAXahiGJXKkkP4Yr"

# 快递鸟
if Debug:
    EBusinessID = "test1527596"
    AppKey = "cba6df6d-f612-49a2-a600-52c4e6f97057"
    ReqURL = "http://sandboxapi.kdniao.com:8080/kdniaosandbox/gateway/exterfaceInvoke.json"
    CustomerName = "admin"
    CustomerPwd = "kdniao"
else:
    EBusinessID = "1528539"
    AppKey = "e8256890-cb96-4c03-b711-50a938361259"
    ReqURL = "http://api.kdniao.com/api/EOrderService"
    CustomerName = "adesknova"
    CustomerPwd = "tryourbest1"
