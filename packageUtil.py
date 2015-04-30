# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'Kinslayer'

import hashlib
import settings
import urllib
import inspect


major_params = {
    'bank_type',
    'body',
    'attach',
    'partner',
    'out_trade_no',
    'total_fee',
    'fee_type',
    'notify_url',
    'spbill_create_ip',
    'time_start',
    'time_expire',
    'transport_fee',
    'product_fee',
    'goods_tag',
    'input_charset',
}




def props(obj, *exludes):
    pr = {}
    for name in dir(obj):
        if name in exludes:
            continue
        value = getattr(obj, name)
        if not name.startswith('_') and not inspect.ismethod(value):
            pr[name] = value
    return pr


def _gen_package_sign(pkg):
    items = props(pkg, 'metadata').items()
    items.sort()
    string1 = u''
    for k, v in items:
        if v is None or k not in major_params:
            continue
        if string1:
            string1 += u'&'
        string1 += u"%s=%s" % (k, v)
        #string1 += u"&key=%s" % wepaysettings.partnerKey
    string1 += u"&key=%s" % settings.partnerKey
    string2 = string1.encode('gb2312')
    return hashlib.md5(string2).hexdigest().upper()


def pkg_to_string(pkg):
    adict = dict()
    items = props(pkg, 'metadata').items()
    items.sort()
    for k, v in items:
        if v is not None and k in major_params:
            adict[k] = v.encode('gb2312') if isinstance(v, unicode) else v

    string1 = url_encode(sorted(adict.iteritems(), key=lambda d: d[0]))
    return string1 + "&sign=%s" % _gen_package_sign(pkg)





#url encode to lower case
def url_encode(d):
    pairs = list()
    if isinstance(d, dict):
        for key, value in d.items():
            newvalue = urllib.unquote(value)
            if newvalue != value:
                newvalue = newvalue.lower()
            pairs.append("%s=%s" % (key, newvalue))
        return '&'.join(pairs)
    elif isinstance(d, list):
        for item in d:
            key = item[0]
            value = item[1]
            newvalue = urllib.quote(str(value), '')
            if newvalue != value:
                newvalue = newvalue.lower()
            pairs.append("%s=%s" % (key, newvalue))
        return '&'.join(pairs)


    if __name__ == "__main__":
        pass