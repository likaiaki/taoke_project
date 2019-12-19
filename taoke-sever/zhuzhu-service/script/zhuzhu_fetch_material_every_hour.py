import datetime
import json

import realpath
import top

# 默认抓取的物料id
from helpers.zhuzhu.Redis import r
from models.zhuzhu import model
from top.api.base import TopException

tb_zone = model.Zone()
# 淘宝客api配置文件
domain = "eco.taobao.com"
port = 443
appkey = "25330814"
secret = "ab31504958f529b9c1b78a50b2e4fec5"

adzone_id = 108893800063  # 渠道&会员

zones = tb_zone.find()


def get_material(material_id, page_no=1):
    req = top.api.TbkDgOptimusMaterialRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    req.adzone_id = adzone_id
    req.material_id = material_id
    req.page_size = 20
    req.page_no = page_no
    try:
        resp = req.getResponse()
        return resp
    except TopException as e:
        print(material_id, e)
        return None


def main():
    for zone in zones:
        _id = str(zone['_id'])
        index = 0
        if r.llen('zhuzhu_' + _id + '_list') < 1000:
            r.lpush('zhuzhu_' + _id + '_list', *['' for x in range(1000)])
        for page in range(50):
            result = get_material(zone['material_id'], page + 1)
            if not result:
                break
            items = result['tbk_dg_optimus_material_response']['result_list']['map_data']
            print(_id, page, len(items))
            for i, item in enumerate(items):
                r.lset('zhuzhu_' + _id + '_list', index, json.dumps(item))
                index += 1
        llen = r.llen('zhuzhu_' + _id + '_list')
        items = r.lrange('zhuzhu_' + _id + '_list', 0, -1)
        count = len([x for x in items if x])
        print('专区名称：', zone['name'] + '\t', '总长度：', str(llen) + ' ' * (8 - len(str(llen))), '有效数据：', str(count) + '\t')
        tb_zone.update_one({'_id': zone['_id']}, {'$set': {'count': count}})


if __name__ == '__main__':
    main()
    print(datetime.datetime.now())
