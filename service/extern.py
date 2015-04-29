#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
外部接口
"""
import json
import socket
import urllib
import urllib2
import logging
from lib.utils import force_utf8
from conf.settings import (E_INTER, API_REGISTER_STAFF_USER, HTTP_TIMEOUT)
from service.context import Singleton, Context

class ExternService(Singleton):
    """
    外部数据接口
    """
    def __init__(self):
        """
        初始化
        @context: 全局资源环境
        """
        self.ctx = Context.inst()

    @staticmethod
    def send_request(url, param=None, timeout=HTTP_TIMEOUT, resp_format='json'):
        """
        获得请求值
        :param url: 地址
        :param param: 参数
        :return: 返回json
        """
        try:
            url = '%s?%s' % (url, urllib.urlencode(param)) if param else url
            resp = urllib2.urlopen(url, timeout=timeout).read()
            if resp_format == 'json':
                return force_utf8(json.loads(resp))
            else:
                return resp
        except (urllib2.URLError, socket.error) as ex:
            logging.error('fail to get url:%s, %s', url, str(ex), exc_info=True)
        return None

    def register_staff_user(self, phone, password):
        """
        自动为内部系统用户创建近邻宝用户

        :param phone: 用户手机号
        :param password: 密码
        :return: 业务码, 近邻宝用户信息
        """
        param = {
            'phone': phone,
            'password':password
        }
        res = self.send_request(API_REGISTER_STAFF_USER, param)
        if not res:
            return E_INTER, None
        return res['code'], res['body']

