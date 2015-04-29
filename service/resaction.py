#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
资源操作
'''
from model.user import ResAction, ResRaction
from conf.settings import (E_SUCC, E_RES_ACTION_NOT_EXIST,
                           E_RES_ACTION_CODE_EXIST)

class ResActionService(object):
    """
    资源操作服务
    """
    def get_list(self, params):
        """
        获取资源操作列表，通过传入参数可实现搜索并获得列表

        :param params dict:
        :return:
        """
        page, psize, orderby = params['page'], params['psize'], params['orderby']
        query = ResAction.mgr().Q()
        if params['name']:
            query.extra("name LIKE '%%%s%%'" % params['name'])
        if params['code']:
            query.extra("code LIKE '%%%s%%'" % params['code'])

        count = query.count()
        if count == 0:
            return E_SUCC, {'count': 0, 'list': []}

        query = query.set_limit((page - 1) * psize, psize)
        if orderby:
            tmp_orderby = orderby.split(' ')
            query = query.orderby(tmp_orderby[0], tmp_orderby[1])
        else:
            query = query.orderby('id', 'DESC')

        res_act_list = query.query()

        return E_SUCC, {'count': count, 'list': res_act_list}

    def delete(self, res_action_id):
        """
        根据id删除资源操作

        :param res_action_id: 资源操作ID
        return 状态码，None
        """
        raction = ResAction.mgr(ismaster=1).one(res_action_id)
        #直接硬删除。 不考虑使用软删除， 1启用2禁用3删除
        #liugang：直接删除时，1删除时是否考虑“资源”引用了这操作, 2 对应的关系是否也删除
        raction.delete()
        #raction.status = 3
        #raction.save()
        return E_SUCC, raction

    def save(self, raction_info):
        """
        创建或更新资源操作

        :param raction_info: dict{
            'id': 资源操作ID,
            'name': name,
            'code': code,
            'cur_username': 当前用户名称,
        }
        :return: 业务码，资源操作信息
        """
        res_act = self.read_raction_bycode(raction_info['code'], ismaster=True)
        if res_act and res_act['id'] != raction_info['id']:
            return E_RES_ACTION_CODE_EXIST, None

        if raction_info['id']:
            res_act = self.read_raction_byid(raction_info['id'], ismaster=True)
            if not res_act:
                return E_RES_ACTION_NOT_EXIST, None

            for k in raction_info:
                res_act[k] = raction_info[k]
        else:
            raction_info['create_user'] = raction_info['cur_username']
            del raction_info['id']
            res_act = ResAction.new(raction_info)
        res_act.save()

        return E_SUCC, dict(res_act)

    def read_raction_byid(self, res_act_id, ismaster=False):
        """
        根据id获取资源操作信息

        :param res_act_id: 资源操作ID
        :param ismaster: 是否从主库获取数据
        return 资源操作信息或者None
        """
        res = ResAction.mgr(ismaster=ismaster).Q().filter(id=res_act_id)
        return res[0]

    def read_raction_bycode(self, code, ismaster=False):
        """
        根据code获取资源操作信息

        :param code: 资源操作编码code
        :param ismaster: 是否从主库获取数据
        return 资源操作信息或者None
        """
        res = ResAction.mgr(ismaster=ismaster).Q().filter(code=code)
        return res[0]

    def set_status(self, res_act_id, status):
        """
        设置资源操作的状态，

        :param res_act_id: 资源操作ID
        :param status: 1启用, 2禁用, 3删除
        return 状态码，资源操作信息
        """
        raction = ResAction.mgr(ismaster=1).one(res_act_id)
        raction.status = status
        raction.save()

        return E_SUCC, raction

    def read_all_resacts(self):
        """
        获取所有的资源操作

        :return: 自由操作res_action对象合集
        """
        return ResAction.mgr().Q()

    def read_resact_obj_byid(self, res_act_id, ismaster=False):
        """
        根据id获取资源操作

        :param res_act_id: 资源操作ID
        :param ismaster: 是否从主库获取数据
        :return: 资源操作对象
        """
        return ResAction.mgr(ismaster=ismaster).one(res_act_id)

    def get_ractions_byresid(self, res_id):
        """
        根据res_id获取资源操作对象

        :param res_id: 资源ID
        :return: 资源操作对象合集list
        """
        rracts = ResRaction.mgr().Q().filter(res_id=res_id).data()
        res_racts = []
        for i in rracts:
            ract = self.read_raction_bycode(i.ract_code)
            res_racts.append(ract)

        return res_racts
