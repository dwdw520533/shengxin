#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
灰度环境
'''
import urlparse
from functools import partial

# Mysql配置
MDB_AUTH = {
    'host':'10.1.0.212',
    'user':'authsys',
    'passwd':'authsysMySQLDB',
    'db':'',
    'sock':'',
    'port':3306
}
SDB_AUTH = {
    'host':'10.1.0.211',
    'user':'authsys',
    'passwd':'authsysMySQLDB',
    'db':'',
    'sock':'',
    'port':3306
}

# Memcache 配置
MC_SERVERS = ['10.1.0.131:13000', '10.1.0.132:13000', '10.1.0.133:13000']

# 记录客服电话状态日志
CS_PHONE_LOG_DIR = '/data/logs/'

# auth conf
AUTH_CNF = {
    'domain': '.internal.jinlinbao.com',
    'cookie_name': 'session_id',
    'cookie_secret': 'FPdaUI5QAGaDdkL5gEmGeJJFuYh7EQnp2XdTP1',
    'sess_user': 'auth_user',
    'login_url': '/user/login',
    'login_errcnt': 5,
}

# 自动为内部用户注册近邻宝用户
API_REGISTER_STAFF_USER = 'http://10.1.0.101:9000/register/staff'

# 快递系统API
CABZOO_API = partial(urlparse.urljoin, 'http://10.1.0.101:9002')

