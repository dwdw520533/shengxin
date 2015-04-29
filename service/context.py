#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全局资源上下文
"""
import json
import urllib
import urllib2
from lib.mclient import MClient
from conf.settings import MC_SERVERS


class Singleton(object):
    """
    单例类
    """
    _instance = None
    def __new__(cls, *args, **kargs):
        """
        真正的 "构造" 函数
        """
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kargs)
        return cls._instance


class Context(object):
    """
    全局资源上下文
    """
    def __init__(self):
        """
        初始化全局变量
        """
        # memcache缓存
        self.cache = MClient(MC_SERVERS)

    @staticmethod
    def inst():
        """
        单例
        """
        name = '_instance'
        if not hasattr(Context, name):
            setattr(Context, name, Context())
        return getattr(Context, name)

    @staticmethod
    def send_request(url, params=None):
        """
        发送请求
        :param url: 请求地址
        :param params: 参数
        :return: code, data
        """
        res = urllib2.urlopen(url, urllib.urlencode(params))
        res = json.loads(res.read())
        return res

    def read_user_group(self, user_id, domain):
        """
        获取用户分组
        :param user_id: 用户ID
        :param domain: 当前系统的域名
        :return: user_group
        """
        if domain.startswith("http://"):
            url = '%s/group/user/find' % domain
        else:
            url = 'http://%s/group/user/find' % domain
        res = self.send_request(url, {'user_id': user_id})
        return None if not res else res['body']

