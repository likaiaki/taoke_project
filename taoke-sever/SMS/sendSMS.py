# -*- coding: utf-8 -*-
import sys
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.client import AcsClient
import json
import uuid
import json

"""
短信业务调用接口示例，版本号：v20170525

Created on 2017-06-12

"""

# 签名必须是在阿里云后台添加并且通过审核的
class SMS:
    def __init__(self, ACCESS_KEY_ID = "LTAIgXLaQd7DPF0j", ACCESS_KEY_SECRET = "2tPkOWLRnlT3cVopL3Nyd16zfDb3hZ", SIGN_NAME='光点视频桌面'):
        REGION = "cn-hangzhou"
        PRODUCT_NAME = "Dysmsapi"
        DOMAIN = "dysmsapi.aliyuncs.com"
        self.SIGN_NAME = SIGN_NAME
        self.acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
        region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

    def send_sms(self, phone_numbers, template_code, code):
        smsRequest = SendSmsRequest.SendSmsRequest()
        # 申请的短信模板编码,必填
        smsRequest.set_TemplateCode(template_code)

        # 短信模板变量参数
        if code is not None:
            params = {'number': code}
            smsRequest.set_TemplateParam(json.dumps(params))

        # 设置业务请求流水号，必填。
        smsRequest.set_OutId(uuid.uuid1())

        # 短信签名
        smsRequest.set_SignName(self.SIGN_NAME)

        # 短信发送的号码列表，必填。
        smsRequest.set_PhoneNumbers(phone_numbers)

        # 调用短信发送接口，返回json
        smsResponse = self.acs_client.do_action_with_exception(smsRequest)

        return json.loads(smsResponse)['Code'] == 'OK'

    def query_send_detail(self, biz_id, phone_number, page_size, current_page, send_date):
        queryRequest = QuerySendDetailsRequest.QuerySendDetailsRequest()
        # 查询的手机号码
        queryRequest.set_PhoneNumber(phone_number)
        # 可选 - 流水号
        queryRequest.set_BizId(biz_id)
        # 必填 - 发送日期 支持30天内记录查询，格式yyyyMMdd
        queryRequest.set_SendDate(send_date)
        # 必填-当前页码从1开始计数
        queryRequest.set_CurrentPage(current_page)
        # 必填-页大小
        queryRequest.set_PageSize(page_size)

        # 调用短信记录查询接口，返回json
        queryResponse = self.acs_client.do_action_with_exception(queryRequest)

        return queryResponse