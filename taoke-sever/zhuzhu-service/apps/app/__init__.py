# -*- coding:utf-8 -*-
from turbo import register

from apps.app import god, api, app

register.register_group_urls('', [
    ('/test', api.AuthCallBackHandler),
    ('/auth_callback', api.AuthCallBackHandler),
])

register.register_group_urls('/v1', [
    ('/home', api.HomeHandler),  # 主页,token
    ('/search', api.SearchHandler),  # 搜索,token
    ('/category', api.CategoryHandler),  # 分类
    ('/hot', api.HotHandler),  # 爆款 ,token
    ('/zone/list', api.ZoneListHandler),  # 专区详情,token
    ('/login', api.LoginHandler),  # 登录
    ('/tpwd', api.TpwdHandler),  # 生成淘口令
    ('/sms_code', api.SMSCodeHandler),  # 获取短信验证码
    ('/user/code', api.UserCodeHandler),  # 帮赚钱
    ('/user/alipay', api.UserAlipayHandler),  # 设置提现支付宝账户
    ('/user/vip', api.UserVipHandler),  # 升级为会员
    ('/user/channel', api.UserChannelHandler),  # 升级为渠道
    ('/user/channel/status', api.UserChannelStatusHandler),  # 查询渠道任务状态
    ('/user/profile', api.ProfileHandler),  # 用户信息
    ('/user/update', api.UserUpdateHandler),  # 更新用户信息
    ('/user/invite', api.UserInviteHandler),  # 生成邀请码
    ('/user/invited/list', api.UserInvitedListHandler),  # 生成邀请码
    ('/user/bind', api.UserBindHandler),  # 用户绑定查询
    ('/user/withdraw', api.WithdrawHandler),  # 提现
    ('/user/withdraw/log', api.WithdrawLogHandler),  # 提现
    ('/user/coupon', api.UserCouponHandler),  # 优惠券
    ('/user/favorite', api.UserFavoriteHandler),  # 收藏
    ('/user/favorite/(.+)', api.UserFavoriteStatusHandler),  # 收藏状态
    ('/user/brokerage/(list|detail)', api.UserBrokerageHandler),  # 收益
])

register.register_group_urls('/god', [
    ('', god.HomeHandler),
    ('/token', god.TokenHandler),
    ('/zone', god.ZoneHandler),
    ('/level_one', god.LevelOneHandler),
    ('/level_two', god.LevelTwoHandler),
    ('/commission_rate', god.CommissionRateHandler),  # 佣金比例配置
    ('/invite', god.InviteHandler),  # 佣金比例配置
    ('/channel', god.ChannelHandler),  # 佣金比例配置
    ('/commission', god.CommissionHandler),  # 返佣统计
])
