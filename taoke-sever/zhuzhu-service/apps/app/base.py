# -*- coding:utf-8 -*-

from . import setting
from apps import base


class BaseHandler(base.BaseHandler):
    _msg = None
    _count = None
    _code = 0

    def initialize(self):
        super(BaseHandler, self).initialize()
        self.template_path = setting.TEMPLATE_PATH

    @staticmethod
    def init_resp(code=0, msg=None):
        """
        responsibility for rest api code msg
        can override for other style

        :args code 0, rest api code
        :args msg None, rest api msg

        """
        resp = {
            'code': code,
            'msg': msg,
            'data': {},
        }
        return resp

    def wo_resp(self, resp):
        """
        can override for other style
        """
        if self._data is not None:
            resp['data'] = self.to_str(self._data)
        if self._msg is not None:
            resp['msg'] = self._msg
        if self._count is not None:
            resp['count'] = self._count
        if self._code != 0:
            resp['code'] = self._code
        return self.wo_json(resp)
