#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
测试环境
'''
import urlparse
from functools import partial

# Mysql配置
MDB_AUTH = {
    'host':'10.0.1.233',
    'user':'zkfc',
    'passwd':'zkfc123',
    'db':'',
    'sock':'',
    'port':3306
}
SDB_AUTH = {
    'host':'10.0.1.233',
    'user':'zkfc',
    'passwd':'zkfc123',
    'db':'',
    'sock':'',
    'port':3306
}

# memcache 配置
MC_SERVERS = ['10.0.1.233:11000']

# 记录客服电话状态日志
CS_PHONE_LOG_DIR = 'logs'

# auth conf
AUTH_CNF = {
    'domain': '.dev.jinlinbao.com',
    'cookie_name': 'session_id',
    'cookie_secret': 'FPdaUI5QAGaDdkL5gEmGeJJFuYh7EQnp2XdTP1',
    'sess_user': 'auth_user',
    'login_url': '/user/login',
    'login_errcnt': 5,
}

# 外部用户注册接口
API_REGISTER_STAFF_USER = 'http://10.0.1.232:9000/register/staff'

# 快递系统API
CABZOO_API = partial(urlparse.urljoin, 'http://10.0.1.232:9002')
