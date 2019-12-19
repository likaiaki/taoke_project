# -*- coding:utf-8 -*-

import os
import sys

from tornado.util import ObjectDict

# server name
SERVER_NAME = 'zhuzhu-service'

# server dir
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
# project dir
PROJECT_DIR = os.path.dirname(SERVER_DIR)
sys.path.append(PROJECT_DIR)

# tornado web application settings
# details in
# http://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings
WEB_APPLICATION_SETTING = ObjectDict(
    static_path=os.path.join(SERVER_DIR, "static"),
    static_url_prefix='/static/',
    template_path=os.path.join(SERVER_DIR, "templates"),
    xsrf_cookies=False,
    cookie_secret="3%$334ma?asdf2987^%23&^%$2",
)

# turbo app setting
TURBO_APP_SETTING = ObjectDict(
    log=ObjectDict(
        log_path=os.path.join("/var/log/", SERVER_NAME + '.log'),
        log_size=500 * 1024 * 1024,
        log_count=3,
    ),
    session_config=ObjectDict({
        'name': 'session-id',
        'secret_key': 'o387xn4ma?adfasdfa83284&^%$2'
    }),
    template='default',
)

# check if app start in debug
if os.path.exists(os.path.join(SERVER_DIR, '__test__')):
    WEB_APPLICATION_SETTING['debug'] = True
    TURBO_APP_SETTING.log.log_path = os.path.join("", SERVER_NAME + '.log')
