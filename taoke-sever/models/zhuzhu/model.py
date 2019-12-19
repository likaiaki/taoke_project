# -*- coding:utf-8 -*-
from datetime import datetime

from bson import ObjectId

from .base import *


class Zone(Model):
    """
    专区表 管理专区
    name:专区名称
    material_id:物料id
    img： 图片
    position: 显示位置，0:只显示在顶部，1:显示在专区推荐，2:全部显示
    count: 当前商品数量
    status: 状态，是否启用，默认启用, 0可用，1删除
    """
    name = 'zhuzhu_zone'

    field = {
        'name': (str, ''),
        'material_id': (str, ''),
        'img': (str, ''),
        'position': (int, 0),
        'count': (int, 0),
        'status': (int, 0),
    }


class LevelOne(Model):
    """
    一级类目表
    name:一级类目名称
    img：图片
    status: 状态，是否启用，默认启用
    """
    name = 'zhuzhu_level_one'

    field = {
        'name': (str, ''),
        'img': (str, ''),
        'status': (bool, True),
    }


class LevelTwo(Model):
    """
    二级类目表
    pid : 所属一级类目id
    name:二级类目名称
    key:关键字
    img：图片
    status: 状态，是否启用，默认启用
    """
    name = 'zhuzhu_level_two'

    field = {
        'pid': (str, ''),
        'name': (str, ''),
        'key': (str, ''),
        'img': (str, ''),
        'status': (bool, True),
    }


class User(Model):
    """
    用户表
    tel ,用户登录的手机号
    nickname　昵称
    avatar 　头像
    passwd: 静态密码，目前没用上
    invite_code: 自己的邀请码
    use_invite_code: 注册时使用的邀请码
    vip:会员状态 0:非会员，1：会员
    channel:渠道状态，0：非渠道，1：预备渠道（任务未完成）2：渠道
    'relation_id': 渠道ID
    'special_id': 会员ID

    balance :账户可提现余额
    total_balance 总收益

    alipay 支付宝账号
    name   用户的姓名

    commission_rate 分成比率
    index:
    [tel, appid]
    [invite_code]
    [use_invite_code]
    """
    name = 'zhuzhu_user'

    field = {
        'tel': (int, None),
        'nickname': (str, None),
        'avatar': (str, None),
        'passwd': (str, None),
        'invite_code': (str, None),
        'use_invite_code': (str, None),
        'vip': (int, 0),
        'channel': (int, 0),
        'commission_rate': (str, None),
        'atime': (datetime, None),
        'invite_time': (datetime, None),
        'balance': (float, 0),
        'alipay': (str, None),
        'name': (str, None),
        'relation_id': (str, None),
        'special_id': (str, None),
        'total_balance': (float, 0),
        'channel_task': (dict, None),
        'favorite': (list, []),
    }


class UserCoupon(Model):
    """
    用户优惠券表


    index:
    [tel, appid]
    """
    name = 'zhuzhu_user_coupon'

    field = {
        'uid': (ObjectId, None),
        'category': (str, None),
        'category_name': (str, None),
        'click_url': (str, None),
        'commission_rate': (str, None),
        'coupon_amount': (str, None),
        'coupon_click_url': (str, None),
        'coupon_end_time': (int, None),
        'coupon_info': (str, None),
        'coupon_remain_count': (str, None),
        'coupon_share_url': (str, None),
        'coupon_start_fee': (str, None),
        'coupon_start_time': (int, None),
        'coupon_total_count': (str, None),
        'item_description': (str, None),
        'item_id': (str, None),
        'level_one_category_id': (int, None),
        'level_one_category_name': (str, None),
        'nick': (str, None),
        'pict_url': (str, None),
        'seller_id': (str, None),
        'shop_title': (str, None),
        'small_images': (dict, None),
        'title': (str, None),
        'user_type': (str, None),
        'volume': (str, None),
        'zk_final_price': (str, None),
        'estimated_earnings_user': (str, None),
    }


class UserToken(Model):
    """
    用户token表

    index:
    [token]
    """
    name = 'zhuzhu_usertoken'

    field = {
        'uid': (ObjectId, None),
        'token': (str, None),
    }


class TelCode(Model):
    """
    手机验证码

    index:
    [tel, code]
    """
    name = 'zhuzhu_telcode'

    field = {
        'tel': (int, None),
        'code': (str, None),
    }


