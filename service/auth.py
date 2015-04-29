#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
登陆认证
"""
import time
import hashlib
from conf.settings import AUTH_CNF
from lib.session import TornadoSessionManager
from service.context import Context
from model.subsystem import SubSystem
from model.user import User


class AuthService(object):
    """
    鉴权相关逻辑
    """
    K_SUBSYS = 'authsys_subsys_%s'
    def __init__(self):
        """
        初始化
        """
        self.ctx = Context.inst()
        self.session_mgr = TornadoSessionManager(AUTH_CNF['cookie_secret'],
                                                 self.ctx.cache,
                                                 AUTH_CNF['cookie_name'],
                                                 AUTH_CNF['domain'])

    def get_subsystem(self, syskey):
        """
        通过子系统Key获取子系统信息

        :param syskey: 子系统Key
        :return: 子系统信息
        """
        key = self.K_SUBSYS % syskey
        res = self.ctx.cache.get(key)
        if not res:
            rlist = SubSystem.mgr().Q().filter(syskey=syskey).query()
            res = rlist[0] if rlist else None
            self.ctx.cache.set(key, res, 3600)
        return res

    def sign(self, key):
        """
        获取某一子系统的签名

        :paramkey: 子系统Key
        :return: (子系统KEY, 时间戳, 签名)
        """
        sub, timestamp = self.get_subsystem(key), time.time()
        sign = hashlib.md5('%s%s%s' % (key, int(timestamp), sub['secret'])).hexdigest()
        return (key, timestamp, sign)

    def verify(self, key, timestamp, sign):
        """
        验证请求的签名

        :param key: 子系统Key
        :param timestamp: 时间戳
        :param sign: 签名
        :return: True or False
        """
        subsys = self.get_subsystem(key)
        if not subsys:
            return False
        _sign = hashlib.md5('%s%s%s'%(key, int(timestamp), subsys['secret'])).hexdigest()
        return sign == _sign

    def get_user_by_sessionid(self, session_id):
        """
        通过会话ID获取用户信息

        :param session_id: 会话ID
        :return: 当前登录用户信息
        """
        session = self.session_mgr.load_session(session_id=session_id)
        if not session:
            return None
        uinfo = session[AUTH_CNF['sess_user']]
        if not uinfo:
            return None
        return User.mgr().one(uinfo['uid'])

