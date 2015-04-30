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
<AppId><![CDATA[{appid}]]></AppId>
<Package><![CDATA[{package}]]></Package>
<TimeStamp>{timestamp}</TimeStamp>
<NonceStr><![CDATA[{noncestr}]]></NonceStr>
<RetCode>{retcode}</RetCode>
<RetErrMsg><![CDATA[{reterrmsg}]]></RetErrMsg>
<AppSignature><![CDATA[{appsignature}]]></AppSignature>
<SignMethod><![CDATA[{signmethod}]></SignMethod>
</xml>""")

    _args = dict()

    def __init__(self, **kwargs):
        if 'appid' in kwargs:
            self.appid = kwargs['appid']
        if 'package' in kwargs:
            self.package = kwargs['package']
        if 'timestamp' in kwargs:
            self.timestamp = kwargs['timestamp']
        if 'noncestr' in kwargs:
            self.noncestr = kwargs['noncestr']
        if 'retcode' in kwargs:
            self.retcode = kwargs['retcode']
        if 'reterrmsg' in kwargs:
            self.reterrmsg = kwargs['reterrmsg']
        if 'appsignature' in kwargs:
            self.appsignature = kwargs['appsignature']
        else:
            self.appsignature = ''

        if 'signmethod' in kwargs:
            self.signmethod = kwargs['signmethod']
        args = dict()
        for k, v in kwargs.items():
            if isstring(v):
                v = to_unicode(v)
            args[k] = v

        self._args = args

    def create_signature(self):
        adict = dict(appid=self.appid,
                     appkey=settings.paySignKey,
                     package=self.package,
                     timestamp=self.timestamp,
                     noncestr=self.noncestr)
        adict['retcode'] = self.retcode
        adict['reterrmsg'] = self.reterrmsg
        return utils.generate_sign(**adict)

    def render(self):
        if not self.appsignature:
            self.appsignature = self.create_signature()
            self._args['appsignature'] = self.appsignature
        return self.TEMPLATE.format(**self._args)


def get_reply(pkgreq):
    #TODO 需要添加支付已经完成等情况的测试, 不确定微信的系统内是否会对这种情况进行处理
    pkg = web.ctx.db.query(Package).filter(Package.out_trade_no == pkgreq.productid).first()
    errmsg = ''
    if not pkg:
        errmsg = '未找到对应订单!'

    adict = {
        'appid': settings.appId,
        'package': packageUtil.pkg_to_string(pkg) if pkg else '',
        'timestamp': utils.timestamp(),
        'noncestr': utils.noncestr(),
        'retcode': 1 if errmsg else 0,
        'reterrmsg': errmsg if errmsg else 'ok!',

        'signmethod': 'sha1'
    }

    return pkgResponse(**adict).render()

