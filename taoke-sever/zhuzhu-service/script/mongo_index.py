from models.zhuzhu.model import *

tb_user = User()
tb_user_coupon = UserCoupon()
tb_user_token = UserToken()
tb_tel_code = TelCode()
tb_user_brokerage = UserBrokerage()

tb_user.ensure_index([('nickname', -1)])
tb_user.ensure_index([('tel', -1)])
tb_user.ensure_index([('invite_code', -1)])
tb_user.ensure_index([('use_invite_code', -1)])
tb_user.ensure_index([('invite_time', -1)])
tb_user.ensure_index([('relation_id', -1)])
tb_user.ensure_index([('special_id', -1)])

tb_user_coupon.ensure_index([('uid', -1)])

tb_user_token.ensure_index([('token', -1)])

tb_tel_code.ensure_index([('tel', -1), ('code', -1)])

tb_user_brokerage.ensure_index([('uid', -1), ('trade_id', -1)])
tb_user_brokerage.ensure_index([('status', -1)])
tb_user_brokerage.ensure_index([('commission_type', -1)])
tb_user_brokerage.ensure_index([('create_time', -1)])
tb_user_brokerage.ensure_index([('complete_time', -1)])

