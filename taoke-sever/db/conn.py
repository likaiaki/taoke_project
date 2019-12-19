# -*- coding:utf-8 -*-

import os

from pymongo import (
    MongoClient,
    read_preferences
)

import db.setting as setting

if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '__test__')):
    mc = MongoClient(host='127.0.0.1')
else:
    mc = MongoClient(','.join(setting.ADESK01_HOSTS), replicaSet=setting.ADESK01,
        socketTimeoutMS=30000, connectTimeoutMS=10000, 
        read_preference=read_preferences.ReadPreference.SECONDARY_PREFERRED)
