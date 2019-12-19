import datetime

import realpath
from bson import ObjectId
from dateutil.relativedelta import relativedelta

from models.zhuzhu import model

tb_user = model.User()
tb_user_brokerage = model.UserBrokerage()
tb_commissionRate = model.CommissionRate()
tb_settle_log = model.SettleLog()

commissionRate = tb_commissionRate.find_one()
user_v = commissionRate.get('user_v')
user_nc_v = commissionRate.get('user_nc_v')
user_c = commissionRate.get('user_c')
user_v_c_p = commissionRate.get('user_v_c_p')
settlement_date = commissionRate.get('settlement_date')


# 提前一天跑脚本,将 计算的钱打到用户账户里 24号早上1点开始,上个月1-30号的数据
# vsp
# * 1 * * * root

def auto_settle_each_month(start, stop):
    results = tb_user_brokerage.find({'complete_time': {"$gte": start, "$lt": stop}, 'status': 'complete'})
    for result in results:
        uid = result['uid']
        u_info = tb_user.find_one({'_id': ObjectId(uid)})
        if u_info:
            pub_share_pre_fee = float(result.get('pub_share_pre_fee', 0))
            new_data = {"$inc": {
                "balance": pub_share_pre_fee,
                'total_balance': pub_share_pre_fee,
            }}
            tb_user.update_one({'_id': ObjectId(uid)}, new_data)
            tb_user_brokerage.update_one({'_id': result['_id']}, {'$set': {'status': 'pay'}})
            data = {
                'uid': uid,
                'brokerage_id': result['_id'],
                'trade_id': result['trade_id'],
                'commission_type': result['commission_type'],
                'create_time': result['create_time'],
                'complete_time': result['complete_time'],
                'pub_share_pre_fee': pub_share_pre_fee,
                'atime': datetime.datetime.now(),
            }
            tb_settle_log.insert_one(data)


def main():
    today = datetime.datetime.now()
    if today == int(settlement_date) - 1:
        start = datetime.datetime(today.year, today.month, 1) + relativedelta(months=-1)
        stop = datetime.datetime(today.year, today.month, 1)
        auto_settle_each_month(start, stop)
    else:
        print('today is not settle day')


if __name__ == '__main__':
    main()
