import datetime
import json
import time

from bson import ObjectId
from turbo.core.exceptions import ResponseMsg

from helpers.zhuzhu import Redis, redisKey
from models.zhuzhu import model

tb_user = model.User()
tb_user_coupon = model.UserCoupon()
tb_usertoken = model.UserToken()
tb_telcode = model.TelCode()
tb_withdraw_log = model.WithDrawLog()
tb_commission_rate = model.CommissionRate()


def get_highest_commission_rate():
    commission_rate = tb_commission_rate.find_one()
    return float(commission_rate.get('user_c', 0))


def get_user_buy_commission_rate():
    commission_rate = tb_commission_rate.find_one()
    return float(commission_rate.get('user_v', 0))


def url_add_relation_id(item, token=None):
    """
    添加渠道id
    :return:
    """
    click_url = item.get('click_url')
    coupon_click_url = item.get('coupon_click_url')
    coupon_share_url = item.get('coupon_share_url')
    token_info = tb_usertoken.find_one({'token': token})
    if not token_info:
        return
    u_info = tb_user.find_one({"_id": ObjectId(token_info.get('uid'))})
    if u_info and u_info.get('relation_id'):
        relation_id = u_info.get('relation_id')
        if not relation_id:
            return
        if click_url:
            item['click_url'] = click_url + '&relationId=' + str(relation_id)
        if coupon_click_url:
            item['coupon_click_url'] = coupon_click_url + '&relationId=' + str(relation_id)
        if coupon_share_url:
            item['coupon_share_url'] = coupon_share_url + '&relationId=' + str(relation_id)


def get_estimated_earnings(item, token=None):
    """
    计算预估收益
    :return:
    """
    commission_rate = float(item.pop('commission_rate', 0))  # 佣金比例
    if 'jdd_price' in item.keys():
        origin_price = float(item.get('jdd_price', 0))  # 原价
        jdd_num = int(item.get('jdd_num', 0))  # 原价
        estimated_earnings_total = commission_rate * origin_price * jdd_num  # 预估总收益
    else:
        origin_price = float(item.get('zk_final_price', 0))  # 原价
        coupon_amount = float(item.get('coupon_amount', 0))  # 优惠额度
        estimated_earnings_total = commission_rate * (origin_price - coupon_amount)  # 预估总收益
    if token:
        u_info = getUserInfo(getUserId(token))
        if u_info:
            estimated_earnings_user = float(u_info.get('commission_rate', '0')) * estimated_earnings_total / 100 / 100
            return "{0:.2f}".format(estimated_earnings_user)
    estimated_earnings_user = int(get_user_buy_commission_rate() * estimated_earnings_total / 100) / 100
    return "{0:.2f}".format(estimated_earnings_user)


def parse_time_to_timestamp(coupon_start_time):
    if isinstance(coupon_start_time, str):
        if '-' in coupon_start_time:
            d = datetime.datetime.strptime(coupon_start_time, '%Y-%m-%d')
            return int(time.mktime(d.timetuple()))
        elif len(coupon_start_time) == 13:
            return int(coupon_start_time) // 1000
        elif len(coupon_start_time) == 10:
            return int(coupon_start_time)
    elif isinstance(coupon_start_time, int):
        if coupon_start_time > 10000000000:
            return coupon_start_time // 1000
        else:
            return coupon_start_time
    return 0


def getUserId(token):
    uid = Redis.getRedisValue(token)
    if uid:
        return ObjectId(uid)
    token_info = tb_usertoken.find_one({'token': token})
    if token_info:
        uid = token_info.get('uid')
        Redis.setRedisValue(token, uid, 86400)
        return ObjectId(uid)
    raise ResponseMsg(-9, '登录已失效')


def getUserInfo(uid):
    uid = ObjectId(uid)
    rediskey = redisKey.getUserInfoKey(uid)
    info = Redis.getRedisValue(rediskey)
    if info:
        return json.loads(info)
    else:
        info = tb_user.find_one({'_id': uid}, {"atime": 0, 'passwd': 0, 'invite_time': 0})
        if not info:
            return None
        info['_id'] = str(info['_id'])
        Redis.setRedisValue(rediskey, json.dumps(info), 86400)
        return info


def item_list_format(data, token=None, decode=False):
    items = []
    for item in data:
        if decode:
            item = json.loads(item.decode())
        item['estimated_earnings_user'] = get_estimated_earnings(item, token)
        url_add_relation_id(item, token)
        item['coupon_start_time'] = parse_time_to_timestamp(item.get('coupon_start_time'))
        item['coupon_end_time'] = parse_time_to_timestamp(item.get('coupon_end_time'))
        item['coupon_end_time'] = parse_time_to_timestamp(item.get('coupon_end_time'))
        if item.get('num_iid'):
            item['item_id'] = item.pop('num_iid')
        items.append(item)
    return items
