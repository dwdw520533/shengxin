#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
组织
"""
from service.context import Context
from model.user import Organization, User
from conf.settings import (E_SUCC, E_ORG_HAS_USERS,
                           CABZOO_API, OPERSYS_ORG_HAS_LOGIS,
                           OPERSYS_CALL_API_FAILED, E_ORG_EXIST,
                           E_ORG_NOT_EXIST)
from service.position import PositionService


class OrganizationService(object):
    """
    组织服务
    """
    CAB_API_ORG_HAS_LOGIS = CABZOO_API('opera/logis/has_depart_logis')

    def __init__(self):
        """
        初始化
        """
        self.ctx = Context.inst()

    def get_list_objects(self, params):
        """
        获取列表，通过传入参数可实现搜索并获得用户对象query合集

        :param params: {
            'org_id': org_id,
            'name': name,
            'parent_id': parent_id,
            'page': page,
            'psize': psize,
            'orderby': orderby
        }
        :return: 状态码， 查询的组织对象query合集， 不是返回dict
        """
        page, psize, orderby = params['page'], params['psize'], params['orderby']
        #query = Organization.mgr().Q().filter(status=1)
        query = Organization.mgr().Q().extra("status != 0")
        if params['org_id']:
            query.filter(id=params['org_id'])
        if params['name']:
            query.extra("name LIKE '%%%s%%'" % params['name'])
        if params['parent_id']:
            query.filter(parent_id=params['parent_id'])

        count = query.count()
        if count == 0:
            return E_SUCC, {'count': 0, 'org_list': []}

        if orderby:
            tmp_orderby = orderby.split(' ')
            query = query.orderby(tmp_orderby[0], tmp_orderby[1])
        else:
            query = query.orderby('ID', 'DESC')
        org_list = query.set_limit((page - 1) * psize, psize)

        return E_SUCC, {'count': count, 'org_list': org_list}

    def read_org_groupby_list(self):
        """
        获取所有groupby后的组织列表

        :return: {'parent_id':[CuswikiColumn,CuswikiColumn,....]}
        """
        col_dict = {}
        temp_list = Organization.mgr().Q().groupby('parent_id')
        for temp_col in temp_list:
            col_dict[temp_col['parent_id']] = self.read_col_bypid(temp_col['parent_id'])
        return E_SUCC, col_dict
    
    def read_col_bypid(self, parent_id):
        """
        根据父id获取组织

        :param parent_id: 父id
        :return: list
        """
        return Organization.mgr(ismaster=True).Q().filter(parent_id=parent_id)

    def read_org_byid(self, org_id, ismaster=False):
        """
        根据id获取组织
        :param org_id: 组织id
        :return: model
        """
        return Organization.mgr(ismaster=ismaster).one(org_id)

    def read_all_orgs(self, status=1):
        """
        获取所有的组织，不再考虑根据用户权限过滤组织，
        filter_org_query方法在base.py文件中

        :return: org对象合集
        """
        return Organization.mgr().Q().filter(status=status).data()

    def get_orgs_byname(self, name, id_list=None):
        """
        根据名称搜索组织列表
        """
        query = Organization.mgr().Q().filter(status=1)
        if name:
            query.extra("name LIKE '%%%s%%'" % name)
        if id_list:
            query.extra("id in (%s)" % (",".join([str(i) for i in id_list])))

        return [{'id': i.id, 'name': i.name} for i in query[:10]]

    def get_orgs_child(self, org_id):
        """
        根据组织ID 获取所有子组织
        :param org_id: 组织ID
        :return: list
        """
        org = OrganizationService().read_org_byid(org_id)
        org_list = [org, ]
        for i in org.children:
            org_list.append(i)

        return org_list

    def set_status(self, org_id, status):
        """
        设置组织的状态，

        :param org_id: 组织ID
        :param status: 1启用, 0禁用
        :return: 状态码，组织信息
        """
        org = Organization.mgr(ismaster=1).one(org_id)
        org.status = status
        org.save()

        return E_SUCC, org

    def check_and_delete(self, org_id):
        """
        检查并删除组织（部门）, 如果该部门或它的下级子部门中包含用户，则不能删除
        1、部门删除时，其对应的子部门也一并删除。
        2、部门删除时，如果部门下边有关联的员工，不允许删除。
        3、部门删除时，如果部门下边有关联的物流中心或者学校小区， 不允许删除。

        :param org_id: 组织ID
        :return: 业务码， None
                 E_SUCC,
                 E_ORG_HAS_USERS,
                 OPERSYS_CALL_API_FAILED,
                 OPERSYS_ORG_HAS_LOGIS
        """
        org_users = self.get_users_by_orgid(org_id)
        if len(org_users) > 0:
            return E_ORG_HAS_USERS, None

        all_orgs = self.get_orgs_child(org_id)
        org_ids = ",".join([str(i.id) for i in all_orgs])
        #是否有关联的物流中心或者学校小区
        res = self.ctx.send_request(self.CAB_API_ORG_HAS_LOGIS, {
            "org_ids": org_ids
        })
        if res['code'] != E_SUCC:
            return OPERSYS_CALL_API_FAILED, None

        if int(res.get('body', 0)) == 1:
            return OPERSYS_ORG_HAS_LOGIS, None

        self.delete(org_id)
        return E_SUCC, None

    def get_users_by_orgid(self, org_id):
        """
        根据组织ID获取该组织、以及所有子组织包含的用户列表

        :param org_id 组织ID
        :return: E_SUCC, 用户对象合集list or []
        """
        all_orgs = self.get_orgs_child(org_id)
        query = User.mgr().Q().filter(status=1)
        query.extra("org_id in (%s)" % (",".join([str(i.id) for i in all_orgs]))).data()

        return query

    def delete(self, org_id):
        """
        删除组织时,(前提是没有关联任何用户的情况)
        1 删除所有下属组织
        2 自动删除该组织（和下级组织）对应的岗位
        （model中， 删除岗位时通过before_delete删除 岗位对应的角色）

        :param org_id 组织ID
        :return: E_SUCC, None
        """
        all_orgs = self.get_orgs_child(org_id)
        for i in all_orgs:
            all_pos = PositionService().read_positions_by_orgid(i.id, ismaster=1)
            if all_pos:
                for j in all_pos:
                    pos = PositionService().read_position_byid(j['id'],
                                                               ismaster=1)
                    pos.delete()
            i.delete()

        return E_SUCC, None

    def check_and_save(self, params):
        """
        创建或更新组织信息（不再考虑组织被软删除的情况）

        :param params: dict{
            'org_id': org_id,
            'name': name,
            'status': status,
            'parent': parent,
            'cur_username': self.current_user['name'],
        }
        :return: 业务码，组织信息
        """
        parent, org_id = params['parent'], params['org_id']
        if not parent:
            parent_id, level = 0, 0
        else:
            level = parent.level + 1
            parent_id = params['parent_id']

        org = Organization.mgr().Q().filter(parent_id=parent_id,
                                            name=params['name'])[0]
        #新建、并且name已存在的情况
        if not org_id and org:
            return E_ORG_EXIST, None

        org_info = {
            'id': params['org_id'],
            'name': params['name'],
            'status': params['status'],
            'update_user': params['cur_username'],
            'level': level,
            'parent_id': parent_id
        }
        if not org_id:
            org_info['create_user'] = params['cur_username']

        code, org = self.save(org_info)

        return code, org

    def save(self, org_info):
        """
        保存组织的基本字段信息

        :param org_info dict:
        :return: 状态码， 组织信息
        """
        org_id = org_info['id']
        if org_id:
            org = self.read_org_byid(org_id, ismaster=True)
            if not org:
                return E_ORG_NOT_EXIST, None
        else:
            org = Organization.new()

        del org_info['id']

        for k in org_info:
            org[k] = org_info[k]

        org.save()
        return E_SUCC, dict(org)

    def get_org_page(self, name, page, psize, id_list=None):
        """
        根据名称搜索组织列表
        """
        query = Organization.mgr().Q().filter(status=1)
        if name:
            query.extra("name LIKE '%%%s%%'" % name)
        if id_list:
            query.extra("id in (%s)" % (",".join([str(i) for i in id_list])))

        count = query.count()
        query = query.set_limit((page-1)*psize, psize).orderby("id", 'ASC')

        return count, query.query()
