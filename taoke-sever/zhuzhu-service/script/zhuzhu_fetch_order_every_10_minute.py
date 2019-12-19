import datetime

import realpath
import top
from helpers.zhuzhu import user
from lib.c_python import c_python as cp
from models.zhuzhu import model
from top.api.base import TopException

tb_user = model.User()
tb_tbk_order = model.TbkOrder()
tb_user_brokerage = model.UserBrokerage()
tb_commissionRate = model.CommissionRate()
commissionRate = tb_commissionRate.find_one()
user_v = commissionRate.get('user_v')
user_nc_v = commissionRate.get('user_nc_v')
user_c = commissionRate.get('user_c')
user_v_c_p = commissionRate.get('user_v_c_p')
user_v_c_s = commissionRate.get('user_v_c_s')

base_rate = 0.8  # 80%拿出来分佣,剩余用于损耗.10%的技术服务费，还有10%的税、坏账等

user_v = int(user_v) * base_rate
user_nc_v = int(user_nc_v) * base_rate
user_c = int(user_c) * base_rate
user_v_c_p = int(user_v_c_p) * base_rate
user_v_c_s = int(user_v_c_s) * base_rate

self_bug_rate = user_v

# 淘宝客api配置文件
domain = "eco.taobao.com"
port = 443
appkey = "25330814"
secret = "ab31504958f529b9c1b78a50b2e4fec5"

adzone_id = 108893800063  # 渠道&会员


# https://open.taobao.com/api.htm?docId=24527&docType=2
# * * * * * root


def get_order(page, size, scene, order_query_type='settle_time', tk_status=3):
    fields = [
        'tb_trade_parent_id',  # 淘宝父订单号
        'tb_trade_id',  # 淘宝订单号
        'num_iid',  # 商品ID
        'item_title',  # 商品标题
        'item_num',  # 商品数量
        'price',  # 单价
        'pay_price',  # 实际支付金额
        'seller_nick',  # 卖家昵称
        'seller_shop_title',  # 卖家店铺名称
        'commission',  # 推广者获得的收入金额，对应联盟后台报表“预估收入”
        'commission_rate',  # 推广者获得的分成比率，对应联盟后台报表“分成比率”
        'create_time',  # 淘客订单创建时间
        'earning_time',  # 淘客订单结算时间
        'tk_status',  # 淘客订单状态，3：订单结算，12：订单付款， 13：订单失效，14：订单成功
        'income_rate',  # 收入比率，卖家设置佣金比率+平台补贴比率
        'pub_share_pre_fee',  # 效果预估，付款金额*(佣金比率+补贴比率)*分成比率
        'auction_category',  # 类目名称
        'alipay_total_price',  # 付款金额
        'total_commission_rate',  # 佣金比率
        'total_commission_fee',  # 佣金金额
        'subsidy_rate',  # 补贴比率
        'subsidy_type',  # 补贴类型，天猫:1，聚划算:2，航旅:3，阿里云:4
        'subsidy_fee',  # 补贴金额
        'relation_id',  # 渠道关系ID
        'special_id',  # 会员运营id
        'click_time',  # 跟踪时间
    ]
    req = top.api.TbkOrderGetRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))
    req.fields = ','.join(fields)
    req.span = 11 * 60  # 60~1200 秒
    req.page_no = page
    req.page_size = size
    req.tk_status = tk_status  # 订单状态，1: 全部订单，3：订单结算，12：订单付款， 13：订单失效，14：订单成功； 订单查询类型为‘结算时间’时，只能查订单结算状态
    # req.start_time = "2019-05-29 16:40:00"  # (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    req.start_time = (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

    req.order_query_type = order_query_type  # 订单查询类型，创建时间“create_time”，或结算时间“settle_time”
    req.order_scene = scene  # 1:常规订单，2:渠道订单，3:会员运营订单
    req.order_count_type = 1  # 1: 2方订单，2: 3方订单，如果不设置，或者设置为1，表示2方订单
    try:
        resp = req.getResponse()
        return resp['tbk_order_get_response']['results'].get("n_tbk_order", [])
    except TopException as e:
        print(e)
        return []


