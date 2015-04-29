#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
岗位管理
"""
import json
from handler.base import BaseHandler
from service.position import PositionService
from service.role import RoleService
from service.org import OrganizationService
from conf.settings import (E_POSITION_DO_BIND_USERS,
                           E_POSITION_EXIST, E_POSITION_HAS_USERS)


class PositionHandler(BaseHandler):
    """
    岗位管理Handler
    """
    def list(self):
        """
        岗位查询并显示列表
        """
        name = self.get_argument('name', '')
        organization_id = self.get_argument_int('organization_id', 0)
        status = self.get_argument_int('status', '')
        page = self.get_argument_int('pageNum', 1)
        psize = self.get_argument_int('numPerPage', 20)
        orderby = self.get_argument('orderby', 'ID DESC')
        all_orgs = OrganizationService().read_all_orgs()

        params = {
            'name': name,
            'organization_id': organization_id,
            'status': status,
            'page': page,
            'psize': psize,
            'orderby': orderby,
        }
        _, res = PositionService().get_list(params)

        count = res.get('count', 0)
        page_count = (count + psize - 1) / psize

        self.render('user/position/list.html',
                    target_tab=self.target_tab,
                    param=params,
                    count=res['count'],
                    page_count=page_count,
                    position_list=res['list'],
                    all_orgs=all_orgs)

    def save(self):
        """
        岗位保存
        """
        position_id = self.get_argument_int('id', 0)
        name = self.get_argument('name')
        organization_id = self.get_argument_int('org_u0.id', 0)
        note = self.get_argument('note', '')
        status = self.get_argument_int('status', 1)
        role_ids = []
        for i in self.request.arguments:
            if i.startswith('role__'):
                role_ids.append(self.get_argument(i, ''))

        new_roles = [int(i) for i in role_ids if i]

        params = {
            'position_id': position_id,
            'name': name,
            'organization_id': organization_id,
            'note': note,
            'status': status,
            'cur_username': self.current_user['name'],
            'new_roles': new_roles,
        }

        code, _ = PositionService().save(params)

        if code == 0:
            self.json2dwz('200', 'closeCurrent', self.target_tab, msg='保存成功!')
        elif code == E_POSITION_DO_BIND_USERS:
            self.json2dwz('300', '', msg='该岗位有绑定正在使用的用户，请先修改这些用户的岗位再做删除')
        elif code == E_POSITION_EXIST:
            self.json2dwz('300', '', msg='该岗位名称已存在，请核对')
        else:
            self.json2dwz('300', '', self.target_tab, msg='')

    def add(self):
        """
        岗位增加
        """
        #all_orgs = self.filter_org_query(Organization.mgr().Q())
        #all_roles = self.filter_role_query(Role.mgr().Q())
        all_orgs = OrganizationService().read_all_orgs()
        all_roles = RoleService().read_all_roles()
        self.render('user/position/add.html',
                    target_tab=self.target_tab,
                    all_orgs=all_orgs,
                    all_status={1:'正常', 2:'禁用'},
                    all_roles=all_roles)

    def edit(self):
        """
        岗位编辑
        """
        pos_id = self.get_argument_int('id')
        pos_info = PositionService().read_position_byid(pos_id, ismaster=1)
        cur_roles = PositionService().get_roleids_byposid(pos_id)
        #all_roles = self.filter_role_query(Role.mgr().Q())
        #all_orgs = self.filter_org_query(Organization.mgr().Q())
        all_orgs = OrganizationService().read_all_orgs()
        all_roles = RoleService().read_all_roles()
        self.render('user/position/edit.html',
                    target_tab=self.target_tab,
                    pos_info=pos_info,
                    all_orgs=all_orgs,
                    cur_roles=cur_roles,
                    all_status={1:'正常', 2:'禁用'},
                    all_roles=all_roles)

    def detail(self):
        """
        岗位查看详情
        """
        pos_id = self.get_argument_int('id')
        pos_info = PositionService().read_position_byid(pos_id, ismaster=1)
        cur_roles = PositionService().get_roleids_byposid(pos_id)
        all_roles = RoleService().read_all_roles()
        all_orgs = OrganizationService().read_all_orgs()
        self.render('user/position/detail.html',
                    target_tab=self.target_tab,
                    pos_info=pos_info,
                    all_orgs=all_orgs,
                    all_status={1:'正常', 2:'禁用'},
                    cur_roles=cur_roles,
                    all_roles=all_roles)

    def delete(self):
        """
        岗位删除
        """
        pos_id = self.get_argument_int('id')
        #PositionService().set_status(position_id, 3)
        code, _ = PositionService().check_and_delete(pos_id)
        if code == 0:
            self.json2dwz('200', 'forward', self.target_tab, forward_url='position/list')
            return

        msg = ''
        if code == E_POSITION_HAS_USERS:
            msg = '有用户关联此岗位, 不能删除。请先把用户从该岗位中移除再做删除操作'

        self.json2dwz('300', '', msg=msg)

    def ref(self):
        """
        根据指定组织id， org_id获得岗位列表
        """
        org_id = self.get_argument_int('org_id', 0)
        flag = self.get_argument_int('flag', 0)
        res = []
        if flag == 1:
            res.append(['', '不限'])
        elif flag == 2:
            res.append(['', '无'])

        pos_list = PositionService().read_positions_by_orgid(org_id)
        for i in pos_list:
            res.append([i['id'], i['name']])
        self.write(json.dumps(res))
