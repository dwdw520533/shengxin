#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
菜单Model
'''

import datetime
from lib.database import Model
from model.subsystem import SubSystem
from model.user import Resource

class Menu(Model):
    '''
    菜单
    '''
    _db = 'authsys'
    _table = 'menu'
    _pk = 'id'
    _fields = set(['id', 'system_id', 'parent_id', 'name', 'level', 'resource_id',
                   'uri', 'target_tab', 'no', 'create_user', 'create_time',
                   'update_user', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`system_id` int NOT NULL DEFAULT '0' COMMENT '子系统ID'",
               "`parent_id` int NOT NULL DEFAULT '0' COMMENT '上级菜单ID'",
               "`name` varchar(32) NOT NULL DEFAULT '' COMMENT '菜单名'",
               "`level` int NOT NULL DEFAULT '0' COMMENT '菜单级别'",
               "`resource_id` int NOT NULL DEFAULT '0' COMMENT '对应的资源ID'",
               "`uri` varchar(255) NOT NULL DEFAULT '' COMMENT '对应的uri'",
               "`target_tab` varchar(32) NOT NULL DEFAULT '' COMMENT '页面上显示的tabID'",
               "`no` int NOT NULL DEFAULT '0' COMMENT '菜单序号'",
               "`create_user` varchar(32) NOT NULL DEFAULT ''",
               "`create_time` datetime NOT NULL DEFAULT '1970-01-01'",
               "`update_user` varchar(32) NOT NULL DEFAULT ''",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `sysid_parentid_name` (`system_id`,`parent_id`,`name`)")
    def before_add(self):
        '''
        插入记录前, 自动生成create_time
        '''
        self['create_time'] = datetime.datetime.now()

    def path(self):
        '''
        菜单树的root到自身节点的路径
        '''
        path = [self]
        parent = self.parent
        if parent:
            path = parent.path() + path
        return path

    @property
    def system(self):
        '''
        菜单所属的系统
        '''
        return SubSystem.mgr(self.ismaster).one(self.system_id)

    @property
    def parent(self):
        '''
        上级菜单
        '''
        return Menu.mgr(self.ismaster).one(self.parent_id)

    @property
    def resource(self):
        '''
        对应的资源
        '''
        return Resource.mgr(self.ismaster).one(self.resource_id)

    @property
    def full_name(self):
        '''
        菜单的全名
        '''
        return '-'.join([i.name for i in self.path()])

    def children(self):
        '''
        下级菜单列表
        '''
        for i in Menu.mgr(self.ismaster).Q().filter(parent_id=self.id):
            yield i

    def descent(self):
        '''
        所有的子孙菜单
        '''
        for i in self.children():
            yield i
            for j in i.descent():
                yield j

    def is_leaf(self):
        '''
        是否是叶节点(只有叶节点上才有具体的uri)
        '''
        return bool(self.uri)

