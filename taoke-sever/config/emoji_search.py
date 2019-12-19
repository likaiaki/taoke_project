# -*- coding: utf-8 -*-

import os
import pyes
from global_setting import STATIC_HOST

if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '__test__')):
    ES_SEARCH_CONFIG = {
        'server': ['jxqctf:9200', 'jxqcth:9200'],
        'index': 'dandanemoji',
        'resource_table': 'resource',
        'bag_table': 'bag'
    }
    CELERY = {
        'backend': 'redis://jxqctm:6379/2',
        'broker': 'redis://jxqctm:6379/1',
    }
    ASYNC = False
else:
    ES_SEARCH_CONFIG = {
        'server': ['jxqctf:9200', 'jxqcth:9200'],
        'index': 'dandanemoji',
        'resource_table': 'resource',
        'bag_table': 'bag'
    }
    CELERY = {
        'backend': 'redis://jxqctm:6379/2',
        'broker': 'redis://jxqctm:6379/1',
    }
    ASYNC = False


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


ES_RESOURCE_TABLE_PROPERTY = {
    '_id': {'type': 'string'},
    'tag': _build_mapping(),
    'desc': _build_mapping(),
    'name': _build_mapping(),
}


ES_BAG_TABLE_PROPERTY = {
    '_id': {'type': 'string'},
    'desc': _build_mapping(),
    'name': _build_mapping(),
}


def resource_to_es_doc(doc):
    return {
        '_id': str(doc['_id']),
        'src': doc['src'],
        'format': doc['format'],
        'url': '%s/%s' % (STATIC_HOST, doc['url']),
        'small_url': '%s/%s?imageView2/1/w/300/h/300' % (STATIC_HOST, doc['url']),
        'big_url': '%s/%s?imageView2/1/w/600/h/600' % (STATIC_HOST, doc['url']),
        'static_url': '%s/%s?imageMogr/v2/format/jpg' % (STATIC_HOST, doc['url']),
        'height': doc['height'],
        'width': doc['width'],
        'groupchat': doc['groupchat'],
        'atime': doc['atime'],
        'status': doc.get('status', ''),
        'name': doc.get('name', ''),
        'desc': doc.get('desc', ''),
        'tag': doc.get('tag', '')
    }


def bag_to_es_doc(doc):
    return {
        '_id': str(doc['_id']),
        'name': doc['name'],
        'desc': doc['desc'],
        'cover': '%s/%s?imageView2/1/w/300/h/300' % (STATIC_HOST, doc['cover']),
        'static_cover': '%s/%s?imageMogr/v2/format/jpg' % (STATIC_HOST, doc['cover']),
        'cover_height': doc['cover_height'],
        'cover_width': doc['cover_width'],
        'atime': doc['atime'],
    }

