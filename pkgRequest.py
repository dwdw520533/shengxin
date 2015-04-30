# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'Kinslayer'
from utils import to_unicode
from xml.etree import ElementTree
import utils
import settings


class pkgRequest(object):
    def __init__(self, **kwargs):
        if 'appid' in kwargs:
            self.appid = kwargs['appid']
        if 'openid' in kwargs:
            self.openid = kwargs['openid']
        if 'issubscribe' in kwargs:
            self.issubscribe = int(kwargs['issubscribe'])
        if 'productid' in kwargs:
            self.productid = kwargs['productid']
        if 'timestamp' in kwargs:
            self.timestamp = int(kwargs['timestamp'])
        if 'noncestr' in kwargs:
            self.noncestr = kwargs['noncestr']
        if 'appsignature' in kwargs:
            self.appsignature = kwargs['appsignature']
        if 'signmethod' in kwargs:
            self.signmethod = kwargs['signmethod']

    def check_appsignature(self):
        adict = dict(appid=self.appid,
                     appkey=settings.paySignKey,
                     productid=self.productid,
                     timestamp=self.timestamp,
                     noncestr=self.noncestr,
                     openid=self.openid,
                     issubscribe=self.issubscribe
        )
        sign = utils.generate_sign(**adict)
        print sign
        print self.appsignature
        return sign == self.appsignature


def parse_user_msg(xml):
    """
    Parse xml from wechat server and return an Message
    :param xml: raw xml from wechat server.
    :return: an Message object
    """
    if not xml:
        return

    _msg = dict((child.tag, to_unicode(child.text))
                for child in ElementTree.fromstring(xml))

    appid = _msg.get('AppId')
    openid = _msg.get('OpenId')
    issubscribe = _msg.get('IsSubscribe')
    productid = _msg.get('ProductId')
    timestamp = _msg.get('TimeStamp')
    noncestr = _msg.get('NonceStr')
    appsignature = _msg.get('AppSignature')
    signmethod = _msg.get('SignMethod')
    msg = dict(
        appid=appid,
        openid=openid,
        issubscribe=issubscribe,
        productid=productid,
        timestamp=timestamp,
        noncestr=noncestr,
        appsignature=appsignature,
        signmethod=signmethod)
    return pkgRequest(**msg)


reqxml = """<xml>
<AppId><![CDATA[wwwwb4f85f3a797777]]></AppId>
<OpenId><![CDATA[111222]]></OpenId>
<IsSubscribe>1</IsSubscribe>
<ProductId><![CDATA[777111666]]></ProductId>
<TimeStamp>1369743908</TimeStamp>
<NonceStr><![CDATA[YvMZOX28YQkoU1i4NdOnlXB1]]></NonceStr>
<AppSignature><![CDATA[e888481ae1fc104aa7c4bb15c5c403e2410b7aa1]]></AppSignature>
<SignMethod><![CDATA[sha1]]></SignMethod>
</xml>"""

if __name__ == "__main__":
    ret = parse_user_msg(reqxml)
    print ret.check_appsignature()