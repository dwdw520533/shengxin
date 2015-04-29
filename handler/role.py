#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
角色管理
"""
from handler.base import BaseHandler
from service.perm import PermService
from service.role import RoleService
from conf.settings import E_ROLE_EXIST, E_SUCC


class RoleHandler(BaseHandler):
    """
    角色管理Handler
    """
    def list(self):
        """
        角色查询
        """
        role_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        orderby = self.get_argument('orderby', 'ID DESC')

        params = {
            'name': name,
            'role_id': role_id,
            'page': page,
            'psize': psize,
            'orderby': orderby,
        }
        #res 返回的是对象的合集
        _, res = RoleService().get_list_objects(params)
        roles = res.get('list', [])
        count = res.get('count', 0)
        page_count = (count + psize - 1) / psize

        self.render('user/role/list.html',
                    target_tab=self.target_tab,
                    name=name,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    roles=roles)

    def save(self):
        """
        角色保存
        """
        role_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        perm_ids = []
        for i in self.request.arguments:
            if i.startswith('perm__'):
                perm_ids.append(self.get_argument(i, ''))
        perm_ids = [int(i) for i in perm_ids if i]
        msg = ''
        if not perm_ids:
            msg = '请选择权限'
        if msg:
            self.json2dwz('300', '', msg=msg)
            return

        params = {
            'role_id': role_id,
            'name': name,
            'perm_ids': perm_ids,
        }

        code, _ = RoleService().check_and_save(params)
        if code == E_SUCC:
            self.json2dwz('200', 'closeCurrent', self.target_tab, msg='保存成功!')

        if code == E_ROLE_EXIST:
            msg = '角色[%s]已经存在' % name
            self.json2dwz('300', '', msg=msg)
            return

    def add(self):
        """
        角色增加
        """
        #all_perms = self.filter_perm_query(Perm.mgr().Q())
        all_perms = all_perms = PermService().read_all_perms()
        self.render('user/role/add.html',
                    target_tab=self.target_tab,
                    all_perms=all_perms)

    def edit(self):
        """
        角色增加
        """
        role_id = int(self.get_argument('id'))
        role = RoleService().read_role_byid(role_id)
        role_perms = RoleService().get_perms_byroleid(role_id)
        cur_perm_ids = [i.id for i in role_perms]
        all_perms = PermService().read_all_perms()
        self.render('user/role/edit.html',
                    target_tab=self.target_tab,
                    role=role,
                    cur_perm_ids=cur_perm_ids,
                    all_perms=all_perms)

    def delete(self):
        """
        角色删除
        """
        role_id = int(self.get_argument('id'))
        RoleService().delete(role_id)
        self.json2dwz('200', 'forward', self.target_tab, forward_url='role/list')