class TbkOrder(Model):
    """
    淘宝客的订单，使用脚本定时拉取

    """
    name = "zhuzhu_tbk_order"
    field = {
        'tb_trade_parent_id': (int, None),  # 淘宝父订单号
        'tb_trade_id': (int, None),  # 淘宝订单号
        'num_iid': (int, None),  # 商品ID
        'item_title': (str, None),  # 商品标题
        'item_num': (int, None),  # 商品数量
        'price': (str, None),  # 单价
        'pay_price': (str, None),  # 实际支付金额
        'seller_nick': (str, None),  # 卖家昵称
        'seller_shop_title': (str, None),  # 卖家店铺名称
        'commission': (str, None),  # 推广者获得的收入金额，对应联盟后台报表“预估收入”
        'commission_rate': (str, None),  # 推广者获得的分成比率，对应联盟后台报表“分成比率”
        'create_time': (str, None),  # 淘客订单创建时间
        'earning_time': (str, None),  # 淘客订单结算时间
        'tk_status': (int, None),  # 淘客订单状态，3：订单结算，12：订单付款， 13：订单失效，14：订单成功
        'income_rate': (str, None),  # 收入比率，卖家设置佣金比率+平台补贴比率
        'pub_share_pre_fee': (str, None),  # 效果预估，付款金额*(佣金比率+补贴比率)*分成比率
        'auction_category': (str, None),  # 类目名称
        'alipay_total_price': (str, None),  # 付款金额
        'total_commission_rate': (str, None),  # 佣金比率
        'total_commission_fee': (str, None),  # 佣金金额
        'subsidy_rate': (str, None),  # 补贴比率
        'subsidy_type': (str, None),  # 补贴类型，天猫:1，聚划算:2，航旅:3，阿里云:4
        'subsidy_fee': (str, None),  # 补贴金额
        'relation_id': (str, None),  # 渠道关系ID
        'special_id': (str, None),  # 会员运营id
        'click_time': (str, None),  # 跟踪时间
    }


class UserBrokerage(Model):
    """
    用户佣金表
        'uid': 用户ID
        'msg': 说明
        'item_title': 商品标题
        'item_num': 购买数量
        'num_iid': 商品ID
        'status': 订单状态 create: 创建订单, complete: 订单完成, fail: 订单失败, pay: 佣金已支付
        'trade_id': 订单ID
        'trade_parent_id': 订单父ID
        'relation_id': 渠道ID
        'special_id': 会员ID
        'alipay_total_price': 实际支付金额
        'create_time': 订单创建时间
        'complete_time': 订单结算时间
        'cancel_time': 订单取消时间
        'pub_share_pre_fee': 获得佣金（已经去掉了我们应该拿走的部分）
        'commission_type' :佣金类型   shopping:会员购买, share:推广 , subordinate:下级返佣
        index:
        [uid, trade_id]
    """
    name = "zhuzhu_user_brokerage"

    field = {
        'uid': (ObjectId, None),
        'msg': (str, None),
        'item_title': (str, None),
        'item_num': (int, None),
        'num_iid': (str, None),
        'status': (str, None),
        'commission_type': (str, None),
        'trade_id': (str, None),
        'trade_parent_id': (str, None),
        'relation_id': (str, None),
        'special_id': (str, None),
        'alipay_total_price': (float, None),
        'create_time': (datetime, None),
        'complete_time': (datetime, None),
        'pub_share_pre_fee': (float, None),
    }


class CommissionRate(Model):
    """
    佣金配置 v:vip ,c:channel ,nc:not channel,p:parent上线
    user_v； 普通会员 %
    user_nc_v 非渠道会员返佣比例 %
    user_c 渠道会员返佣比例 %
    user_v_c_p 上线渠道会员返佣比例 %
    user_v_c_s 上线渠道会员 分享 返佣 %
    settlement_date 结算日期
    update_time 上次更新时间
    """
    name = "zhuzhu_commission_rate"

    field = {
        'user_v': (int, None),
        'user_nc_v': (int, None),
        'user_c': (int, None),
        'user_v_c_p': (int, None),
        'user_v_c_s': (int, None),
        'settlement_date': (int, None),
        'update_time': (datetime, None),
    }


class WithDrawLog(Model):
    """
    提现记录

    uid 用户id
    amount 体现金额
    alipay 支付宝账户
    name 用户的姓名
    atime 申请时间
    status 操作状态 1:成功，2：失败
    reason 失败原因
    """
    name = "zhuzhu_withdraw"

    field = {
        'uid': (ObjectId, None),
        'amount': (str, None),
        'order_id': (str, None),
        'pay_date': (str, None),
        'alipay': (str, None),
        'name': (str, None),
        'status': (int, None),
        'reason': (str, None),
        'result': (dict, {}),
        'atime': (datetime, None),
    }


class SettleLog(Model):
    """
        用户结算表
            'uid': 用户ID
            'trade_id': 订单ID
            'create_time': 订单创建时间
            'complete_time': 订单结算时间
            'cancel_time': 订单取消时间
            'pub_share_pre_fee': 获得佣金（已经去掉了我们应该拿走的部分）
            'commission_type' :佣金类型   shopping:会员购买, share:推广 , subordinate:下级返佣
            index:
            [uid, trade_id]
    """
    name = "zhuzhu_settle_log"

    field = {
        'uid': (ObjectId, None),
        'brokerage_id': (ObjectId, None),
        'commission_type': (str, None),
        'trade_id': (str, None),
        'create_time': (datetime, None),
        'complete_time': (datetime, None),
        'pub_share_pre_fee': (float, None),
        'atime': (datetime, None),
    }
