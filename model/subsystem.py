#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
子系统Model
'''

import time
import random
import hashlib
import datetime
from lib.database import Model


class SubSystem(Model):
    '''
    子系统
    '''
    _db = 'authsys'
    _table = 't_subsystem'
    _pk = 'id'
    _fields = set(['id', 'name', 'domain', 'syskey', 'secret', 'create_user',
                   'create_time', 'update_user', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`name` varchar(32) NOT NULL DEFAULT '' COMMENT '名称'",
               "`domain` varchar(64) NOT NULL DEFAULT '' COMMENT '域名'",
               "`syskey` varchar(32) NOT NULL DEFAULT '' COMMENT 'key'",
               "`secret` varchar(32) NOT NULL DEFAULT '' COMMENT 'secret'",
               "`create_user` varchar(32) NOT NULL DEFAULT ''",
               "`create_time` datetime NOT NULL DEFAULT '1970-01-01'",
               "`update_user` varchar(32) NOT NULL DEFAULT ''",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `name` (`name`)",
               "UNIQUE KEY `syskey` (`syskey`)")

    def gen_key_secret(self):
        '''
        随机生成唯一的key
        '''
        now = time.time()
        rval = random.random()
        key = hashlib.md5("%s%s%s" % (now, rval, self)).hexdigest()
        secret = hashlib.md5("%s%s%s" % (now, rval, key)).hexdigest()
        return key, secret

    def before_add(self):
        '''
        记录插入前, 自动生成key、secret
        '''
        if 'syskey' not in self or not self['syskey']:
            self['syskey'], self['secret'] = self.gen_key_secret()
        self['create_time'] = datetime.datetime.now()