def insert_create_data(scene):
    orders = get_order(1, 20, scene, 'create_time', 12)
    for order in orders:
        relation_id = order.get('relation_id', '')
        special_id = order.get('special_id', '')

        v = 0
        if special_id:
            commission_type = "shopping"
            user_info = tb_user.find_one({'special_id': special_id})
            if not user_info:
                continue
            if user_info.get('vip', 0) == 0:
                print('vip is 0')
                continue
        elif relation_id:
            commission_type = "share"
            user_info = tb_user.find_one({'relation_id': relation_id})
        else:
            continue

        channel = user_info.get('channel', 0)
        if channel == 0:  # 普通会员，自己购买　
            v = user_v
        elif channel == 1:  # 非高级会员，购买
            v = user_nc_v
        elif channel == 2:
            if not special_id:  # 高级会员,分享
                v = user_v_c_s
            else:  # 高级会员,购买
                v = user_c
        if not user_info:
            continue
        uid = user_info['_id']
        from_uid = None
        if user_info.get('use_invite_code', None):
            from_user = tb_user.find_one({'invite_code': user_info.get('use_invite_code')})
            if from_user:
                from_uid = from_user['_id']
        I = {
            'uid': uid,
            'msg': '返佣',
            'item_title': order.get('item_title', ''),
            'item_num': order.get('item_num', 1),
            'num_iid': order.get('num_iid', ''),
            'status': 'create',
            'commission_type': commission_type,
            'trade_id': order.get('trade_id', ''),
            'trade_parent_id': order.get('trade_parent_id', ''),
            'relation_id': order.get('relation_id', ''),
            'special_id': order.get('special_id', ''),
            'alipay_total_price': order.get('alipay_total_price', ''),
            'create_time': cp.strToTime(order.get('create_time', '')),
            'complete_time': None,
            'pub_share_pre_fee': int(float(order.get('pub_share_pre_fee', 0)) * float(v)) / 100,
        }

        if not tb_user_brokerage.find_one({'trade_id': order.get('trade_id', ''), 'uid': uid}):
            if channel == 1:
                finish = user_info.get('channel_task', {}).get('finish', 0)
                data = {"$inc": {'channel_task.finish': 1}, }
                if finish >= 2:
                    data['$set'] = {
                        'channel': 2,
                        'commission_rate': str(commissionRate.get('user_c'))
                    }
                user.update({'_id': user_info['_id']}, data)
            if channel == 1 and not special_id:  # 非高级会员分享，不得佣金
                continue
            tb_user_brokerage.insert(I)
            print('insert', order.get('trade_id', ''), 'special_id', special_id, 'relation_id', relation_id, )

        if from_uid:
            I.pop('_id', None)
            I['uid'] = from_uid
            I['msg'] = '下线返佣, %s' % uid
            I['commission_type'] = "subordinate"
            I['pub_share_pre_fee'] = int(float(order.get('pub_share_pre_fee', 0)) * float(user_v_c_p)) / 100

            if not tb_user_brokerage.find_one({'trade_id': order.get('trade_id', ''), 'uid': from_uid}):
                tb_user_brokerage.insert(I)
                print('insert from', order.get('trade_id', ''), 'special_id', special_id, 'relation_id', relation_id, )


def update_create_data(scene):
    orders = get_order(1, 20, scene, 'settle_time', 3)
    for order in orders:
        relation_id = order.get('relation_id', '')
        special_id = order.get('special_id', '')
        if special_id:
            user_info = tb_user.find_one({'special_id': special_id})
        elif relation_id:
            user_info = tb_user.find_one({'relation_id': relation_id})
        else:
            continue
        if not user_info:
            continue
        uid = user_info['_id']
        from_uid = None
        if user_info.get('use_invite_code', None):
            from_user = tb_user.find_one({'invite_code': user_info.get('use_invite_code')})
            if from_user:
                from_uid = from_user['_id']
        U = {
            'status': 'complete',
            'complete_time': cp.strToTime(order.get('earning_time', '')),
        }

        tb_user_brokerage.update({'trade_id': order.get('trade_id', ''), 'uid': uid}, {'$set': U})
        print('update', order.get('trade_id', ''))

        if from_uid:
            tb_user_brokerage.update({'trade_id': order.get('trade_id', ''), 'uid': from_uid}, {'$set': U})
            print('update from', order.get('trade_id', ''))


def main():
    insert_create_data(2)
    insert_create_data(3)
    update_create_data(2)
    update_create_data(3)


if __name__ == '__main__':
    main()
