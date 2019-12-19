#-*- coding:utf-8 -*-

import os


SCORE_ACTION = {
    # 每日登录
    'sign_in': {
        'rank': 10,
        'limit': 10,
        'desc':'每日登录送积分%d'
    },
    # 评论资源
    'comment_resource': {
        'rank': 1,
        'limit': 5,
        'desc':'评论资源送积分%d'
    },
    # 回复评论
    'reply_comment': {
        'rank': 1,
        'limit': 5,
        'desc':'回复评论送积分%d'
    },
    # 评论专区
    'comment_column':{
        'rank':1,
        'limit':5,
        'desc':'评论专区送积分%d'
    },
    # 点赞资源
    'up_resource': {
        'rank': 1,
        'limit': 5,
        'desc':'点赞资源送积分%d'
    },
    # 点赞评论
    'up_comment': {
        'rank': 1,
        'limit': 5,
        'desc':'点赞评论送积分%d'
    },
    # 点赞专区
    'up_column': {
        'rank': 1,
        'limit': 5,
        'desc':'点赞专区送积分%d'
    },
    # 收藏资源
    'favor_resource': {
        'rank': 1,
        'limit': 5,
        'desc':'收藏资源送积分%d'
    },
    # 关注专区
    'favor_column': {
        'rank': 1,
        'limit': 5,
        'desc':'关注专区送积分%d'
    },
    # 设置资源
    'set_resource': {
        'rank': 1,
        'limit': 5,
        'desc':'设置资源送积分%d'
    },
    # 分享资源
    'share_resource': {
        'rank': 1,
        'limit': 5,
        'desc':'分享资源送积分%d'
    },
    # 上传资源
    'upload_image':{
        'rank': 1,
        'limit': 5,
        'desc':'上传资源送积分%d'
    },
    # 兑吧消费
    'duiba_cost':{
        'rank': 0,
        'limit': 100,
        'desc':'兑吧消费积分%d'
    },
    'duiba_cashback':{
        'rank': 0,
        'limit': 100,
        'desc':'兑吧消费失败返还积分%d'
    }
}

QINIU_ORIGIN_HOST = 'http://7xopnn.com2.z0.glb.qiniucdn.com'
CDN_HOST = 'http://s.adesk.com'
if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '__test__')):
    BUCKET = 'test'
    STATIC_HOST = 'http://7xlipz.com2.z0.glb.qiniucdn.com'
    ES_SEARCH_CONFIG = {
        'server': ['localhost:9200'],
        'index': 'dandanjiang',
        'resource_table': 'resource',
        'album_table': 'album',
        'feed_table': 'feed'
    }
    CELERY = {
        'backend': 'redis://localhost:6379/1',
        'broker': 'redis://localhost:6379/1',
    }
    CACHE_MASTER_HOST = 'localhost'
    CACHE_SLAVE_HOST = ['localhost', 'localhost']
    DB = 1
else:
    BUCKET = 'dandan-jiang'
    STATIC_HOST = 'http://img7.dl.ltimg.net'
    STATIC_HOST_OSS = 'http://img7-oss.dl.ltimg.net'
    ES_SEARCH_CONFIG = {
        'server': ['jxqctf:9200', 'jxqctg:9200'],
        'index': 'dandanjiang',
        'resource_table': 'resource',
        'album_table': 'album',
        'feed_table': 'feed'
    }
    CELERY = {
        'backend': 'redis://jxqcta:6379/1',
        'broker': 'redis://jxqcta:6379/1',
    }
    CACHE_MASTER_HOST = 'cache01'
    CACHE_SLAVE_HOST = ['cache01', 'cache02']
    DB = 9


def _build_mapping(boost=1.0):
    return {
        'type': 'string',
        'store': 'yes',
        'index': 'analyzed',
        'analyzer': 'ik_max_word',
        'search_analyzer': 'ik_smart',
        'null_value': 'None',
        'boost': boost,
        'term_vector': "with_positions_offsets",
    }


ES_TABLE_PROPERTY = {
    '_id': {'type': 'string'},
    'tag': _build_mapping(),
    'desc': _build_mapping(),
    'name': _build_mapping(),
    'author': _build_mapping(),
    'category': _build_mapping(),
}


ES_ALBUM_TABLE_PROPERTY = {
    '_id': {'type': 'string'},
    'tag': _build_mapping(),
    'desc': _build_mapping(),
    'name': _build_mapping(),
    'author': _build_mapping(),
    'actor': _build_mapping(),
    'director': _build_mapping(),
    'role': _build_mapping(),
}


ES_FEED_TABLE_PROPERTY = {
    '_id': {'type': 'string'},
    'desc': _build_mapping(),
}

CLIENT_EXE_JS = {
    'www.acfun.tv':{
        'depend':'http://s.adesk.com/ddj/h5/acfun.html?url={{page_url}}',
        'js':'',
        'update_method':'client'
    },
    'www.bilibili.com':{
        'depend':'{{page_url}}',
        'js':'http://s.adesk.com/ddj/js/bili.js?version=1.1.5',
        'update_method':'client'
    },
    'www.iqiyi.com':{
        'depend':'{{page_url}}',
        'js':'http://s.adesk.com/ddj/js/iqiyi.js',
        'update_method':'client'
    },
    'www.youku.com':{
        'depend':'{{page_url}}',
        'js':'http://s.adesk.com/ddj/js/youku.js',
        'update_method':'client'
    }
}

def image_to_es_doc(doc):
    new_doc = {
        '_id': str(doc['_id']),
        'tag': ' '.join(doc['tag']),
        'category': '',
        'desc': doc['desc'],
        'during': 0,
        'cover': doc['cover'],
        'size': 0,
        'url': doc['url'],
        'type': 'image',
        'name': doc.get('name'),
    }

    return new_doc


def resource_to_es_doc(doc):
    return {
        '_id': str(doc['_id']),
        'tag': ' '.join(doc['tag']),
        'category': ' '.join(doc['category']),
        'desc': doc['desc'],
        'cover': doc['cover'],
        'url': doc['url'],
        'type': doc['type'],
    }


def video_to_es_doc(doc):
    return {
        '_id': str(doc['_id']),
        'tag': ' '.join(doc['tag']),
        'category': ' '.join(doc.get('category', [])) if doc.get('category') else '',
        'desc': doc['desc'],
        'during': doc['during'],
        'cover': doc['cover'],
        'size': doc['size'],
        'url': doc['url'],
        'type': 'video',
        'name': doc['name'],
    }


def ring_to_es_doc(doc):
    return {
        '_id': str(doc['_id']),
        'tag': ' '.join(doc['tag']),
        'category': ' '.join(doc.get('category', [])) if doc.get('category') else '',
        'desc': doc['desc'],
        'cover': doc['cover'],
        'during': doc['during'],
        'size': doc['size'],
        'url': doc['url'],
        'type': 'ring',
        'name': doc['name'],
    }


def album_to_es_doc(doc):
    return {
        '_id': str(doc['_id']),
        'tag': ' '.join(doc['tag']),
        'desc': doc['desc'],
        'name': doc['name'],
        'type': 'album',
        'cover': doc['cover'],
        'author': doc['author'],
        'director': doc['director'],
        'actor': ' '.join([one['aname'] for one in doc['role']]),
        'role': ' '.join([one['name'] for one in doc['role']]),
    }


def feed_to_es_doc(doc):
    return {
        '_id': str(doc['_id']),
        'desc': doc['desc'],
    }
