#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Abstract: init all the necessay models

import os
import sys

sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))

from lib.database import Model
from model.subsystem import SubSystem 
from model.menu import Menu
from model.notice import Notice, NoticeCategory, NoticeWho
from model.user import Organization,User,UserRole,Role,RolePerm,Perm,PermAttr,Resource

class BootStrap(object):
    '''
    initing 
    '''
    def start(self):
        # create user,role ...
        for i in (Organization,User,UserRole,Role,RolePerm,Perm,PermAttr,Resource, Notice,NoticeCategory, NoticeWho):
            i.new().init_table()
        # create super user 
        user = User.new()
        user.name = 'admin'
        user.passwd = 'admin!123456'
        user.is_root = 1
        user.is_staff = 1
        user.save()
        # create auth system
        sub = SubSystem.new()
        sub.init_table()
        sub.name = '登陆系统'
        authsys = sub.save()
        # create menu list for auth system
        Menu.new().init_table()
        menu_list = [{
                    'name':'用户管理',
                    'uri':'/user',
                    'no':1,
                    'children':[
                                {'name':'组织管理','uri':'/org/list','no':11},
                                {'name':'用户管理','uri':'/user/list','no':12},
                                {'name':'角色管理','uri':'/role/list','no':13},
                                {'name':'权限管理','uri':'/perm/list','no':14},
                                {'name':'资源管理','uri':'/resource/list','no':15},
                                ]
                    },
                    {
                        'name':'系统设置',
                        'uri':'/setting',
                        'no':2,
                        'children':[
                                    {'name':'菜单管理','uri':'/menu/list','no':21},
                                    {'name':'系统管理','uri':'/subsystem/list','no':22},
                                ]
                    },
	            {
                        'name':'通知管理',
                        'uri':'/notice',
                        'no':3,
                        'children':[
                                    {'name':'分类管理','uri':'/notice/category/list','no':31},
                                    {'name':'通知管理','uri':'/notice/list','no':32},
                                ]
                    }
		   ]
        for i in menu_list:
            mp = Menu.new() 
            mp.system_id = authsys.id
            mp.name = i['name']
            mp.uri = i['uri']
            mp.no = i['no']
            mp = mp.save()
            for j in i['children']:
                m = Menu.new()
                m.system_id = authsys.id
                m.parent_id = mp.id
                m.name = j['name']
                m.uri = j['uri']
                m.no = j['no']
                m.level = 1
                m.save()
        
if __name__ == "__main__":
    bs = BootStrap()
    bs.start()

