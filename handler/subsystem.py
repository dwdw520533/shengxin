#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
子系统管理
"""
from handler.base import BaseHandler
from model.subsystem import SubSystem


class SubSystemHandler(BaseHandler):
    """
    子系统管理Handler
    """
    def list(self):
        """
        子系统查询
        """
        subsys_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        syskey = self.get_argument('syskey', '')
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        query = SubSystem.mgr().Q()
        if subsys_id:
            query.filter(id=subsys_id)
        if syskey:
            query.filter(syskey=syskey)
        if name:
            query.extra("name LIKE '%%%s%%'"%name)
        count = query.count()
        page_count = (count+psize-1)/psize
        subsystems = query[(page-1)*psize:page*psize]
        self.render('setting/subsystem_list.html',
                    target_tab=self.target_tab,
                    name=name,
                    syskey=syskey,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    subsystems=subsystems)

    def save(self):
        """
        子系统保存
        """
        subsys_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        domain = self.get_argument('domain')
        # 参数检查
        msg = ''
        subsys = SubSystem.mgr().Q().filter(name=name)[0]
        if subsys and subsys_id != subsys.id:
            msg = '子系统[%s]已经存在' % name
        if msg:
            self.json2dwz('300', '', msg=msg)
            return
        # 保存到数据库
        if subsys_id:
            subsys = SubSystem.mgr(ismaster=True).one(subsys_id)
        else:
            subsys = SubSystem.new()
            subsys.create_user = self.current_user['name']
        subsys.name, subsys.domain = name, domain
        subsys.update_user = self.current_user['name']
        subsys.save()
        self.json2dwz('200', 'closeCurrent', self.target_tab)

    def add(self):
        """
        子系统增加
        """
        self.render('setting/subsystem_add.html',
                    target_tab=self.target_tab)

    def edit(self):
        """
        子系统编辑
        """
        subsys_id = int(self.get_argument('id'))
        subsystem = SubSystem.mgr(ismaster=1).one(subsys_id)
        self.render('setting/subsystem_edit.html',
                    target_tab=self.target_tab,
                    subsystem=subsystem)

    def delete(self):
        """
        子系统删除
        """
        subsys_id = int(self.get_argument('id'))
        subsystem = SubSystem.mgr(ismaster=1).one(subsys_id)
        if subsystem:
            subsystem.delete()
        self.json2dwz('200', 'forward', self.target_tab, forward_url='subsystem/list')

