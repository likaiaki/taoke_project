# -*- coding:utf-8 -*-

import json
import random
import re
from urllib.parse import parse_qsl, urlencode

import datetime
import uuid

import requests
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayFundTransToaccountTransferModel import AlipayFundTransToaccountTransferModel
from alipay.aop.api.request.AlipayFundTransToaccountTransferRequest import AlipayFundTransToaccountTransferRequest
from bson import ObjectId
from turbo.core.exceptions import ResponseMsg

from SMS import sendSMS
from helpers.zhuzhu import tbk
from helpers.zhuzhu.util import getUserId, getUserInfo, item_list_format
from models.zhuzhu import model
from . import Redis, redisKey

tb_user = model.User()
tb_user_coupon = model.UserCoupon()
tb_usertoken = model.UserToken()
tb_telcode = model.TelCode()
tb_withdraw_log = model.WithDrawLog()

tb_commission_rate = model.CommissionRate()
commission_rate = tb_commission_rate.find_one()

SMS = sendSMS.SMS(SIGN_NAME='速诺科技')


def update(Q, U):
    tb_user.update(Q, U)
    Redis.deleteRedisValue(redisKey.getUserInfoKey(Q['_id']))


def auth_callback(token, code, type):
    u_info = getUserInfo(getUserId(token))
    data = {
        'code': code,
        'client_id': 25330814,
        'client_secret': 'ab31504958f529b9c1b78a50b2e4fec5',
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://taobaosavemoney.adesk.com/auth_callback',
    }
    resp = requests.post(url="https://oauth.taobao.com/token", data=data, timeout=10)
    data = resp.json()
    access_token = data['access_token']
    status, result = tbk.user_register(type, access_token)
    if status:
        if type == 'vip':
            if u_info and u_info.get('vip', 0) == 1:
                return status, result
            special_id = result['special_id']
            new_data = {'special_id': special_id,
                        'vip': 1,
                        'commission_rate': str(commission_rate.get('user_v', '0')), }
            update({'_id': ObjectId(u_info['_id'])}, {'$set': new_data})
            return status, result
        else:
            if u_info and u_info.get('channel', 0) != 0:
                return status, result
            relation_id = result['relation_id']
            new_data = {
                'relation_id': relation_id,
                'channel': 1,
                'channel_task': {'finish': 0, 'total': 3},
                'commission_rate': str(commission_rate.get('user_nc_v', '0')),
            }
            update({'_id': ObjectId(u_info['_id'])}, {'$set': new_data})
            return status, result
    else:
        return status, result


def checkPasswd(tel, passwd):
    if len(passwd) != 32:
        return False
    return not not tb_user.find_one({'tel': tel, 'passwd': passwd})


def genCode():
    code = str(random.random())[2:10]
    if not tb_user.find_one({'code': code}):
        return code
    else:
        genCode()


def login(tel, code, type):
    tel = int(tel)
    if (type == 'code' and checkTelCode(tel, code)) or (type == 'passwd' and checkPasswd(tel, code)):
        u_info = tb_user.find_one({'tel': tel})
        if not u_info:
            uid = tb_user.insert({
                'tel': tel,
                'nickname': '',
                'avatar': '',
                'invite_code': '',
                'use_invite_code': '',
                'passwd': None,
                'vip': 0,
                'channel': 0,
                'atime': datetime.datetime.now(),
            })
            vip = 0
        else:
            uid = u_info['_id']
            vip = u_info.get('vip', 0)
        token = genToken(uid)
        tb_usertoken.insert({'uid': uid, 'token': token})
        return token, vip
    else:
        raise ResponseMsg(-1, '验证码不正确' if type == 'code' else '密码不正确')


def bind(token, data):
    uid = getUserId(token)
    update({'_id': ObjectId(uid)}, {"$set": data})
    u_info = tb_user.find_one({'_id': ObjectId(uid)})
    return u_info.get('vip', 0)


def setPasswdAndCode(token, passwd, code):
    uid = getUserId(token)
    u_info = tb_user.find_one({'_id': uid})
    if not u_info:
        raise ResponseMsg(-9, '登录已失效')
    if len(passwd) != 32:
        raise ResponseMsg(-1, '密码无效')
    doc = {'passwd': passwd}
    if not u_info.get('usecode', ''):
        doc['usecode'] = code
    update({'_id': uid}, {'$set': doc})


def firstLogin(token):
    uid = getUserId(token)
    u_info = tb_user.find_one({'_id': uid})
    return not u_info.get('passwd', '')


