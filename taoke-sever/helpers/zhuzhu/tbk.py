# coding=utf-8
import hashlib
import json
import re

import top
# 淘宝客api配置文件
from helpers.zhuzhu.util import item_list_format
from top.api.base import TopException

domain = "eco.taobao.com"
port = 443
appkey = "25330814"
secret = "ab31504958f529b9c1b78a50b2e4fec5"
sessionkey = "610261054d2ff0cc5c142cdc757cd5604ab9be30fab92084002112494"

adzone_id = 108893800063


def user_register(type, sessionkey):
    req = top.api.TbkScPublisherInfoSaveRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    # code type:1 => ZYQF29 渠道邀请
    # code type:3 => VRDQZ7 会员邀请

    req.inviter_code = "ZYQF29" if type == 'channel' else 'VRDQZ7'
    req.info_type = 1
    try:
        resp = req.getResponse(sessionkey)
        return True, resp['tbk_sc_publisher_info_save_response']['data']
    except TopException as e:
        print(e)
        return False, e.submsg


def hot_coupon(skip, limit, token=None):
    req = top.api.TbkDgItemCouponGetRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    req.adzone_id = adzone_id
    req.page_no = int(skip // limit) + 1
    req.page_size = limit
    try:
        resp = req.getResponse()
        data = []
        for result in resp['tbk_dg_item_coupon_get_response']['results']['tbk_coupon']:
            nums = re.findall('[0-9\.]{1,}', result['coupon_info'])
            if len(nums) == 2:
                result['coupon_start_fee'] = int(nums[0])
                result['coupon_amount'] = int(nums[1])
            elif len(nums) == 1:
                result['coupon_start_fee'] = 0
                result['coupon_amount'] = int(nums[0])
            else:
                result['coupon_start_fee'] = 0
                result['coupon_amount'] = 0
            data.append(result)
        return item_list_format(data, token)
    except TopException as e:
        print(e)
        return []


def item_query(iids, token=None):
    req = top.api.TbkItemInfoGetRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    req.num_iids = ','.join(iids)
    req.platform = 1
    # req.ip = "47.75.61.229"
    try:
        resp = req.getResponse()
        return item_list_format(resp['tbk_item_info_get_response']['results']['n_tbk_item'], token)
    except TopException as e:
        print(e)
        return []


def search_list(skip, limit, key, material_id=None, ip=None, sort='', imei=None, token=None):
    req = top.api.TbkDgMaterialOptionalRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    if sort == 'all':  # 综合搜索
        req.start_dsr = 10  # 商品筛选(特定媒体支持)-店铺dsr评分。筛选大于等于当前设置的店铺dsr评分的商品0-50000之间
    page = int(skip // limit) + 1
    req.page_size = limit
    req.page_no = page
    req.platform = 1
    # req.end_tk_rate = 1234 #商品筛选-淘客佣金比率上限。如：1234表示12.34%
    # req.start_tk_rate = 1234 #商品筛选-淘客佣金比率下限。如：1234表示12.34%
    # req.end_price = 10 #商品筛选-折扣价范围上限。单位：元
    # req.start_price = 10 #商品筛选-折扣价范围下限。单位：元
    req.is_overseas = 'false'  # 商品筛选-是否海外商品。true表示属于海外商品，false或不设置表示不限
    req.is_tmall = 'false'  # 商品筛选-是否天猫商品。true表示属于天猫商品，false或不设置表示不限
    if sort != 'all':
        req.sort = sort  # 排序_des（降序），排序_asc（升序），销量（total_sales），淘客佣金比率（tk_rate）， 累计推广量（tk_total_sales），总支出佣金（tk_total_commi），价格（price）
    # req.itemloc = "杭州"  # 商品筛选-所在地
    # req.cat = "16,18"
    req.q = key  # 查询的关键词
    if material_id:
        req.material_id = material_id
    req.has_coupon = 'false'  # 优惠券筛选-是否有优惠券。true表示该商品有优惠券，false或不设置表示不限
    if ip:
        req.ip = ip
    req.adzone_id = adzone_id
    # req.need_free_shipment = 'true' # 包邮
    req.need_prepay = 'true'  # 商品筛选-是否加入消费者保障
    # req.include_pay_rate_30 = 'true'
    # req.include_good_rate = 'true'
    # req.include_rfd_rate = 'true'
    # req.npx_level = 2
    # req.end_ka_tk_rate = 1234
    # req.start_ka_tk_rate = 1234
    if sort == 'all' and imei:
        req.device_encrypt = "MD5"
        req.device_value = hashlib.md5(imei.encode(encoding='UTF-8')).hexdigest()
        req.device_type = "IMEI"

    try:
        resp = req.getResponse()
        data = []
        for result in resp['tbk_dg_material_optional_response']['result_list']['map_data']:
            result['commission_rate'] = float(result['commission_rate']) / 100
            if not result.get('click_url'):
                result['click_url'] = result['url']
            data.append(result)
        return item_list_format(data, token)
    except TopException as e:
        print(e)
        return []


def query_order():
    req = top.api.TbkOrderGetRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    req.fields = "tb_trade_parent_id,tb_trade_id,num_iid,item_title,item_num,price,pay_price,seller_nick,seller_shop_title,commission,commission_rate,relation_id,special_id,click_time"
    req.span = 60

    req.page_no = 1
    req.page_size = 20
    req.tk_status = 1
    req.start_time = "2019-05-29 09:58:00"

    req.order_query_type = "create_time"
    req.order_scene = 2
    req.order_count_type = 1
    try:
        resp = req.getResponse()
        print(resp)
    except TopException as e:
        print(e)


def query_order_new():
    req = top.api.TbkOrderDetailsGetRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    req.query_type = 1  # 1：按照订单淘客创建时间查询，2:按照订单淘客付款时间查询，3:按照订单淘客结算时间查询
    # req.position_index = "2222_334666"
    req.page_size = 20
    req.member_type = 2  # 2:二方，3:三方，不传，表示所有角色
    req.tk_status = 12
    req.end_time = "2019-05-29 10:00:00"
    req.start_time = "2019-05-29 09:57:00"
    req.jump_type = 1
    req.page_no = 1
    req.order_scene = 1  # 1:常规订单，2:渠道订单，3:会员运营订单，默认为1
    try:
        resp = req.getResponse()
        data = json.dumps(resp).decode('unicode-escape')
        print(data)
        with open(__file__ + '.OrderDetailsGet.json', 'a+') as f:
            f.write(data.encode('utf-8'))
            f.write('\r\n')
    except TopException as e:
        print(e)


def tpwd_create(url, text, img=None):
    req = top.api.TbkTpwdCreateRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    req.text = text
    req.url = url
    if img:
        req.logo = img
    try:
        resp = req.getResponse()
        print(resp)
        return True, resp['tbk_tpwd_create_response']['data']['model']
    except TopException as e:
        print(e.submsg)
        return False, e.submsg


# ------------------------------
def PublisherInfoGet():
    req = top.api.TbkScPublisherInfoGetRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    # req.relation_id = 2138087509
    req.info_type = 1
    req.page_no = 1
    req.page_size = 99
    req.relation_app = "common"
    try:
        resp = req.getResponse(sessionkey)
        data = json.dumps(resp).decode('unicode-escape')
        print(data)
        with open(__file__ + '.PublisherInfoGet.json', 'a+') as f:
            f.write(data.encode('utf-8'))
            f.write('\r\n')
    except TopException as e:
        print(e)


def InvitecodeGet():
    req = top.api.TbkScInvitecodeGetRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    req.relation_id = 2138087509
    req.relation_app = "common"
    req.code_type = 1
    try:
        resp = req.getResponse(sessionkey)
        data = json.dumps(resp).decode('unicode-escape')
        print(data)
        with open(__file__ + '.InvitecodeGet.json', 'a+') as f:
            f.write(data.encode('utf-8'))
            f.write('\r\n')
    except TopException as e:
        print(e)


def OptimusMaterial():
    req = top.api.TbkDgOptimusMaterialRequest(domain, port)
    req.set_app_info(top.appinfo(appkey, secret))

    req.adzone_id = adzone_id
    req.material_id = 3761

    try:
        resp = req.getResponse()
        return resp
    except TopException as e:
        print(e)


if __name__ == '__main__':
    tpwd_create(
        'https://s.click.taobao.com/t?e=m=2&s=kw/IhWP420Bw4vFB6t2Z2ueEDrYVVa64Dne87AjQPk9yINtkUhsv0Hoo+YpJnEl868fTScoFPtyzOsnH7AQXz5GDZlmGS8CcVc/a3Rp+i7iIrQ22sLmz3gPpaC8bZFEBFBoMXOGuG5DkaqczTKGnOpvhnsc6QdSo/Ue0eKE/TC+REjEiL0p2TupL9cJfNfu1K2bvhDe4JectUO4j5VppG8Yl7w3/A2kb&scm=1007.19011.107455.0_4094&pvid=41b1800d-76da-457a-898b-93fa0186873e&app_pvid=59590_11.23.92.101_1644_1560762042020&ptl=floorId:4094;pvid:41b1800d-76da-457a-898b-93fa0186873e;app_pvid:59590_11.23.92.101_1644_1560762042020&union_lens=lensId:0b175c65_0cc3_16b64aac71b_17d3',
        '长度大于5个字长度大于5个字符')
