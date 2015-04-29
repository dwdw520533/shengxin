#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
权限管理
"""
from conf.settings import E_PERM_EXIST
from handler.base import BaseHandler
from service.perm import PermService
from service.resaction import ResActionService
from service.resource import ResourceService


class PermHandler(BaseHandler):
    """
    权限管理Handler
    """
    def list(self):
        """
        权限查询
        """
        perm_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        orderby = self.get_argument('orderby', 'ID DESC')

        params = {
            'perm_id': perm_id,
            'name': name,
            'page': page,
            'psize': psize,
            'orderby': orderby
        }

        _, res = PermService().get_list_objects(params)
        perms = res.get('perm_list', [])
        count = res.get('count', 0)
        page_count = (count + psize - 1) / psize

        self.render('user/perm/list.html',
                    target_tab=self.target_tab,
                    name=name,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    perms=perms)

    def save(self):
        """
        权限保存
        """
        perm_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        #oper = self.get_argument('oper')  #html页面中移除此内容
        resource_id = int(self.get_argument('resource_id', 0))
        resource = ResourceService().read_resource_byid(resource_id)
        #获取资源操作code
        new_ract_codes = []
        for i in self.request.arguments:
            if i.startswith('ract_code__'):
                new_ract_codes.append(self.get_argument(i, ''))

        # 权限的资源、属性信息
        all_attrs = []
        if resource:
            if resource['attr']:
                all_attrs = [i for i in resource['attr'].split(':') if i]
        perm_attr = {}
        for i in all_attrs:
            perm_attr[i] = self.get_argument('__%s' % i, '')

        params = {
            'perm_id':perm_id,
            'name':name,
            'resource':resource,
            'resource_id':resource_id,
            'new_ract_codes':new_ract_codes,
            'perm_attr':perm_attr
        }

        code, _ = PermService().check_and_save(params)
        if code == 0:
            self.json2dwz('200', 'closeCurrent', self.target_tab)

        msg = ''
        if code == E_PERM_EXIST:
            msg = '权限[%s]已经存在' % name
            self.json2dwz('300', '', msg=msg)

    def add(self):
        """
        权限增加
        """
        #resources = self.filter_resource_query(Resource.mgr().Q())
        resources = ResourceService().read_all_resources()
        all_res_acts = ResActionService().read_all_resacts()
        self.render('user/perm/add.html',
                    target_tab=self.target_tab,
                    sub_systems=self.get_subsystems(),
                    resources=resources,
                    all_res_acts=all_res_acts,
                    perm_attr={})

    def edit(self):
        """
        权限编辑
        """
        pid = int(self.get_argument('id'))
        perm = PermService().read_perm_byid(pid)
        all_res_acts = ResActionService().read_all_resacts()
        #根据权限id获取对应的“资源操作code”列表
        _, cur_ract_codes = PermService().get_perm_act_codes(pid)
        #resources = self.filter_resource_query(Resource.mgr().Q())
        resources = ResourceService().read_all_resources()
        res_ractions= ResActionService().get_ractions_byresid(perm.resource_id)

        # 权限资源、属性， liugang 不再需要获取perm_attr
        #perm_attr = PermService().get_conf_data(perm, perm.resource_id)
        perm_attr = {}

        self.render('user/perm/edit.html',
                    target_tab=self.target_tab,
                    perm=perm,
                    sub_systems=self.get_subsystems(),
                    resources=resources,
                    all_res_acts=all_res_acts,
                    cur_ract_codes=cur_ract_codes,
                    res_ractions=res_ractions,
                    perm_attr=perm_attr)

    def delete(self):
        """
        权限删除
        """
        pid = int(self.get_argument('id'))
        PermService().check_and_delete(pid)
        self.json2dwz('200', 'forward', self.target_tab, forward_url='perm/list')

    def conf(self):
        """
        根据资源ID生成该权限的配置数据html片段

        perm_id = int(self.get_argument('perm_id', 0))
        resource_id = int(self.get_argument('resource_id', 0))
        perm = Perm.mgr().one(perm_id)
        self.render('user/perm_conf.html',
                    perm_attr=self.get_conf_data(perm, resource_id))
        """
        self.render('user/perm/conf.html', perm_attr={})

    def get_res_ractions(self):
        """
        根据资源ID生成该资源操作编码数据html片段
        """
        perm_id = self.get_argument_int('perm_id', 0)
        cur_ract_codes = []
        if perm_id:
            _, cur_ract_codes = PermService().get_perm_act_codes(perm_id)

        resource_id = self.get_argument_int('resource_id', 0)
        res_ractions= ResActionService().get_ractions_byresid(resource_id)

        self.render('user/perm/res_ractions.html',
                    res_ractions=res_ractions,
                    cur_ract_codes=cur_ract_codes)
