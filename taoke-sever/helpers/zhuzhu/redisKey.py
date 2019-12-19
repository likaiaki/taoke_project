def getTaskListRedisKey(appid):
    return 'tasklist_%s' % str(appid)


def getCompleteKey(appid, page, action):
    return 'completeKey_%s_%s_%s' % (appid, page, action)


def getCompleteTimeKey(appid, page, action):
    return 'completeTimeKey_%s_%s_%s_time' % (appid, page, action)


def getCompleteDailyKey(appid, page, action, need_num, uid):
    return 'completeDailyKey_%s_%s_%s_%s_%s' % (appid, page, action, need_num, uid)


def getCompleteTimeDailyKey(appid, page, action, time, uid):
    return 'completeTimeDailyKey_%s_%s_%s_%s_%s' % (appid, page, action, time, uid)


def getOneCompleteKey(appid, page, action, time, need_num, uid):
    return 'oneCompleteKey_%s_%s_%s_%s_%s_%s' % (appid, page, action, time, need_num, uid)


def getUserInfoKey(uid):
    return 'userInfo_%s' % (uid)


def getTaskInfoKey(id):
    return 'taskInfo_%s' % (id)


def getPriceInfoKey(id):
    return 'priceInfo_%s' % id


def getPriceListKey():
    return 'priceList'


def getAppInfoKey(uid):
    return 'appInfo_%s' % (uid)


def getAppTaskListKey(uid):
    return 'appTaskList_%s' % (uid)


def getAppTaskInfoKey(appid, page, action, time):
    return 'appTaskInfo_%s_%s_%s_%s' % (appid, page, action, time)