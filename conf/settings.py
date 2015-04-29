#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
相关配置
'''

import json

# HTTP超时
HTTP_TIMEOUT = 3

# 登陆会话
COOKIE_NAME = 'session_id'
COOKIE_SECRET = 'FPdaUI5QAGaDdkL5gEmGeJJFuYh7EQnp2XdTP1'
SESSION_USER = 'auth_user'
SESSION_SYSTEM = 'auth_system'
SESSION_LOGIN_ERRCNT = 'login_errcnt'

# 系统错误码
E_SUCC, E_PARAM, E_INTER, E_TIMEOUT, E_RESRC, E_EXTERNAL, E_AUTH, E_FORBID = 0, 1, 2, 3, 4, 5, 6, 7

# 基本 20000 - 20019
E_LOCKED, E_USER_NOT_EXIST, E_USER_EXISTED = 20000, 20001, 20002
E_NAME_INVALID, E_NICK_INVALID = 20003, 20004
E_PASSWD_INVALID, E_GENDER_INVALID = 20005, 20006
E_PHONE_INVALID, E_AVATAR_INVALID = 20007, 20008
E_PASSWD_WRONG, E_PCODE_WRONG = 20009, 20010
E_PCODE_RETRY_LATER = 20011
E_NOT_LOGINED, E_NOT_STAFF = 20012, 20013
E_ROLE_NOT_EXIST = 20014
E_POSITION_NOT_EXIST = 20015
E_RES_ACTION_NOT_EXIST = 20016
E_USER_EMAIL_EXIST = 20017
E_USER_PHONE_EXIST = 20018  #用户表中phone已存在
E_CREATE_JLB_USER_FAILED = 20019  #自动创建近邻宝用户失败
E_RES_ACTION_CODE_EXIST = 20020  #res_action中code已存在
E_PERM_EXIST = 20021  #权限已存在
E_PERM_NOT_EXIST = 20022  #权限不存在
E_ROLE_EXIST = 20023  #权限存在
E_RESOURCE_EXIST = 20024  #资源存在
E_RESOURCE_NOT_EXIST = 20025  #资源不存在
E_POSITION_DO_BIND_USERS = 20026  #岗位已绑定用户（用于禁用时）
E_POSITION_EXIST = 20027  #岗位已存在
E_ORG_HAS_USERS = 20028  #组织或这其下级组织中包含用户
OPERSYS_CALL_API_FAILED = 20029  #调用opersys的API失败
OPERSYS_ORG_HAS_LOGIS = 20030  #opersys中，组织有对应的物流中心或学校校区
E_POSITION_HAS_USERS = 20031  #岗位中包含用户(用于删除时返回msg)
E_ORG_EXIST = 20032  #组织存在
E_ORG_NOT_EXIST = 20033  #组织不存在

# 错误码描述
ERR_DESC = {
    E_SUCC: 'OK',
    E_PARAM: '参数错误',
    E_INTER: '程序内部错误',
    E_TIMEOUT: '外部接口超时',
    E_RESRC: '接口不存在',
    E_EXTERNAL: '外部接口错误',
    E_AUTH: '鉴权失败',
    E_FORBID: '访问被禁止',
}

# 测试、灰度、线上
from tornado.options import define, options
if not hasattr(options, 'runmode'):
    define('runmode', default='dev', help='dev gray prod')
    define('debug', default=True, help='enable debug')
    options.parse_command_line()

# 加载相应环境的配置
if options.runmode == 'dev':
    from conf.settings_dev import *
elif options.runmode == 'test':
    from conf.settings_test import *
elif options.runmode == 'gray':
    from conf.settings_gray import *
elif options.runmode == 'prod':
    from conf.settings_prod import *
else:
    raise Exception('wrong runmode')

# conf for db and model
DB_CNF = {
    'm':{
        json.dumps(MDB_AUTH):['authsys']
    },
    's':{
        json.dumps(SDB_AUTH):['authsys']
    },
}

# Let pylint shutup
ENV_VARLIST = (MC_SERVERS, )
