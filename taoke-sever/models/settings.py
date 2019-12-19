# -*- coding:utf-8 -*-

from db.conn import mc

# mc = mongo_client
MONGO_DB_MAPPING = {
    'db': {
        'gif_server': mc['gif_server'],
        'ios_wallpaper': mc['ios_wallpaper'],
        'advanced_wallpaper': mc['advanced_wallpaper'],
        'novapps_server': mc['novapps_server'],
        'adesk_ad': mc['adesk_ad'],
        'vip_server': mc['vip_server'],
        'daka_server': mc['daka_server'],
        'dandan_emoji': mc['dandan_emoji'],
        'zhuzhu_service': mc['zhuzhu_service'],
        'god_log': mc['god_log'],
    },
    'db_file': {
    }
}
