# -*- coding:utf-8 -*-

import redis
import datetime
from config.global_setting import CACHE_MASTER_HOST, CACHE_SLAVE_HOST, DB
pool_size = 4
redis_port = 6379
redis_pool_master = redis.ConnectionPool(host=CACHE_MASTER_HOST, port=redis_port, db=DB, max_connections=pool_size)
r = redis.StrictRedis(connection_pool=redis_pool_master)


def setRedisValue(key, value, time):
    r.set(key, str(value))
    if isinstance(time, datetime.datetime):
        r.expireat(key, time)
    else:
        r.expire(key, time)


def getRedisValue(key):
    value = r.get(key)
    if value:
        try:
            return value.decode()
        except:
            return value
    return None


def deleteRedisValue(key):
    r.delete(key)