def genToken(uid):
    uid = str(uid)
    token = str(uuid.uuid1())
    Redis.setRedisValue(token, uid, 86400)
    return token


def sendTelCode(tel):
    tel = int(tel)
    code = str(random.random())[3:7]
    if SMS.send_sms(tel, 'SMS_91850019', code):
        tb_telcode.insert({
            'tel': tel,
            'code': code,
        })
        return True
    else:
        raise ResponseMsg(-1, '验证码发送失败,请稍后再试')


def checkTelCode(tel, code):
    # if code == '1234':
    #     return True
    tel = int(tel)
    code = str(code)
    info = tb_telcode.find_one({'tel': tel, 'code': code})
    if info:
        tb_telcode.remove({'tel': tel})
        return True
    raise ResponseMsg(-1, '验证码不正确')


def getFavoriteList(token, skip=None, limit=None):
    uid = getUserId(token)
    u_info = tb_user.find_one({'_id': ObjectId(uid)})
    item_ids = u_info.get('favorite', [])
    if item_ids and len(item_ids) > 0:
        if skip is not None and limit is not None:
            item_ids = item_ids[skip:limit]
        items = tbk.item_query(item_ids, token)
        data = []
        for result in items:
            nums = re.findall('[0-9\.]{1,}', result.get('coupon_info', ''))
            if len(nums) == 2:
                result['coupon_start_fee'] = int(nums[0])
                result['coupon_amount'] = int(nums[1])
            elif len(nums) == 1:
                result['coupon_start_fee'] = 0
                result['coupon_amount'] = int(nums[0])
            else:
                result['coupon_start_fee'] = 0
                result['coupon_amount'] = 0
            data.append(result)
        return item_list_format(data, token)
    else:
        return []


def addToFavorite(token, item_id):
    uid = getUserId(token)
    update({'_id': ObjectId(uid)}, {"$addToSet": {'favorite': item_id}})


def is_favorite(token, item_id):
    uid = getUserId(token)
    u_info = tb_user.find_one({'_id': ObjectId(uid)})
    if item_id in u_info.get('favorite', []):
        return True
    else:
        return False


def delete_favorite(token, item_ids):
    uid = getUserId(token)
    update({'_id': ObjectId(uid)}, {"$pull": {'favorite': {'$in': item_ids}}})


def get_coupon_list(token, skip, limit):
    uid = getUserId(token)
    results = tb_user_coupon.find({'uid': ObjectId(uid)}, {"uid": 0, '_id': 0}).skip(skip).limit(limit)
    data = []
    for result in results:
        data.append(result)
    return data


def add_coupon(token, data):
    uid = getUserId(token)
    item = tb_user_coupon.find_one({'item_id': data['item_id']})
    if item:
        tb_user_coupon.update_one({'item_id': data['item_id']}, {'$addToSet': {"uid": uid}})
    else:
        data['uid'] = [uid]
        tb_user_coupon.insert_one(data)


def deleteCoupon(token, item_ids):
    uid = getUserId(token)
    tb_user_coupon.update_many({'item_id': {'$in': item_ids}}, {"$pull": {'uid': uid}})


def updateUserInfo(token, data):
    uid = getUserId(token)
    update({'_id': ObjectId(uid)}, {"$set": data})


def makeInviteCode():
    code = str(random.random())[2:8]
    if not tb_user.find_one({'code': code}):
        return code
    else:
        makeInviteCode()


def checkInviteCode(code):
    return tb_user.find_one({'invite_code': code, })


def setInviteCode(token, code):
    uid = getUserId(token)
    result = checkInviteCode(code)
    if result:
        if str(result['_id']) == uid:
            raise ResponseMsg(-1, '不可使用自己的邀请码!')
        else:
            update({'_id': ObjectId(uid)}, {"$set": {'use_invite_code': code, 'invite_time': datetime.datetime.now()}})
    else:
        raise ResponseMsg(-1, '无效的邀请码')


def get_withdraw_log(token):
    uid = getUserId(token)
    results = tb_withdraw_log.find({'uid': ObjectId(uid), 'status': 1})
    data = []
    for result in results:
        data.append({
            'atime': result['atime'],
            'alipay': result['alipay'],
            'name': result['name'],
            'amount': result['amount'],
        })
    return data


