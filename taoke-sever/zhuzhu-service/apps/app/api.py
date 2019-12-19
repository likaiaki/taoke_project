# -*- coding:utf-8 -*-
import datetime
import json

import turbo.log
from turbo.core.exceptions import ResponseMsg

from helpers.zhuzhu import user, material, zone, tbk, brokerage
from models.zhuzhu import model
from .base import BaseHandler

logger = turbo.log.getLogger(__file__)

tb_level_one = model.LevelOne()
tb_level_two = model.LevelTwo()
tb_zone = model.Zone()


class HomeHandler(BaseHandler):

    def GET(self):
        token = self.get_argument('token', None)
        self._data = {
            'category': zone.get_category(),  # 分类
            'featured': material.get_featured(),  # 精选
            'recommend': material.get_recommend(token),  # 推荐列表 10个
        }


class CategoryHandler(BaseHandler):

    def GET(self):
        self._data = zone.get_category()


class ZoneListHandler(BaseHandler):

    def GET(self):
        id = self.get_argument('id')
        token = self.get_argument('token', None)
        skip = int(self.get_argument('skip', 0))
        limit = int(self.get_argument('limit', 20))
        self._data = material.get_material_list(id, skip, limit, token)


class LoginHandler(BaseHandler):

    def GET(self):
        self.POST()

    def POST(self):
        tel = self.get_argument('tel', '')
        code = self.get_argument('code', '')
        passwd = self.get_argument('passwd', '')
        token, vip = user.login(tel, code if passwd == '' else passwd, 'code' if passwd == '' else 'passwd')
        url = 'https://oauth.m.taobao.com/authorize?response_type=code&client_id=25330814&redirect_uri={}&view=wap&state={}'.format(
            'http://taobaosavemoney.adesk.com/auth_callback', token + '_vip')
        print(url)
        self._msg = "ok"
        self._data = {
            'token': token,
            'vip': vip,
            'url': url if not vip else ''
        }


class SMSCodeHandler(BaseHandler):

    def GET(self):
        self.POST()

    def POST(self):
        tel = self.get_argument('tel', '')
        user.sendTelCode(tel)
        self._msg = "ok"


class AuthCallBackHandler(BaseHandler):
    def get(self):
        code = self.get_argument('code')
        state = self.get_argument('state')
        token, type = state.split('_')

        status, result = user.auth_callback(token, code, type)
        if status:
            if type == "vip":
                self.render('vip_success.html')
            elif type == "channel":
                self.render('channel_success.html')
        else:
            self.write(result)


class UserVipHandler(BaseHandler):

    def POST(self):
        token = self.get_argument('token', None)
        avatar = self.get_argument('avatar', None)
        nickname = self.get_argument('nickname', None)
        access_token = self.get_argument('access_token', None)
        code = self.get_argument('code', None)
        print(code, access_token)
        status, result = tbk.user_register('vip', access_token)
        special_id = result['special_id']
        data = {
            'nickname': nickname,
            'avatar': avatar,
            'special_id': special_id,
        }
        user.updateUserInfo(token, data)


class UserChannelHandler(BaseHandler):

    def POST(self):
        token = self.get_argument('token', '')
        url = 'https://oauth.m.taobao.com/authorize?response_type=code&client_id=25330814&redirect_uri={}&view=wap&state={}'.format(
            'http://taobaosavemoney.adesk.com/auth_callback', token + '_channel')
        u_info = user.getUserInfo(user.getUserId(token))
        channel = u_info.get('channel', 0)
        self._msg = "ok"
        self._data = {
            'channel': channel,
            'url': url if channel == 0 else ''
        }


class UserChannelStatusHandler(BaseHandler):

    def GET(self):
        token = self.get_argument('token', None)
        u_info = user.getUserInfo(user.getUserId(token))
        channel = u_info.get('channel', 0)
        channel_task = u_info.get('channel_task', {'finnal': 0, 'total': 3})
        data = {'channel': channel}
        if channel == 1:
            data.update(channel_task)
        self._data = data


class ProfileHandler(BaseHandler):
    """
    我的页面
    """

    def GET(self):
        # 本月预估收益，今日预估收益，昨日预估收益，昵称，头像
        token = self.get_argument('token', '')
        uid = user.getUserId(token)
        user_info = user.getUserInfo(uid)

        if user_info:
            user_info.pop('favorite')
            data = brokerage.detail(uid)
            user_info['channel_task'] = user_info['channel_task'] if user_info['channel_task'] else {}
            self._data = {
                'user': user_info,
            }
            self._data.update(data)
        else:
            raise ResponseMsg(-9, '登录已失效')


class WithdrawHandler(BaseHandler):
    """
    申请提现
    """

    def POST(self):
        token = self.get_argument('token', '')
        amount = self.get_argument('amount', '')
        version = self.get_argument('version', '1')  # 数字，
        version = int(version)
        if version == 1:  # 第一版不能提现
            self._code = -1
            self._msg = "账户余额不足!"
            return
            status, msg = user.request_withdraw(token, amount)
            if not status:
                self._code = -1
            self._msg = msg
        else:
            self._code = -1
            self._msg = '无效的App版本!'
            return


