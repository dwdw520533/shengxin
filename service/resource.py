#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源
"""
from model.user import (Resource, ResRaction)
from conf.settings import E_SUCC, E_RESOURCE_EXIST, E_RESOURCE_NOT_EXIST


class ResourceService(object):
    """
    资源服务
    """
    def get_list_objects(self, params):
        """
        获取资源对象列表

        :param params dict:{
            'resrc_id': resrc_id,
            'name': name,
            'group': group,
            'system_id': system_id,
            'page': page,
            'psize': psize,
            'orderby': orderby
        }
        :return: E_SUCC, {'count': count, 'list': res_list}
        其中role_list为查询的对象query合集
        """
        page, psize, orderby = params['page'], params['psize'], params['orderby']
        name, resrc_id, group = params['name'], params['resrc_id'], params['group']
        query = Resource.mgr().Q()

        if resrc_id:
            query.filter(id=resrc_id)
        if name:
            query.extra("name LIKE '%%%s%%'"%name)
        if group:
            query.filter(group=group)
        if params['system_id']:
            query.filter(system_id=params['system_id'])

        count = query.count()
        if count == 0:
            return E_SUCC, {'count': 0, 'list': []}

        if orderby:
            tmp_orderby = orderby.split(' ')
            query = query.orderby(tmp_orderby[0], tmp_orderby[1])
        else:
            query = query.orderby('id', 'DESC')

        res_list = query.set_limit((page - 1) * psize, psize)

        return E_SUCC, {'count': count, 'list': res_list}

    def check_and_save(self, params):
        """
        检查并保存资源信息

        :param params: dict{
            'resrc_id': resrc_id, 资源id
            'name': 资源英文名,
            'nick': 资源中文名
            'group': 分组,
            'system_id': system_id, 系统id
            'new_ract_codes': 资源操作code列表,
            'attr': attr
        }
        :return: 业务码，资源信息dict
        """
        name = params['name']
        system_id, group = params['system_id'], params['group']
        resrc = Resource.mgr().Q().filter(system_id=system_id,
                                          group=group,
                                          name=name)[0]
        if resrc and params['resrc_id'] != resrc.id:
            return E_RESOURCE_EXIST, None

        res_info = {
            'id': params['resrc_id'],
            'name': params['name'],
            'nick': params['nick'],
            'group': params['group'],
            'system_id': params['system_id'],
            'attr': params['attr'],
        }

        code, resource = self.save_baseinfo(res_info)
        if code == E_SUCC:
            #保存资源和“资源操作code”的关系
            self.save_res_and_ract(resource['id'], params['new_ract_codes'])

        return code, dict(resource)

    def save_baseinfo(self, res_info):
        """
        保存资源基本字段信息

        :param res_info dict:{
            'id': params['resrc_id'],
            'name': params['name'],
            'nick': params['nick'],
            'group': params['group'],
            'system_id': params['system_id'],
            'attr': params['attr'],
        }
        :return: 状态码， 资源信息dict
        """
        res_id = res_info['id']
        if res_id:
            res = self.read_res_obj_byid(res_id, ismaster=True)
            if not res:
                return E_RESOURCE_NOT_EXIST, None
        else:
            res = Resource.new()
            del res_info['id']

        for k in res_info:
            res[k] = res_info[k]

        res.save()
        return E_SUCC, dict(res)

    def get_res_act_codes(self, res_id):
        """
        根据资源id获取所有的“资源操作code”

        :param params:
        :return: 业务码，“资源操作code”列表
        """
        res = [i.ract_code for i in ResRaction.mgr().Q().filter(res_id=res_id)]
        return E_SUCC, res

    def save_res_and_ract(self, res_id, new_ract_codes):
        """
        保存资源和“资源操作code”的关系

        :param res_id: 资源ID
        :param new_ract_codes: 新的资源操作code列表
        :return:
        """
        _, cur_ract_codes = self.get_res_act_codes(res_id)
        for i in [j for j in cur_ract_codes if j not in new_ract_codes]:
            rra = ResRaction.mgr(ismaster=1).Q().filter(res_id=res_id, ract_code=i)[0]
            if rra:
                rra.delete()
        for i in [j for j in new_ract_codes if j not in cur_ract_codes]:
            rra = ResRaction.new()
            rra.res_id, rra.ract_code = res_id, i
            rra.save()

        return E_SUCC, None

    def read_resource_byid(self, res_id, ismaster=False):
        """
        根据获取ID资源信息

        :param res_id: 资源ID
        :return: 资源信息或None
        """
        res = Resource.mgr(ismaster=ismaster).Q().filter(id=res_id).query()
        return res[0]

    def read_res_obj_byid(self, res_id, ismaster=False):
        """
        根据ID获取资源对象

        :param res_id: 资源ID
        :return: 资源对象
        """
        return Resource.mgr(ismaster=ismaster).one(res_id)

    def read_all_resources(self):
        """
        获取所有的岗位

        :return: resource对象合集
        """
        return Resource.mgr().Q()

    def delete(self, res_id):
        """
        删除资源

        :param res_id: 资源ID
        :return: E_SUCC, NONE
        """
        resource = Resource.mgr(ismaster=1).one(res_id)
        #目前先使用软删除， 1启用2禁用3删除
        #resource.delete()
        resource.status = 3
        resource.save()
        return E_SUCC, None