def request_withdraw(token, amount):
    u_info = getUserInfo(getUserId(token))
    balance = float(u_info.get('balance', 0))  # 账户余额
    amount = float(amount)  # 提现金额
    if amount < 0.1:
        raise ResponseMsg(-1, "提现金额不得低于0.1元")
    if amount > balance:
        raise ResponseMsg(-1, "账户余额不足")
    else:
        data = {
            'uid': u_info['_id'],
            'order_id': '',
            'pay_date': '',
            'amount': amount,
            'alipay': u_info.get('alipay', ''),
            'name': u_info.get('name', ''),
            'status': 0,
            'atime': datetime.datetime.now()
        }
        new_balance = str((int(balance * 100) - int(amount * 100)) / 100)
        tb_user.update_one({'_id': ObjectId(u_info['_id'])}, {'$set': {'balance': new_balance}})
        wid = str(tb_withdraw_log.insert_one(data).inserted_id)
        result = trans_to_account(wid, amount, data['alipay'], data['name'])
        out_biz_no = result.get('out_biz_no')
        if result.get('code') == '10000':
            new_data = {
                'order_id': result['order_id'],
                'pay_date': result['pay_date'],
                'status': 1,
                'reason': result['msg'],
                'result': result
            }
            tb_withdraw_log.update_one({'_id': ObjectId(out_biz_no)}, {"$set": new_data})
            return True, "提现成功!"
        else:
            # TODO 加个邮件通知
            new_data = {
                'status': 2,
                'reason': result['sub_msg'],
                'result': result
            }
            tb_withdraw_log.update_one({'_id': ObjectId(out_biz_no)}, {"$set": new_data})
            return False, result['sub_msg']


alipay_app_id = 2019061065476798
alipay_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAhRpdMg90WW7cgrRropQb6ndTmZuT3/Y0kqyZH7WepTr9TKTAg09dtE0J5gTsA9Z6V9LAtrRiaVtK15QEVu5luYsAPF4+s6bof9s1A4a7GPzIk+S5Twpm7IdvgkPya7hOSCZyjKVVr54ILxtOaRgazbY9haXOk67mPI+JTV4neE0XXhDCD8+vcEpgZy3BjsOqljrqfxWkAD480oqMmPEW/TDRG9yOSbktyIjpy7QHmdreP5nlKJftGEp7fgJCE28gfpRba4TPviowdAraOKiC4BaxFlVOjkHysBCgNN5HFfYb2SQR6xaKJFdOs8Wn/7qaDGe3B6ASnd+do+uw+xGXBQIDAQAB"
alipay_app_private = "MIIEpAIBAAKCAQEAzztkWcuR/ilEPqtXNdl0wJW77yMV+y7fc5sUshvXfWgeHYlkC0maoGXjPucshNweoSiXlmK7l0ZaLsoJiLs+yTg8iNsRTVJngI0jFrw5AouQL+0t4FzvfDnC040GoE8QD7sqTgtbOIzGEYcXHwlAKJrT1JdGfJA6W+xP1fmvXMqNm4ljRd7mPDFWcH+fMvbP0U5xgB5NPP6RJsncDLkJ9P1FF7i0lX+zKSquPtDjpXj/cItZQxAUvJN8LPxnJ9FmD/Px60z+2HrFwHW+iJih0OEDu+xDgTK6n+64pKytS0xHoGFs5maSzWd4U2odvN0rpQuNTsLc0dEeKeUibtrvMwIDAQABAoIBAQC+m+pZjZzjIiHbYs38gd+ZpCAQfT0ipKJzOxl2GZXDi5jnog+bMkA/eHfky81vBuhFY4jKklXpdpRMpRjP4yqE+mzzlEv9yuXYn/i+WLI3XRdqfcXMsK62nIpO+1A084PadFUdI+TrxtAIHzFtIp0YvBBLYjk7KY4ELv/f2KErvpqJjEYVeYlnuuEPO8T+RTeTmtPG+UV3xrbdRGw6ZVmgbPLrieTKOpp3KGRX+8jDRP3e5HzuyVTaYXdlilvR1RrmuZ65mPWyaa5fe5ytLhdNAg0LjRoe7y5i4bbWwOjspPs1mDqyrz0UJehtzPqz5Wd16C39wTlB7pLUzFdgUZPBAoGBAPY4TNo7mf+jlUqxAYoet/8MDjUFQva1tc5r32GoBol7bIQIEiE5zu+GikFtYZS6pyifu3c0xYsLBLsVC8wlw0iHA1neF+YILLg15vUgFEiZEVklEBW1NjCpzKR+pfUkxb5Acunrk8g1J3imLOZvKGcyY05C49CappcdbIuNusBPAoGBANd2pCBBI9kaTp0vYot4+KH71pPJlsIN3+LjKX62kd51ZIE4bxfpBzXIdmIl/1uyIBQFkJsRj2Oo+Bo/YIvwfHq2JBxNQE/FRAbpRWIwg8kvjLF/EZArsBtmFGEq2gs6rnUmF41LtYpEHaF7nOu9ai2wDRnRm5ypsiJ4Ep0CUKXdAoGBAJyx/9bzD3KtvJkoRP6NxjM+jNwZWSCBTA7uf986e86LCeiM6lzS2Wt+iAZTgkKQ90jXPwsCPqXagUw+fJ+TeNBzfCJ5QWRX1330b+OYYtBA+dVtzOrDxJT7uw0EvMFigaYuhfNwxUAo89HIj9Km82OZobFwyGM9yL9rLmUx8aPpAoGAUNp7koL/QcwGbiPG9hGqM5b+mazPPvjX6BtYie1W5cTltzwHLFDM3Njh28jof29jbD/+WMKJLVvN5oOb5keTXrUU7e3rUUP0WCeXWtZbzdZjFIRbgd9zEYUH5sKe2hHmP53QvrwHXuBawitR4oDM5GIpOGQY4fwoFZk7WuHwg50CgYABSH6shaTwCVj2saOZKVSn4gBEjwat1oeitJ0UpTH3ja/scHmFm4iriV21gGemQnUVKZyA+woAgSvQ7/ThgN+zBXmmqTpLtRS5ey36oxdXg1I9CzYiafXmrF1aatBAhmwrvGaGsMFAD6LZRDMVa6z8W7U4AdZccqpp7Y3fb8O0fw=="


