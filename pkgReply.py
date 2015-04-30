# -*- coding: utf-8 -*-
#!/usr/bin/env python

__author__ = 'Kinslayer'
from utils import to_unicode, isstring
from models import *
import settings
import utils
import packageUtil
import web


class pkgResponse:
    TEMPLATE = to_unicode("""<xml>
<ToUserName><![CDATA[{ToUserName}]]></ToUserName>
<FromUserName><![CDATA[{ToUserName}]]></FromUserName>
<CreateTime>{CreateTime}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{Content}]]></Content>
</xml>""")

    kwargs = dict()

    def __init__(self, **kwargs):
        self.appsignature = ''
        self.kwargs = kwargs

    def create_signature(self):
        return utils.generate_sign(**self.kwargs)

    def render(self):
        if not self.appsignature:
            self.appsignature = self.create_signature()
            self.kwargs['appsignature'] = self.appsignature
        return self.TEMPLATE.format(**self.kwargs)


def get_reply(pkgreq):
    return pkgResponse(**pkgreq.kwargs).render()

