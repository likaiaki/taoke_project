# -*- coding:utf-8 -*-

# sub app setting
# try not to include function or class
import os

TEMPLATE_PATH = 'app/'

SECRET_KEY = 'kgIq_JZKLEm18s-NbUD4-wlyBJReid9FVmcximf1'
ACCESS_KEY = 'WFSZh7ihx3Xm-p7UkRBWUJDZj5JUwkygWRf4q_3X'

QINIU_BUCKET = 'novapps'
QINIU_HOST = 'http://novapps.qiniucdn.dandanjiang.tv'

if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '__test__')):
    QINIU_BUCKET = 'test'
    QINIU_HOST = 'http://7xlipz.com1.z0.glb.clouddn.com'