def trans_to_account(out_biz_no, amount, alipay, name):  # TODO 待测试
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = 'https://openapi.alipay.com/gateway.do'
    alipay_client_config.app_id = alipay_app_id
    alipay_client_config.app_private_key = alipay_app_private
    alipay_client_config.alipay_public_key = alipay_public_key
    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
    alipay_model = AlipayFundTransToaccountTransferModel()
    alipay_model.out_biz_no = out_biz_no
    alipay_model.payee_type = "ALIPAY_LOGONID"
    alipay_model.amount = str(amount)
    alipay_model.payee_account = alipay
    alipay_model.payee_real_name = name
    alipay_model.remark = "猪猪惠返提现"  # TODO 修改app名字
    request = AlipayFundTransToaccountTransferRequest(biz_model=alipay_model)
    response_content = client.execute(request)
    print(response_content)
    return json.loads(response_content)


def getAllChannel(skip, limit, start=None, stop=None, status=None, tel=None, name=None):
    spec = {}
    if tel:
        spec['tel'] = int(tel)
    elif name:
        spec['name'] = name
    else:
        if start and stop:
            spec['atime'] = {'$gt': datetime.datetime.utcfromtimestamp(start)}
            spec['atime'] = {'$lt': datetime.datetime.utcfromtimestamp(stop)}
        if status:
            spec['channel'] = int(status)
    results = tb_user.find(spec).skip(skip).limit(limit).sort([('atime', -1)])
    data = []
    for _ in results:
        use_invite_code = _['use_invite_code']
        if use_invite_code:
            res = tb_user.find_one({'invite_code': use_invite_code})
            if not res:
                print(use_invite_code)
                continue
            _['invite_nickname'] = res['nickname']
        data.append(_)
    count = results.count()
    return data, count


def getInviteStatus(skip, limit, start, stop, tel, name, code):
    spec = {'use_invite_code': {"$ne": ''}}
    if tel:
        spec['tel'] = int(tel)
    elif name:
        spec['name'] = name
    elif code:
        spec['code'] = code
    else:
        if start and stop:
            spec['atime'] = {'$gt': datetime.datetime.utcfromtimestamp(start)}
            spec['atime'] = {'$lt': datetime.datetime.utcfromtimestamp(stop)}
    results = tb_user.find(spec).skip(skip).limit(limit).sort([('atime', -1)])
    data = []
    for _ in results:
        use_invite_code = _['use_invite_code']
        if use_invite_code:
            res = tb_user.find_one({'invite_code': use_invite_code})
            if not res:
                print(use_invite_code)
                continue
            _['invite_nickname'] = res['nickname']
        data.append(_)
    count = results.count()
    return data, count


def getInvitedList(token, skip=0, limit=20):
    u_info = getUserInfo(getUserId(token))
    invite_code = u_info.get('invite_code', '')
    data = []
    results = tb_user.find({'use_invite_code': invite_code}).skip(skip).limit(limit)
    for result in results:
        temp = {
            'avatar': result.get('avatar', ''),
            'nickname': result.get('nickname', ''),
            'invite_time': result.get('invite_time', ''),
        }
        data.append(temp)
    return data