class UserCouponHandler(BaseHandler):
    """
    优惠券
    """

    def GET(self):
        token = self.get_argument('token', '')
        skip = int(self.get_argument('skip', 0))
        limit = int(self.get_argument('limit', 20))
        data = user.get_coupon_list(token, skip, limit)
        self._data = data

    def POST(self):  # TODO
        token = self.get_argument('token')
        data = self.get_argument('data', '{}')
        try:
            data = json.loads(data)
            print(data)
        except:
            raise ResponseMsg(-1, "无效的数据格式")
        user.add_coupon(token, data)

    def PUT(self):
        token = self.get_argument('token', '')
        item_ids = self.get_argument('item_ids', '')
        item_ids = item_ids.split(',')
        user.deleteCoupon(token, item_ids)


class UserFavoriteHandler(BaseHandler):
    """
    收藏、取消收藏
    """

    def GET(self):
        token = self.get_argument('token', '')
        skip = int(self.get_argument('skip', 1))
        limit = int(self.get_argument('limit', 20))
        if limit > 40:
            limit = 40
        data = user.getFavoriteList(token, skip, limit)
        self._msg = "ok"
        self._data = data

    def POST(self):
        token = self.get_argument('token', '')
        item_id = self.get_argument('item_id', '')  # 商品id
        user.addToFavorite(token, item_id)
        self._msg = "ok"

    def PUT(self):
        token = self.get_argument('token', '')
        item_ids = self.get_argument('item_ids', '')
        item_ids = item_ids.split(',')
        user.delete_favorite(token, item_ids)
        self._msg = "ok"


class UserUpdateHandler(BaseHandler):
    """
    更新用户信息，目前只有昵称
    """

    def POST(self):
        nickname = self.get_argument('nickname', None)
        token = self.get_argument('token')
        data = {
            'nickname': nickname
        }
        _data = {k: v for k, v in data.items() if v}
        user.updateUserInfo(token, _data)
        self._msg = "ok"


class UserInviteHandler(BaseHandler):

    def POST(self):
        token = self.get_argument('token')
        uid = user.getUserId(token)
        code = user.makeInviteCode()
        user.update({'_id': uid}, {'$set': {'invite_code': str(code)}})
        self._msg = 'ok'


class UserInvitedListHandler(BaseHandler):

    def GET(self):
        token = self.get_argument('token')
        skip = int(self.get_argument('skip', 0))
        limit = int(self.get_argument('limit', 20))
        self._data = user.getInvitedList(token, skip, limit)
        self._msg = 'ok'


class UserCodeHandler(BaseHandler):
    """
    设置上级的邀请码
    """

    def POST(self):
        token = self.get_argument('token', None)
        code = self.get_argument('code', None)
        user.setInviteCode(token, code)
        self._msg = "邀请码设置完成"


class SearchHandler(BaseHandler):
    """
    搜索
    """

    def POST(self):
        token = self.get_argument('token', None)
        skip = int(self.get_argument('skip', 0))
        limit = int(self.get_argument('limit', 20))
        sort = self.get_argument('sort', 'all')
        imei = self.get_argument('imei', None)
        key = self.get_argument('key')
        material_id = self.get_argument('material_id', None)
        ip = None
        data = tbk.search_list(skip, limit, key, material_id, ip, sort, imei, token)
        self._data = data
        self._msg = "ok"


class HotHandler(BaseHandler):

    def GET(self):
        token = self.get_argument('token', None)
        skip = int(self.get_argument('skip', 0))
        limit = int(self.get_argument('limit', 20))
        self._data = tbk.hot_coupon(skip, limit, token)


class UserBrokerageHandler(BaseHandler):

    def GET(self, type):
        self.route(type)

    def do_list(self):
        token = self.get_argument('token', '')
        skip = int(self.get_argument('skip', 0))
        limit = int(self.get_argument('limit', 20))
        self._data = brokerage.getList(user.getUserId(token), skip, limit)

    def do_detail(self):
        token = self.get_argument('token', '')
        uid = user.getUserId(token)
        self._data = brokerage.detail(uid)


class UserFavoriteStatusHandler(BaseHandler):

    def GET(self, item_id):
        token = self.get_argument('token', '')
        self._msg = "ok"
        self._data = {
            'favorite': user.is_favorite(token, item_id)
        }


class UserAlipayHandler(BaseHandler):
    def POST(self):
        token = self.get_argument('token', None)
        alipay = self.get_argument('alipay', None)
        name = self.get_argument('name', None)
        tel = self.get_argument('tel', None)
        code = self.get_argument('code', None)
        if user.checkTelCode(tel, code):
            data = {
                'alipay': alipay,
                'name': name,
            }
            user.updateUserInfo(token, data)
            self._msg = "ok"


class UserBindHandler(BaseHandler):

    def POST(self):
        token = self.get_argument('token', None)
        avatar = self.get_argument('avatar', '')
        nickname = self.get_argument('nickname', '')
        data = {
            'avatar': avatar,
            'nickname': nickname,
            'atime': datetime.datetime.now()
        }
        vip = user.bind(token, data)
        self._msg = "ok"
        self._data = {
            'vip': vip
        }


class WithdrawLogHandler(BaseHandler):

    def GET(self):
        token = self.get_argument('token', None)
        data = user.get_withdraw_log(token)
        self._msg = "ok"
        self._data = data


class TpwdHandler(BaseHandler):

    def GET(self):
        url = self.get_argument('url', None)
        text = self.get_argument('text', None)
        img = self.get_argument('img', None)

        if not url and not text:
            raise ResponseMsg(-1, "参数异常")
        if len(text) < 5:
            raise ResponseMsg(-1, "口令内容长度不得小于5个字符")
        status, result = tbk.tpwd_create(url, text, img)
        if status:
            self._data = {'model': result}
        else:
            self._code = -1
            self._msg = result
