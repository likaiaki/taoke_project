from apps.app.setting import QINIU_HOST
from models.zhuzhu.model import *

tb_zone = Zone()
tb_level_one = LevelOne()
tb_level_two = LevelTwo()


def zone_list_and_size(spec):
    if not spec:
        spec = {}
    results = tb_zone.find(spec)
    count = tb_zone.count(spec)
    data = []
    for result in results:
        result['id'] = str(result.pop('_id'))
        img = result.get('img')
        if img:
            img = result['img'] if result['img'].startswith('http') else QINIU_HOST + '/' + result['img']
        result['img'] = img
        data.append(result)
    return data, count


def zone_insert(name, material_id, img, position, status):
    data = {
        'name': name,
        'material_id': material_id,
        'img': img,
        'position': position,
        'status': status,
    }
    tb_zone.insert_one(data)


def zone_delete(ids):
    tb_zone.delete_many({'_id': {"$in": [ObjectId(x) for x in ids]}})


def zone_update(id, name, material_id, img, position):
    data = {
        'name': name,
        'material_id': material_id,
        'img': img,
        'position': position,
    }
    data = {k: v for k, v in data.items() if v}
    result = tb_zone.update_one({'_id': ObjectId(id)}, {"$set": data}, upsert=True)
    print(result)


def level_one_delete(ids):
    tb_level_one.delete_many({'_id': {"$in": [ObjectId(x) for x in ids]}})


def level_one_list_and_size(spec):
    if not spec:
        spec = {}
    results = tb_level_one.find(spec)
    count = tb_level_one.count(spec)
    data = []
    for result in results:
        result['id'] = str(result.pop('_id'))
        result['img'] = result['img'] if result.get('img', '').startswith("http") else result['img']  # TODO 添加七牛前缀
        data.append(result)
    return data, count


def level_one_insert(name, key, img, status):
    data = {
        'name': name,
        'key': key,
        'img': img,
        'status': status,
    }
    tb_level_one.insert_one(data)


def level_one_update(id, name, key, img):
    data = {
        'name': name,
        'key': key,
        'img': img.replace('http......', '') if img.startswith('http') else img,  # TODO 去除七牛前缀
    }
    data = {k: v for k, v in data.items() if v}
    tb_level_one.update_one({'_id': ObjectId(id)}, {"$set": data})


def level_two_list_and_size(spec):
    if not spec:
        spec = {}
    results = tb_level_two.find(spec)
    reselts_one = tb_level_one.find(spec)
    id_name = {}
    for _ in reselts_one:
        id_name[str(_['_id'])] = _['name']
    count = tb_level_two.count(spec)
    data = []
    for result in results:
        result['id'] = str(result.pop('_id'))
        result['pid_name'] = id_name[str(result['pid'])]
        result['img'] = result['img'] if result.get('img', '').startswith("http") else result['img']  # TODO 添加七牛前缀
        data.append(result)
    return data, count


def level_two_insert(pid, name, key, img, status):
    data = {
        'pid': pid,
        'name': name,
        'key': key,
        'img': img,
        'status': status,
    }
    tb_level_two.insert_one(data)


def level_two_delete(ids):
    tb_level_two.delete_many({'_id': {"$in": [ObjectId(x) for x in ids]}})


def level_two_update(id, name, key, img):
    data = {
        'name': name,
        'key': key,
        'img': img.replace('http......', '') if img.startswith('http') else img,  # TODO 去除七牛前缀
    }
    data = {k: v for k, v in data.items() if v}
    tb_level_two.update_one({'_id': ObjectId(id)}, {"$set": data})


def get_category():
    results = tb_level_one.find().sort([('_id', 1)])
    data = []
    for result in results:
        temp = {'title': result['name'], 'list': []}
        level_twos = tb_level_two.find({'pid': str(result['_id'])})
        for level_two in level_twos:
            temp['list'].append({
                "img": level_two['img'],
                "title": level_two['name']
            })
        data.append(temp)
    return data
