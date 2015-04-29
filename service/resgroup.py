#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
系统分组
'''
from model.user import ResGroup
from conf.settings import E_SUCC, E_RES_ACTION_NOT_EXIST

class ResGroupService(object):
    """
    系统分组服务
    """
    def get_list(self, params):
        """
        获取系统分组列表，通过传入参数可实现搜索并获得列表

        :param params dict:
        :return:
        """
        page, psize, orderby = params['page'], params['psize'], params['orderby']
        query = ResGroup.mgr().Q()
        if params['sub_sys_id']:
            query.filter(sub_sys_id=params['sub_sys_id'])
        if params['name']:
            query.extra("name LIKE '%%%s%%'" % params['name'])

        count = query.count()
        if count == 0:
            return E_SUCC, {'count': 0, 'list': []}

        query = query.set_limit((page - 1) * psize, psize)
        if orderby:
            tmp_orderby = orderby.split(' ')
            query = query.orderby(tmp_orderby[0], tmp_orderby[1])
        else:
            query = query.orderby('id', 'DESC')

        sysgroup_list = query.query()

        return E_SUCC, {'count': count, 'list': sysgroup_list}

    def delete(self, sys_group_id):
        """
        根据id删除系统分组 （是否软删除 status 1启用, 2禁用, 3删除）

        :param res_group_id: 系统分组ID
        return 状态码，None
        """
        res_group = ResGroup.mgr(ismaster=1).one(sys_group_id)
        #目前先使用软删除， 1启用2禁用3删除
        #res_group.delete()
        res_group.status = 3
        res_group.save()
        return E_SUCC, None

    def save(self, sg_info):
        """
        创建或更新系统分组

        :param sg_info: dict{
            'id': 系统分组ID,
            'name': name,
            'nick': nick,
            'sub_sys_id': sub_system的ID,
            'cur_username': 当前用户名称,
        }
        :return: 业务码，系统分组信息
        """
        if sg_info['id']:
            res_sg = self.read_resgroup_byid(sg_info['id'], ismaster=True)
            if not res_sg:
                return E_RES_ACTION_NOT_EXIST, None

            for k in sg_info:
                res_sg[k] = sg_info[k]
        else:
            sg_info['create_user'] = sg_info['cur_username']
            del sg_info['id']
            res_sg = ResGroup.new(sg_info)
        res_sg.save()

        return E_SUCC, dict(res_sg)

    def read_resgroup_byid(self, res_group_id, ismaster=False):
        """
        根据id获取系统分组信息

        :param res_group_id: 系统分组ID
        :param ismaster: 是否从主库获取数据
        return 系统分组信息或者None
        """
        res = ResGroup.mgr(ismaster=ismaster).Q().filter(id=res_group_id)
        return res[0]

    def read_resgroups_by_sysid(self, sys_id, status=1, ismaster=False):
        """
        根据sys_id获取”资源分组“查询对象合集

        :param sys_id: 系统ID
        :param status: 状态， 1启用, 2禁用, 3删除
        :param ismaster: 是否从主库获取数据
        return “资源分组”查询对象合集
        """
        query = ResGroup.mgr(ismaster=ismaster).Q()
        res = query.filter(sub_sys_id=sys_id, status=status)
        return res

    def read_all_res_groups(self):
        """
        获取所有的资源分组

        :return: 资源分组对象合集
        """
        return ResGroup.mgr().Q()
