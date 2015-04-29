#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统分组管理
"""
import json
from handler.base import BaseHandler
from service.resgroup import ResGroupService
from model.user import SubSystem


class ResGroupHandler(BaseHandler):
    """
    系统分组管理Handler
    """
    def list(self):
        """
        系统分组查询并显示列表
        """
        name = self.get_argument('name', '')
        sub_sys_id = self.get_argument_int('sub_sys_id', 0)
        page = self.get_argument_int('pageNum', 1)
        psize = self.get_argument_int('numPerPage', 20)
        orderby = self.get_argument('orderby', 'ID DESC')
        all_systems = SubSystem.mgr().Q().data()
        params = {
            'name': name,
            'page': page,
            'sub_sys_id': sub_sys_id,
            'psize': psize,
            'orderby': orderby,
        }
        code, res = ResGroupService().get_list(params)

        self.render('user/res_group/list.html',
                    target_tab=self.target_tab,
                    param=params,
                    count=res['count'],
                    all_systems=all_systems,
                    sub_sys_id=sub_sys_id,
                    sys_group_list=res['list'])

    def save(self):
        """
        系统分组保存
        """
        res_act_id = self.get_argument_int('id', 0)
        name = self.get_argument('name')
        nick = self.get_argument('nick')
        sub_sys_id = self.get_argument('sub_sys_id')

        res_group_info = {
            'id': res_act_id,
            'name': name,
            'nick': nick,
            'sub_sys_id': sub_sys_id,
            'cur_username': self.current_user['name'],
        }

        code, res = ResGroupService().save(res_group_info)

        if code == 0:
            self.json2dwz('200', 'closeCurrent', self.target_tab, msg='保存成功!')
        else:
            self.json2dwz('300', '', self.target_tab, msg='')

    def add(self):
        """
        系统分组增加
        """
        all_systems = SubSystem.mgr().Q().data()
        self.render('user/res_group/add.html',
                    target_tab=self.target_tab,
                    all_systems=all_systems)

    def edit(self):
        """
        系统分组编辑
        """
        sys_group_id = self.get_argument_int('id')
        all_systems = SubSystem.mgr().Q().data()
        sys_group_info = ResGroupService().read_resgroup_byid(sys_group_id)
        self.render('user/res_group/edit.html',
                    target_tab=self.target_tab,
                    all_systems=all_systems,
                    sys_group_info=sys_group_info)

    def delete(self):
        """
        系统分组删除
        """
        sys_group_id = self.get_argument_int('id')
        ResGroupService().delete(sys_group_id)
        self.json2dwz('200', 'forward', self.target_tab, forward_url='sysgroup/list')

    def ref(self):
        """
        根据指定sub_sys_id获取 资源分组列表
        """
        sub_sys_id = self.get_argument_int('sub_sys_id', 0)
        flag = self.get_argument_int('flag', 0)
        res = []
        if flag == 1:
            res.append(['', '不限'])
        elif flag == 2:
            res.append(['', '无'])

        res_list = ResGroupService().read_resgroups_by_sysid(sub_sys_id)
        for i in res_list:
            res.append([i.name, i.full_name])
        self.write(json.dumps(res))
