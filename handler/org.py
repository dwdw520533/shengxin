#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
组织管理
"""
import json
from handler.base import BaseHandler
from model.user import Organization
from service.org import OrganizationService
from conf.settings import(E_SUCC, E_ORG_HAS_USERS, E_ORG_EXIST,
                          OPERSYS_ORG_HAS_LOGIS, E_ORG_NOT_EXIST)


class OrgHandler(BaseHandler):
    """
    组织管理Handler
    """
    def list(self):
        """
        组织查询
        """
        org_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        parent_id = int(self.get_argument('orgparent.id', 0))
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        orderby = self.get_argument('orderby', 'ID DESC')

        params = {
            'org_id': org_id,
            'name': name,
            'parent_id': parent_id,
            'page': page,
            'psize': psize,
            'orderby': orderby,
        }
        _, res = OrganizationService().get_list_objects(params)
        orgs = res.get('org_list', [])
        count = res.get('count', 0)
        page_count = (count + psize - 1) / psize
        #all_orgs = self.filter_org_query(Organization.mgr().Q()).data()
        all_orgs = OrganizationService().read_all_orgs()
        self.render('user/org/list.html',
                    target_tab=self.target_tab,
                    name=name,
                    parent_id=parent_id,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    orgs=orgs,
                    all_orgs=all_orgs)

    def search(self):
        """
        组织搜索
        """
        org_name = self.get_argument('org_name', '')
        query = Organization.mgr().Q().filter(status=1)
        query.extra("name LIKE '%%%s%%'"%org_name)
        query = self.filter_org_query(query)
        orgs = [{'id':i.id, 'name':i.name} for i in query[:10]]
        self.write(json.dumps(orgs))

    def save(self):
        """
        组织保存
        """
        org_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        status = self.get_argument_int('status', 1)
        parent_id = int(self.get_argument('orgparent%s.id' % org_id, 0))
        parent = OrganizationService().read_org_byid(parent_id)

        params = {
            'org_id': org_id,
            'name': name,
            'status': status,
            'parent': parent,
            'parent_id': parent_id,
            'cur_username': self.current_user['name'],
        }

        code, res = OrganizationService().check_and_save(params)

        if code == 0:
            self.json2dwz('200', 'closeCurrent', self.target_tab, msg='保存成功!')
            return

        msg = ''
        if code == E_ORG_EXIST:
            msg = '组织[%s]已经存在' % name
            self.json2dwz('300', '', msg=msg)
        elif code == E_ORG_NOT_EXIST:
            self.json2dwz('300', '', msg='岗位记录不存在。不能更新')
        else:
            self.json2dwz('300', '', self.target_tab, msg='')

    def add(self):
        """
        组织增加
        """
        #query = Organization.mgr().Q().filter(status=1)
        all_orgs = OrganizationService().read_all_orgs()
        self.render('user/org/add.html',
                    target_tab=self.target_tab,
                    #all_orgs=self.filter_org_query(query))
                    all_orgs=all_orgs)

    def edit(self):
        """
        组织编辑
        """
        oid = int(self.get_argument('id'))
        org = Organization.mgr(ismaster=1).one(oid)
        #query = Organization.mgr().Q().filter(status=1)
        all_orgs = OrganizationService().read_all_orgs()
        self.render('user/org/edit.html',
                    target_tab=self.target_tab,
                    org=org,
                    #all_orgs=self.filter_org_query(query))
                    all_orgs=all_orgs)

    def delete(self):
        """
        组织删除
        通过before_delete,删除角色的同时删除其与岗位、用户、权限的关系
        """
        org_id = int(self.get_argument('id'))
        code, res = OrganizationService().check_and_delete(org_id)
        if code == E_SUCC:
            self.json2dwz('200', 'forward', self.target_tab, forward_url='org/list')
            return

        msg = ''
        if code == E_ORG_HAS_USERS:
            msg = '有用户关联组织或其下级组织中, 不能删除。请先把用户从组织中移除再做删除操作'

        if code == OPERSYS_ORG_HAS_LOGIS:
            msg = '有物流中心或校园小区关联组织或其下级组织, 请联系管理员处理'

        self.json2dwz('300', '', msg=msg)
        return

    def treelookup(self):
        """
        组织弹窗tree查询
        """
        _, all_orgs = OrganizationService().read_org_groupby_list()
        self.render('user/org/treelookup.html',
                    target_tab=self.target_tab,
                    colDict=all_orgs)
