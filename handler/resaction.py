#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源操作管理
"""
import json
from conf.settings import E_RES_ACTION_CODE_EXIST
from handler.base import BaseHandler
from service.resaction import ResActionService
from model.user import ResRaction


class ResActionHandler(BaseHandler):
    """
    资源操作管理Handler
    """
    def list(self):
        """
        资源操作查询并显示列表
        """
        name = self.get_argument('name', '')
        code = self.get_argument('code', '')
        page = self.get_argument_int('pageNum', 1)
        psize = self.get_argument_int('numPerPage', 20)
        orderby = self.get_argument('orderby', 'CODE ASC')

        params = {
            'name': name,
            'code': code,
            'page': page,
            'psize': psize,
            'orderby': orderby,
        }
        code, res = ResActionService().get_list(params)

        self.render('user/res_action/list.html',
                    target_tab=self.target_tab,
                    param=params,
                    count=res['count'],
                    res_action_list=res['list'])

    def save(self):
        """
        资源操作保存
        """
        res_act_id = self.get_argument_int('id', 0)
        name = self.get_argument('name')
        code = self.get_argument('code')

        raction_info = {
            'id': res_act_id,
            'name': name,
            'code': code,
            'cur_username': self.current_user['name'],
        }

        code, res = ResActionService().save(raction_info)
        if code == 0:
            self.json2dwz('200', 'closeCurrent', self.target_tab, msg='保存成功!')

        msg = ''
        if code == E_RES_ACTION_CODE_EXIST:
            msg = '操作编码已经存在，请检查'
            self.json2dwz('300', '', msg=msg)

    def add(self):
        """
        资源操作增加
        """
        self.render('user/res_action/add.html',
                    target_tab=self.target_tab)

    def edit(self):
        """
        资源操作编辑
        """
        res_act_id = self.get_argument_int('id')
        res_act_info = ResActionService().read_resact_obj_byid(res_act_id)
        self.render('user/res_action/edit.html',
                    target_tab=self.target_tab,
                    res_act_info=res_act_info)

    def delete(self):
        """
        资源操作删除
        """
        res_act_id = self.get_argument_int('id')
        ResActionService().delete(res_act_id)
        self.json2dwz('200', 'forward', self.target_tab, forward_url='raction/list')

    def ref(self):
        """
        根据指定res_id获得资源操作code
        """
        res_id = int(self.get_argument('res_id', 0))
        flag = int(self.get_argument('flag', 0))
        if res_id:
            query = ResRaction.mgr().Q().filter(res_id=res_id)

        res = []
        if flag == 1:
            res.append(['', '不限'])
        elif flag == 2:
            res.append(['', '无'])
        for i in query:
            res.append([i.code, i.ract.name])
        self.write(json.dumps(res))
