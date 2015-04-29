#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户权限服务
"""
from conf.settings import E_PERM_EXIST
from conf.settings import E_SUCC
from model.user import Perm, PermAttr, PermRaction, Resource


class PermService(object):
    """
    用户权限服务
    """
    def get_list_objects(self, params):
        """
        获取列表，通过传入参数可实现搜索并获得权限对象query合集

        :param params: {
            'perm_id': perm_id,
            'name': name,
            'page': page,
            'psize': psize,
            'orderby': orderby
        }
        :return: 状态码， 查询的组织对象query合集， 不是返回dict
        """
        page, psize, orderby = params['page'], params['psize'], params['orderby']
        query = Perm.mgr().Q()
        if params['perm_id']:
            query.filter(id=params['perm_id'])
        if params['name']:
            query.extra("name LIKE '%%%s%%'" % params['name'])

        count = query.count()
        if count == 0:
            return E_SUCC, {'count': 0, 'perm_list': []}

        if orderby:
            tmp_orderby = orderby.split(' ')
            query = query.orderby(tmp_orderby[0], tmp_orderby[1])
        else:
            query = query.orderby('ID', 'DESC')

        perm_list = query.set_limit((page - 1) * psize, psize)

        return E_SUCC, {'count': count, 'perm_list': perm_list}

    def check_and_save(self, params):
        """
        检查输入信息并保存

        :param params: {
            'perm_id':perm_id,
            'name':name,
            'resource':resource,
            'resource_id':resource_id,  #资源ID
            'new_ract_codes':资源操作code列表,
            'perm_attr':perm_attr  #权限的资源、属性信息
        }
        :return: 状态码， 用户信息 or None
        """
        name, perm_id = params['name'], params['perm_id']
        perm = Perm.mgr().Q().filter(name=name)[0]
        if perm and perm_id != perm.id:
            return E_PERM_EXIST, None

        perm_info = {
            'id': params['perm_id'],
            'name': params['name'],
            'resource_id': params['resource_id']
        }

        code, res_perm = self.save(perm_info)
        if code == E_SUCC:
            self.save_perm_attr(res_perm['id'], params['perm_attr'])
            self.save_perm_res_actions(res_perm['id'], params['new_ract_codes'])

        return code, res_perm

    def save(self, perm_info):
        """
        保存perm的基本字段信息

        :param perm_info dict:
        :return: 状态码， perm信息
        """
        if perm_info['id']:
            perm = Perm.mgr(ismaster=True).one(perm_info['id'])
        else:
            perm = Perm.new()

        del perm_info['id']

        for k in perm_info:
            perm[k] = perm_info[k]

        perm.save()
        return E_SUCC, dict(perm)

    def save_perm_attr(self, perm_id, perm_attr):
        """
        保存或更新用户对应的角色信息

        :param user_id: 用户ID
        :param perm_attr: 权限属性列表
        :return:状态码，None
        """
        for i in perm_attr:
            pattr = PermAttr.mgr(ismaster=1).Q().filter(perm_id=perm_id, attr_name=i)[0]
            if pattr:
                pattr.attr_val = perm_attr[i]
            else:
                pattr = PermAttr.new()
                pattr.perm_id, pattr.attr_name, pattr.attr_val = perm_id, i, perm_attr[i]
            pattr.save()
        for i in PermAttr.mgr(ismaster=1).Q().filter(perm_id=perm_id):
            if i.attr_name not in perm_attr:
                i.delete()
        return E_SUCC, None

    def get_user_perm(self, perm_id):
        """
        获取权限信息
        :param perm_id: 权限ID
        :return:
        """
        return Perm.mgr().one(perm_id)

    def get_user_perm_byids(self, perm_ids):
        """
        根据id获取权限数据
        :param perm_ids:
        :return:
        """
        extra_sql = "id in(%s)" % (",".join([str(i) for i in perm_ids]))
        return Perm.mgr().Q().extra(extra_sql).query()

    def get_system_perms(self):
        """
        获取不同系统的权限列表

        :return:[{
                'sub_sys_id': '系统ID',
                'sub_sys_name': '系统名称',
                'perm_list': [
                {该系统下的权限信息},
                ...,
                ]

            },...
        ]
        """
        #all_perms = self.filter_perm_query(Perm.mgr().Q())
        pass

    def save_perm_res_actions(self, perm_id, new_ract_codes):
        """
        保存权限和“资源操作code”的关系

        :param perm_id: 权限ID
        :param new_ract_codes: 新的资源操作code列表
        :return: E_SUCC, None
        """
        _, cur_ract_codes = self.get_perm_act_codes(perm_id)
        for i in [j for j in cur_ract_codes if j not in new_ract_codes]:
            pra = PermRaction.mgr(ismaster=1).Q().filter(perm_id=perm_id, ract_code=i)[0]
            if pra:
                pra.delete()
        for i in [j for j in new_ract_codes if j not in cur_ract_codes]:
            pra = PermRaction.new()
            pra.perm_id, pra.ract_code = perm_id, i
            pra.save()

        return E_SUCC, None

    def get_perm_act_codes(self, perm_id):
        """
        根据权限id获取对应的“资源操作code”

        :param perm_id: 权限ID
        :return: 业务码，“资源操作code”列表
        """
        res = [i.ract_code for i in PermRaction.mgr().Q().filter(perm_id=perm_id)]
        return E_SUCC, res

    @staticmethod
    def get_conf_data(perm, resource_id):
        """
        取得权限的配置数据

        :param perm：权限对象
        :param resource_id: 资源ID
        :return: E_SUCC, 权限属性dict
        """
        resource = Resource.mgr().one(resource_id)
        all_attrs = []
        if resource:
            if resource.attr:
                all_attrs = [i for i in resource.attr.split(':') if i]
        if perm:
            perm_attr_list = PermAttr.mgr().Q().filter(perm_id=perm.id)
            _perm_attr = dict([(i.attr_name, i.attr_val) for i in perm_attr_list])
        else:
            _perm_attr = {}
        perm_attr = {}
        for i in all_attrs:
            perm_attr[i] = _perm_attr.get(i, '')
        return E_SUCC, perm_attr

    def read_all_perms(self):
        """
        获取所有的权限

        :return: perm对象合集
        """
        return Perm.mgr().Q()

    def read_perm_byid(self, perm_id, ismaster=False):
        """
        根据id获取权限信息

        :param perm_id: 权限ID
        :param ismaster: 是否从主库获取数据
        :return: 权限记录对象
        """
        return Perm.mgr(ismaster=ismaster).one(perm_id)

    def check_and_delete(self, perm_id):
        """
        检查并删除权限, 如果该权限和 正常用户有关联，则不能删除

        :param org_id: 组织ID
        :return: E_SUCC or E_ORG_HAS_USERS, NONE
        """
        #罗成虎：判断是否有关联关系

        self.delete(perm_id)

        return E_SUCC, None

    def delete(self, perm_id):
        """
        删除权限

        :param perm_id: 权限ID
        :return: E_SUCC, NONE
        """
        perm = self.read_perm_byid(perm_id, ismaster=True)
        #未使用软删除， 1启用2禁用3删除
        perm.delete()

        return E_SUCC, None
