# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'Kinslayer'

import settings
import random
import re
import time
import inspect
import hashlib
from datetime import datetime


def test():
    params = {
        #'sign': "XXXXX",
        'appid': settings.appId,
        'productid': '123456',
        'timestamp': '189026618', # str(time.time()),
        'noncestr': 'adssdasssd13d'
    }
    print create_url(**params)


def generate_sign(**kwargs):
    adict = kwargs.copy()
    items = adict.items()
    items.sort()
    string1 = ''
    for k, v in items:
        if string1:
            string1 += '&'
        string1 += "%s=%s" % (k.lower(), v)

    #print string1
    return hashlib.sha1(to_unicode(string1)).hexdigest()


def create_url(**kwargs):
    baseurl = "weixin://wxpay/bizpayurl"
    is_firstparam = True
    adict = kwargs.copy()
    items = adict.items()
    items.sort()
    for k, v in items:
        if is_firstparam:
            baseurl += "?%s=%s" % (k, v)
            is_firstparam = False
        else:
            baseurl += "&%s=%s" % (k, v)

    adict['appkey'] = settings.paySignKey
    sign = generate_sign(**adict)
    baseurl += "&sign=%s" % sign
    return baseurl


def generate_token(length=''):
    if not length:
        length = random.randint(3, 32)
    length = int(length)
    assert 3 <= length <= 32
    token = []
    letters = 'abcdefghijklmnopqrstuvwxyz' \
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '0123456789'
    for _ in range(length):
        token.append(random.choice(letters))
    return ''.join(token)


def check_token(token):
    return re.match('^[A-Za-z0-9]{3,32}$', token)


def to_unicode(value):
    if isinstance(value, unicode):
        return value
    if isinstance(value, basestring):
        return value.decode('utf-8')
    if isinstance(value, int):
        return str(value)
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return value


def to_utf8(value, coding='GB2312'):
    if isinstance(value, unicode):
        return value.encode('utf-8')
    if isinstance(value, basestring):
        return value.decode(coding).encode('utf-8')


def isstring(value):
    return isinstance(value, basestring)


def generate_token(length=''):
    if not length:
        length = random.randint(3, 32)
    length = int(length)
    assert 3 <= length <= 32
    token = []
    letters = 'abcdefghijklmnopqrstuvwxyz' \
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '0123456789'
    for _ in range(length):
        token.append(random.choice(letters))
    return ''.join(token)


def noncestr(length=20):
    length = int(length)
    token = []
    letters = 'abcdefghijklmnopqrstuvwxyz' \
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '0123456789'
    for _ in range(length):
        token.append(random.choice(letters))
    return ''.join(token)


def timestamp():
    return int(time.time())


def wxtime():
    """
    返回微信格式的时间
    """
    return datetime.now().strftime('%Y%m%d%H%M%S')


def generate_password(length=6):
    pwd = []
    letters = '1234567890'
    for index in range(length):
        pwd.append(random.choice(letters))
    return ''.join(pwd)


def props_ignore_null(obj, *exludes):
    pr = {}
    for name, value in obj.__dict__.items():
        if name in exludes or name.startswith('_') or value is None:
            continue
        pr[name] = value
    return pr


def props(obj, *exludes):
    pr = {}
    for name, value in obj.__dict__.items():
        if name in exludes or name.startswith('_'):
            continue
        pr[name] = value
    return pr


def dict_to_obj(adict, objtype):
    obj = objtype()
    for a, b in adict.items():
        assert not isinstance(b, dict)
        obj.__setattr__(a, b)
    return obj


if __name__ == "__main__":
    _params = {
        "appId": "wxf8b4f85f3a794e77",
        "timeStamp": "189026618",
        "nonceStr": "adssdasssd13d",
        "package": "bank_type=WX&body=XXX&fee_type=1&input_charset=GBK&notify_url=http%3a%2f%2fwww.qq.com&out_trade_no=16642817866003386000&partner=1900000109&spbill_create_ip=127.0.0.1&total_fee=1&sign=BEEF37AD19575D92E191C1E4B1474CA9",
        "appKey": "2Wozy2aksie1puXUBpWD8oZxiD1DfQuEaiC7KcRATv1Ino3mdopKaPGQQ7TtkNySuAmCaDCrw4xhPY5qKTBl7Fzm0RgR3c0WaVYIXZARsxzHV2x7iwPPzOz94dnwPWSn"

    }
    _sign = generate_sign(**_params)

    str1 = """appid=wxf8b4f85f3a794e77&appkey=2Wozy2aksie1puXUBpWD8oZxiD1DfQuEaiC7KcRATv1Ino3mdopKaPGQQ7TtkNySuAmCaDCrw4xhPY5qKTBl7Fzm0RgR3c0WaVYIXZARsxzHV2x7iwPPzOz94dnwPWSn&noncestr=adssdasssd13d&package=bank_type=WX&body=XXX&fee_type=1&input_charset=GBK&notify_url=http%3a%2f%2fwww.qq.com&out_trade_no=16642817866003386000&partner=1900000109&spbill_create_ip=127.0.0.1&total_fee=1&sign=BEEF37AD19575D92E191C1E4B1474CA9&timestamp=189026618"""

    import hashlib

    print hashlib.sha1(str1).hexdigest() == _sign
    test()

def force_utf8(data):
    '''
    数据转换为utf8
    @data: 待转换的数据
    @return: utf8编码
    '''
    if isinstance(data, unicode):
        return data.encode('utf-8')
    elif isinstance(data, list):
        return [force_utf8(i) for i in data]
    elif isinstance(data, dict):
        return {force_utf8(i):force_utf8(data[i]) for i in data}
    return data