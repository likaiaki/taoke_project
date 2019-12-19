# -*- coding:utf-8 -*-
import qiniu
import turbo.log
from bson import ObjectId

from apps.app.setting import ACCESS_KEY, SECRET_KEY, QINIU_BUCKET
from helpers.zhuzhu import zone, commission, user, brokerage
from .base import BaseHandler

logger = turbo.log.getLogger(__file__)


def qiniu_token(key):
    try:
        q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
        token = q.upload_token(QINIU_BUCKET, key)
    except:
        return None
    return token


class HomeHandler(BaseHandler):

    def get(self):
        self.render('index.html')


class ZoneHandler(BaseHandler):

    def get(self):
        data, count = zone.zone_list_and_size({'status': {"$ne": 1}})
        self.write({'code': 0, 'msg': '', 'data': data, 'count': count})

    def post(self):
        name = self.get_argument('name')
        material_id = self.get_argument('material_id')
        img = self.get_argument('img')
        position = self.get_argument('position')
        zone.zone_insert(name, material_id, img, position, 0)
        self.write({'code': 0, 'msg': 'ok'})

    def delete(self):
        ids = self.get_argument('ids')
        ids = ids.split(',')
        zone.zone_delete(ids)
        self.write({'code': 0, 'msg': 'ok'})

    def put(self):
        id = self.get_argument('id')
        name = self.get_argument('name')
        material_id = self.get_argument('material_id')
        img = self.get_argument('img')
        position = self.get_argument('position')
        zone.zone_update(id, name, material_id, img, position)
        self.write({'code': 0, 'msg': 'ok'})


class LevelOneHandler(BaseHandler):
    def get(self):
        data, count = zone.level_one_list_and_size({'status': 0})
        self.write({'code': 0, 'msg': '', 'data': data, 'count': count})

    def post(self):
        name = self.get_argument('name')
        key = self.get_argument('key')
        img = self.get_argument('img')
        zone.level_one_insert(name, key, img, 0)
        self.write({'code': 0, 'msg': 'ok'})

    def delete(self):
        ids = self.get_argument('ids')
        ids = ids.split(',')
        zone.level_one_delete(ids)
        self.write({'code': 0, 'msg': 'ok'})

    def put(self):
        id = self.get_argument('id')
        name = self.get_argument('name')
        key = self.get_argument('key')
        img = self.get_argument('img')
        zone.level_one_update(id, name, key, img)
        self.write({'code': 0, 'msg': 'ok'})


class LevelTwoHandler(BaseHandler):
    def get(self):
        data, count = zone.level_two_list_and_size({'status': 0})
        self.write({'code': 0, 'msg': '', 'data': data, 'count': count})

    def post(self):
        pid = self.get_argument('pid')
        name = self.get_argument('name')
        key = self.get_argument('key')
        img = self.get_argument('img')
        zone.level_two_insert(pid, name, key, img, 0)
        self.write({'code': 0, 'msg': 'ok'})

    def delete(self):
        ids = self.get_argument('ids')
        ids = ids.split(',')
        zone.level_two_delete(ids)
        self.write({'code': 0, 'msg': 'ok'})

    def put(self):
        id = self.get_argument('id')
        name = self.get_argument('name')
        key = self.get_argument('key')
        img = self.get_argument('img')
        zone.level_two_update(id, name, key, img)
        self.write({'code': 0, 'msg': 'ok'})


class CommissionRateHandler(BaseHandler):
    def get(self):
        data = commission.get_commission_rate()
        self.write({'code': 0, 'msg': '', 'data': data})

    def post(self):
        id = self.get_argument('id', '')
        user_v = self.get_argument('user_v')
        user_nc_v = self.get_argument('user_nc_v')
        user_c = self.get_argument('user_c')
        user_v_c_p = self.get_argument('user_v_c_p')
        user_v_c_s = self.get_argument('user_v_c_s')
        settlement_date = self.get_argument('settlement_date')

        data = {
            'user_v': user_v,
            'user_nc_v': user_nc_v,
            'user_c': user_c,
            'user_v_c_p': user_v_c_p,
            'user_v_c_s': user_v_c_s,
            'settlement_date': settlement_date,
        }
        commission.update_commission_rate(id, data)
        self.write({'code': 0, 'msg': 'ok'})


class InviteHandler(BaseHandler):
    def GET(self):
        page = int(self.get_argument('page', 1))
        limit = int(self.get_argument('limit', 20))
        skip = (page - 1) * limit
        start = self.get_argument('start', None)  # 时间戳
        stop = self.get_argument('stop', None)  # 时间戳
        code = self.get_argument('code', None)
        tel = self.get_argument('tel', None)
        name = self.get_argument('name', None)
        data, count = user.getInviteStatus(skip, limit, start, stop, tel, name, code)
        self._msg = "ok"
        self._count = count
        self._data = data


class ChannelHandler(BaseHandler):

    def GET(self):
        page = int(self.get_argument('page', 1))
        limit = int(self.get_argument('limit', 20))
        skip = (page - 1) * limit
        start = self.get_argument('start', None)  # 时间戳
        stop = self.get_argument('stop', None)  # 时间戳
        status = self.get_argument('status', None)
        tel = self.get_argument('tel', None)
        name = self.get_argument('name', None)
        data, count = user.getAllChannel(skip, limit, start, stop, status, tel, name)
        self._msg = "ok"
        self._count = count
        self._data = data


class CommissionHandler(BaseHandler):

    def GET(self):
        page = int(self.get_argument('page', 1))
        limit = int(self.get_argument('limit', 20))
        skip = (page - 1) * limit
        create_start = self.get_argument('create_start', None)  # 时间戳
        create_stop = self.get_argument('create_stop', None)  # 时间戳
        complete_start = self.get_argument('complete_start', None)  # 时间戳
        complete_stop = self.get_argument('complete_stop', None)  # 时间戳
        commission_type = self.get_argument('commission_type', None)  # 佣金类型
        status = self.get_argument('status', None)  # 订单状态
        tel = self.get_argument('tel', None)
        name = self.get_argument('name', None)
        data, count = brokerage.get_brokerage_and_count(skip, limit, create_start, create_stop, complete_start,
                                                        complete_stop, commission_type, status, name, tel)
        self._msg = "ok"
        self._count = count
        self._data = data


class TokenHandler(BaseHandler):
    def GET(self):
        _id = self.get_argument('id', None)
        type = self.get_argument('type', 'zone')
        token = ''
        if not _id:
            _id = str(ObjectId())
        key = "zhuzhu/zone/" + _id
        if type == 'zone':
            token = qiniu_token(key)
        self._data = {'token': token, 'key': key, 'id': _id}
