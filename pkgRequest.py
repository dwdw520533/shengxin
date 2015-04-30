# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'Kinslayer'
from utils import to_unicode
from xml.etree import ElementTree
import utils


class pkgRequest(object):
    kwargs = {}

    def __init__(self, signature, **kwargs):
        self.appsignature = signature
        self.kwargs = kwargs

    def check_appsignature(self):
        sign = utils.generate_sign(**self.kwargs)
        print sign
        print self.appsignature
        return sign == self.appsignature


def parse_user_msg(signature, xml):
    """
    Parse xml from wechat server and return an Message
    :param xml: raw xml from wechat server.
    :return: an Message object
    """
    if not xml:
        return

    _msg = dict((child.tag, to_unicode(child.text))
                for child in ElementTree.fromstring(xml))

    return pkgRequest(signature, **_msg)


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