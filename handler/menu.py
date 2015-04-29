#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
菜单管理
"""
import json
from handler.base import BaseHandler
from model.menu import Menu
from model.subsystem import SubSystem
from model.user import Resource


class MenuHandler(BaseHandler):
    """
     菜单管理Handler
    """
    def list(self):
        """
        菜单查询
        """
        menu_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        system_id = int(self.get_argument('system_id', 0) or 0)
        parent_id = int(self.get_argument('parent_id', 0) or 0)
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        query = Menu.mgr().Q().orderby('no')
        if menu_id:
            query.filter(id=menu_id)
        if name:
            query.extra("name LIKE '%%%s%%'" % name)
        if system_id:
            query.filter(system_id=system_id)
        if parent_id:
            query.filter(parent_id=parent_id)
        count = query.count()
        page_count = (count+psize-1)/psize
        menus = query[(page-1)*psize:page*psize]
        all_menus = Menu.mgr().Q().data()
        all_systems = SubSystem.mgr().Q().data()
        self.render('setting/menu_list.html',
                    target_tab=self.target_tab,
                    name=name,
                    system_id=system_id,
                    parent_id=parent_id,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    menus=menus,
                    all_menus=all_menus,
                    all_systems=all_systems)

    def save(self):
        """
        菜单保存
        """
        menu_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        system_id = int(self.get_argument('system_id') or 0)
        parent_id = int(self.get_argument('parent_id', 0) or 0)
        resource_id = int(self.get_argument('resource_id', 0) or 0)
        uri = self.get_argument('uri', '')
        target = self.get_argument('target', '')
        no = int(self.get_argument('no', 0))
        parent = Menu.mgr().one(parent_id)
        # 参数检查
        msg = ''
        menu = Menu.mgr().Q().filter(system_id=system_id, parent_id=parent_id, name=name)[0]
        if menu and menu_id != menu.id:
            msg = '菜单[%s:%s]已经存在' % (menu.system.name, menu.full_name)
        resource = Resource.mgr().one(resource_id)
        if resource and resource.system_id != system_id:
            msg = '资源[%s]不属于所选子系统[%s]' % (resource.full_name, SubSystem.mgr().one(system_id).name)
        if msg:
            self.json2dwz('300', '', msg=msg)
            return
        # 保存到数据库
        if not parent:
            parent_id, level = 0, 0
        else:
            level = parent.level + 1
        if menu_id:
            menu = Menu.mgr(ismaster=True).one(menu_id)
        else:
            menu = Menu.new()
            menu.create_user = self.current_user['name']
        menu.name, menu.level, menu.parent_id, menu.system_id = name, level, parent_id, system_id
        menu.resource_id, menu.uri, menu.target_tab, menu.no = resource_id, uri, target, no
        menu.update_user = self.current_user['name']
        menu = menu.save()
        self.json2dwz('200', 'closeCurrent', self.target_tab)

    def add(self):
        """
        菜单增加
        """
        all_menus = Menu.mgr().Q().data()
        all_systems = SubSystem.mgr().Q().data()
        all_resources = Resource.mgr().Q().data()
        self.render('setting/menu_add.html',
                    target_tab=self.target_tab,
                    all_menus=all_menus,
                    all_systems=all_systems,
                    all_resources=all_resources)

    def edit(self):
        """
        菜单编辑
        """
        mid = int(self.get_argument('id'))
        menu = Menu.mgr(ismaster=1).one(mid)
        all_menus = Menu.mgr().Q().filter(system_id=menu.system_id).data()
        all_systems = SubSystem.mgr().Q().data()
        all_resources = Resource.mgr().Q().filter(system_id=menu.system_id).data()
        self.render('setting/menu_edit.html',
                    target_tab=self.target_tab,
                    menu=menu,
                    all_menus=all_menus,
                    all_systems=all_systems,
                    all_resources=all_resources)

    def delete(self):
        """
        菜单删除
        """
        mid = int(self.get_argument('id'))
        menu = Menu.mgr(ismaster=1).one(mid)
        menu.delete()
        self.json2dwz('200', 'forward', self.target_tab, forward_url='menu/list')

    def ref(self):
        """
        根据指定system_id获得菜单列表
        """
        system_id = int(self.get_argument('system_id', 0))
        flag = int(self.get_argument('flag', 0))
        query = Menu.mgr().Q()
        if system_id:
            query.filter(system_id=system_id)
        res = []
        if flag == 1:
            res.append(['', '不限'])
        elif flag == 2:
            res.append(['', '无'])
        for i in query:
            res.append([i.id, i.full_name])
        self.write(json.dumps(res))

