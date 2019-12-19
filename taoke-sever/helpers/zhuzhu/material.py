from apps.app.setting import QINIU_HOST
from helpers.zhuzhu.Redis import r
from helpers.zhuzhu.util import item_list_format
from models.zhuzhu import model

tb_zone = model.Zone()
tb_commission_rate = model.CommissionRate()


def get_featured():
    results = tb_zone.find({'position': {"$ne": '1'}})
    data = []
    for result in results:
        img = result.get('img')
        if img:
            img = result['img'] if result['img'].startswith('http') else QINIU_HOST + '/' + result['img']
        result['img'] = img
        data.append({
            'name': result['name'],
            'id': str(result['_id']),
            'material_id': result['material_id'],
            'img': img,
        })
    return data


def get_recommend(token=None):
    results = tb_zone.find({'position': {"$ne": '0'}})
    data = []
    for result in results:
        temp = {'name': result['name'], 'id': str(result['_id']), 'material_id': result['material_id'], 'items': []}
        key = 'zhuzhu_' + str(result['_id']) + '_list'
        temp['items'] = item_list_format(r.lrange(key, 0, 9), token, True)
        data.append(temp)

    return data


def get_material_list(id, skip, limit, token=None):
    key = 'zhuzhu_' + id + '_list'
    return item_list_format(r.lrange(key, skip, skip + limit - 1), token, True)


if __name__ == '__main__':
    print(get_recommend())
    print(get_featured())
