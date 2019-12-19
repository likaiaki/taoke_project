# coding=utf-8
import datetime

from bson import ObjectId
from dateutil.relativedelta import relativedelta
from turbo.core.exceptions import ResponseMsg

from models.zhuzhu import model

tb_brokerage = model.UserBrokerage()
tb_user = model.User()


def getList(uid, skip, limit):
    uid = ObjectId(uid)
    return tb_brokerage.find({'uid': uid}).skip(skip).limit(limit).sort('_id', -1)


def get_brokerage_and_count(skip, limit, create_start=None, create_stop=None, complete_start=None, complete_stop=None,
                            commission_type=None, status=None, name=None, tel=None):
    spec = {}
    if create_start and create_stop:
        spec['create_time'] = {'$gt': datetime.datetime.utcfromtimestamp(int(create_start)),
                               '$lt': datetime.datetime.utcfromtimestamp(int(create_stop))}
    if complete_start and complete_stop:
        spec['complete_time'] = {'$gt': datetime.datetime.utcfromtimestamp(int(complete_start)),
                                 '$lt': datetime.datetime.utcfromtimestamp(int(complete_stop))}
    if commission_type:
        spec['commission_type'] = commission_type
    if status:
        spec['status'] = status
    if name:
        users = tb_user.find({'nickname': name})
        spec['uid'] = {"$in": [x['_id'] for x in users]}
    if tel:
        users = tb_user.find({'tel': int(tel)})
        spec['uid'] = {"$in": [x['_id'] for x in users]}
    results = tb_brokerage.find(spec).skip(skip).limit(limit).sort([('atime', -1)])
    count = tb_brokerage.count(spec)
    data = []
    for result in results:
        result['nickname'] = tb_user.find_one({"_id": result['uid']}).get('nickname', '')
        data.append(result)
    return data, count


def detail(uid):
    uid = ObjectId(uid)
    now = datetime.datetime.now()
    last_month_one = datetime.datetime(now.year, now.month, 1) + relativedelta(months=-1)
    now_month_one = datetime.datetime(now.year, now.month, 1)
    today_start = datetime.datetime(now.year, now.month, now.day)
    yestoday_start = datetime.datetime(now.year, now.month, now.day) + relativedelta(days=-1)

    _ = tb_brokerage.find(
        {'uid': uid, 'status': 'create', 'create_time': {'$gte': last_month_one, '$lt': now_month_one}})
    last_moth_reckon = sum([float(f.get('pub_share_pre_fee', 0)) for f in _])

    _ = tb_brokerage.find({'uid': uid, 'status': 'pay', 'create_time': {'$gte': last_month_one, '$lt': now_month_one}})
    last_moth_pay = sum([float(f.get('pub_share_pre_fee', 0)) for f in _])

    _ = tb_brokerage.find({'uid': uid, 'status': 'create', 'create_time': {'$gte': now_month_one}})
    now_moth_reckon = sum([float(f.get('pub_share_pre_fee', 0)) for f in _])

    _ = tb_brokerage.find({'uid': uid, 'status': 'create', 'create_time': {'$gte': today_start}})
    today_reckon = sum([float(f.get('pub_share_pre_fee', 0)) for f in _])
    today_num = _.count()

    _ = tb_brokerage.find({'uid': uid, 'status': 'create', 'create_time': {'$gte': yestoday_start, '$lt': today_start}})
    yestoday_reckon = sum([float(f.get('pub_share_pre_fee', 0)) for f in _])
    yestoday_num = _.count()

    u_info = tb_user.find_one({'_id': uid})
    if not u_info:
        raise ResponseMsg(-9, '登录已失效!')
    return {
        'balance': u_info.get('balance', 0),
        'total_balance': '%.2f' % u_info.get('total_balance', 0),
        'last_moth_pay': '%.2f' % last_moth_pay,  # 上月结算到账
        'last_moth_reckon': '%.2f' % last_moth_reckon,  # 上月预估
        'now_moth_reckon': '%.2f' % now_moth_reckon,  # 本月预估
        'today_reckon': '%.2f' % today_reckon,  # 今天预估
        'today_num': today_num,  # 今天付款笔数
        'yestoday_reckon': '%.2f' % yestoday_reckon,  # 昨天预估收益
        'yestoday_num': yestoday_num,  # 昨天付款笔数
    }
