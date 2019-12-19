import datetime

from bson import ObjectId

from models.zhuzhu import model

tb_commission_rate = model.CommissionRate()


def get_commission_rate():
    result = tb_commission_rate.find_one()
    if result:
        result['id'] = str(result.pop('_id'))
        result['update_time'] = str(result['update_time'])
        return result
    else:
        return {}


def update_commission_rate(id, data):
    if id:
        data['update_time'] = datetime.datetime.now()
        tb_commission_rate.update_one({'_id': ObjectId(id)}, {'$set': data})
    else:
        tb_commission_rate.insert_one(data)
