# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'Kinslayer'

import logging
import traceback

import web
import hashlib
import pkgRequest
import pkgReply
from settings import token


class Method:
    def __init__(self):
        pass

    def GET(self):
        # 获取输入参数
        data = web.input()
        signature = data.signature
        timestamp = data.timestamp
        nonce = data.nonce
        echostr = data.echostr
        # 字典序排序
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
        # sha1加密算法

        # 如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr

    def POST(self):
        try:
            reqbody = web.data()
            logging.info(reqbody)
            message = pkgRequest.parse_user_msg(reqbody)
            if not message.check_appsignature():
                return web.HTTPError('403', 'check_signature failed!')

            logging.info(u"request = %s" % reqbody)
            reply = pkgReply.get_reply(message)
            logging.info(u"reply = %s" % reply)
        except Exception, e:
            errmsg = traceback.format_exc()
            logging.error(errmsg)
            reply = None

        web.header('Content-Type', 'text/html; charset=utf-8')
        return reply if reply else ''


def test():
    reqbody = """<xml><OpenId><![CDATA[oY7uijoODBWpXuaaR-7N4jEPxGfQ]]></OpenId>
<AppId><![CDATA[wx80a445e58ff37347]]></AppId>
<IsSubscribe>1</IsSubscribe>
<ProductId><![CDATA[20131224185347968576]]></ProductId>
<TimeStamp>1387882457</TimeStamp>
<NonceStr><![CDATA[yLEV0CKY4AQN6J9x]]></NonceStr>
<AppSignature><![CDATA[94088ae0b63ad1a08885d1263e580cb8b5f2f753]]></AppSignature>
<SignMethod><![CDATA[sha1]]></SignMethod>
</xml>"""
    message = pkgRequest.parse_user_msg(reqbody)
    if not message.check_appsignature():
        print 'check signature failed'
        return web.HTTPError('403', 'check_signature failed!')

    reply = pkgReply.get_reply(message)
    print reply

if __name__ == '__main__':
    import entrance
    entrance.load_sqla()
    test()