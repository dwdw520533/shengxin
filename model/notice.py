#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
公告 Model
'''

import datetime
from lib.database import Model

class Notice(Model):
    '''
    公告
    '''
    _db = 'authsys'
    _table = 't_notice'
    _pk = 'id'
    _fields = set(['id', 'name', 'content', 'category_id', 'is_top', 'is_global',
                   'no', 'status', 'create_user', 'create_time', 'update_user',
                   'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`name` varchar(64) NOT NULL DEFAULT '' COMMENT '标题'",
               "`content` text NOT NULL COMMENT '内容'",
               "`category_id` int NOT NULL DEFAULT '0' COMMENT '分类ID'",
               "`is_top` tinyint NOT NULL DEFAULT '0' COMMENT '是否置顶'",
               "`is_global` tinyint NOT NULL DEFAULT '0' COMMENT '是否面向所有人'",
               "`no` int NOT NULL DEFAULT '0' COMMENT '序号'",
               "`status` tinyint NOT NULL DEFAULT '0' COMMENT '是否有效'",
               "`create_user` varchar(32) NOT NULL DEFAULT ''",
               "`create_time` datetime NOT NULL DEFAULT '1970-01-01'",
               "`update_user` varchar(32) NOT NULL DEFAULT ''",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "KEY `name` (`name`)",
               "KEY `no` (`no`)")

    def before_add(self):
        '''
        创建时间
        '''
        self['create_time'] = datetime.datetime.now()

    @property
    def category(self):
        '''
        获取分类
        '''
        return NoticeCategory.mgr(ismaster=self.ismaster).one(self.category_id)

class NoticeCategory(Model):
    '''
    公告类别
    '''
    _db = 'authsys'
    _table = 't_notice_category'
    _pk = 'id'
    _fields = set(['id', 'name', 'no', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`name` varchar(64) NOT NULL DEFAULT '' COMMENT '类别名称'",
               "`no` int NOT NULL DEFAULT '0' COMMENT '序号'",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `name` (`name`)")

class NoticeWho(Model):
    '''
    公告所属
    '''
    _db = 'authsys'
    _table = 't_notice_who'
    _pk = 'id'
    _fields = set(['id', 'notice_id', 'who_type', 'who_id', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`notice_id` int NOT NULL DEFAULT '0' COMMENT '公告ID'",
               "`who_type` enum('user','organization','role') NOT NULL DEFAULT 'user' COMMENT '类型'",
               "`who_id` int NOT NULL DEFAULT '0' COMMENT '用户ID,组织ID,角色ID'",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `noticeid_whotype_whoid` (`notice_id`,`who_type`,`who_id`)")

