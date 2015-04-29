#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源管理
"""

import json
from handler.base import BaseHandler
from model.user import Resource
from model.subsystem import SubSystem
from service.resource import ResourceService
from service.resaction import ResActionService
from service.resgroup import ResGroupService
from conf.settings import E_RESOURCE_EXIST


class ResourceHandler(BaseHandler):
    """
    资源管理Handler
    """
    def list(self):
        """
        资源查询
        """
        resrc_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        group = self.get_argument('group', '')
        system_id = int(self.get_argument('system_id', 0))
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        orderby = self.get_argument('orderby', 'ID DESC')

        params = {
            'resrc_id': resrc_id,
            'name': name,
            'group': group,
            'system_id': system_id,
            'page': page,
            'psize': psize,
            'orderby': orderby,
        }
        #res 返回的是对象的合集
        _, res = ResourceService().get_list_objects(params)
        resources = res.get('list', [])
        count = res.get('count', 0)
        page_count = (count + psize - 1) / psize
        all_systems = SubSystem.mgr().Q().data()

        self.render('user/resource/list.html',
                    target_tab=self.target_tab,
                    name=name,
                    group=group,
                    system_id=system_id,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    resources=resources,
                    all_systems=all_systems)

    def ref(self):
        """
        根据指定system_id获得资源列表
        """
        system_id = self.get_argument_int('system_id', 0)
        flag = int(self.get_argument('flag', 0))
        query = Resource.mgr().Q()
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

    def save(self):
        """
        资源保存
        """
        resrc_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        nick = self.get_argument('nick')
        group = self.get_argument('group', '')
        system_id = int(self.get_argument('system_id'))
        #attr = self.get_argument('attr', '')
        attr = ""  #属性字段不再需要 liugang

        new_ract_codes = []
        for i in self.request.arguments:
            if i.startswith('ract_code__'):
                new_ract_codes.append(self.get_argument(i, ''))

        params = {
            'resrc_id': resrc_id,
            'name': name,
            'nick': nick,
            'group': group,
            'system_id': system_id,
            'new_ract_codes': new_ract_codes,
            'attr': attr
        }

        code, _ = ResourceService().check_and_save(params)

        if code == 0:
            self.json2dwz('200', 'closeCurrent', self.target_tab, msg='保存成功!')

        if code == E_RESOURCE_EXIST:
            msg = '资源[%s]已经存在' % name
            self.json2dwz('300', '', msg=msg)
            return

    def add(self):
        """
        资源增加
        """
        all_systems = SubSystem.mgr().Q().data()
        all_res_acts = ResActionService().read_all_resacts()
        all_res_groups = ResGroupService().read_all_res_groups()

        self.render('user/resource/add.html',
                    target_tab=self.target_tab,
                    all_res_acts=all_res_acts,
                    all_res_groups=all_res_groups,
                    all_systems=all_systems)

    def edit(self):
        """
        资源编辑
        """
        resrc_id = int(self.get_argument('id'))
        resource = ResourceService().read_res_obj_byid(resrc_id)
        all_systems = SubSystem.mgr().Q().data()
        all_res_groups = ResGroupService().read_all_res_groups()
        _, cur_ract_codes = ResourceService().get_res_act_codes(resrc_id)
        all_res_acts = ResActionService().read_all_resacts()
        self.render('user/resource/edit.html',
                    target_tab=self.target_tab,
                    resource=resource,
                    cur_ract_codes=cur_ract_codes,
                    all_res_acts=all_res_acts,
                    all_res_groups=all_res_groups,
                    all_systems=all_systems)

    def delete(self):
        """
        资源删除
        """
        resrc_id = int(self.get_argument('id'))
        ResourceService().delete(resrc_id)
        self.json2dwz('200', 'forward', self.target_tab, forward_url='resource/list')

