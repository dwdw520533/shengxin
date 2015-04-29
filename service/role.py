#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户角色服务
"""
from model.user import Role, RolePerm, Perm
from conf.settings import E_SUCC, E_ROLE_EXIST


class RoleService(object):
    """
    用户角色服务
    """
    def get_list_objects(self, params):
        """
        获取角色列表，通过传入参数可实现搜索并获得列表

        :param params dict:
        :return: E_SUCC, {'count': count, 'list': role_list}
        其中role_list为查询的对象query合集
        """
        page, psize, orderby = params['page'], params['psize'], params['orderby']
        name, role_id = params['name'], params['role_id']
        query = Role.mgr().Q()

        if role_id:
            query.filter(id=role_id)
        if name:
            query.extra("name LIKE '%%%s%%'" % name)

        count = query.count()
        if count == 0:
            return E_SUCC, {'count': 0, 'list': []}

        if orderby:
            tmp_orderby = orderby.split(' ')
            query = query.orderby(tmp_orderby[0], tmp_orderby[1])
        else:
            query = query.orderby('id', 'DESC')

        role_list = query.set_limit((page - 1) * psize, psize)

        return E_SUCC, {'count': count, 'list': role_list}

    def check_and_save(self, params):
        """
        检查并保存角色信息

        :param params: dict{
            'role_id': role_id,
            'name': name,
            'perm_ids': perm_ids列表
        }
        :return: 业务码，岗位信息
        """
        # 参数检查
        role = Role.mgr().Q().filter(name=params['name'])[0]
        if role and params['role_id'] != role.id:
            return E_ROLE_EXIST, None

        role_info = {
            'id': params['role_id'],
            'name': params['name']
        }

        code, role = self.save_baseinfo(role_info)
        if code == E_SUCC:
            #保存角色和权限之间的关系
            self.save_role_perms(role['id'], params['perm_ids'])

        return code, dict(role)

    def save_baseinfo(self, role_info):
        """
        保存角色基本字段信息

        :param role_info dict:
        :return: 状态码， 角色信息
        """
        role_id = role_info['id']
        if role_id:
            role = Role.mgr(ismaster=True).one(role_id)
        else:
            role = Role.new()
        role.name = role_info['name']
        role.save()
        return E_SUCC, dict(role)

    def save_role_perms(self, role_id, perm_ids):
        """
        保存角色和权限之间的关系

        :param role_id: 角色ID
        :param perm_ids: 权限ids列表
        :return:状态码，None
        """
        cur_perms = [i.perm_id for i in RolePerm.mgr().Q().filter(role_id=role_id)]
        new_perms = [int(i) for i in perm_ids]
        for i in [j for j in cur_perms if j not in new_perms]:
            rolep = RolePerm.mgr(ismaster=1).Q().filter(role_id=role_id, perm_id=i)[0]
            if rolep:
                rolep.delete()
        for i in [j for j in new_perms if j not in cur_perms]:
            rolep = RolePerm.new()
            rolep.role_id, rolep.perm_id = role_id, i
            rolep.save()

        return E_SUCC, None

    def read_role_byid(self, role_id, ismaster=False):
        """
        获取角色信息

        :param id:角色ID
        :return:角色对象
        """
        return Role.mgr(ismaster=ismaster).one(role_id)

    def get_user_role_byids(self, role_ids):
        """
        根据role_id获取角色数据

        :param role_ids:
        :return:
        """
        sql_where = "id in (%s)" % (",".join([str(i) for i in role_ids]))
        return Role.mgr().Q().extra(sql_where).query()

    def get_perms_byroleid(self, role_id):
        """
        本角色所拥有的所有权限

        :param role_id: 角色ID
        :return: Perm对象合集或[]
        """
        perms = []
        for i in RolePerm.mgr().Q().filter(role_id=role_id):
            perm = Perm.mgr().Q().filter(id=i.perm_id)[0]
            if perm:
                perms.append(perm)
        return perms

    def read_all_roles(self):
        """
        所有角色

        :return: role对象合集或[]
        """
        return Role.mgr().Q()

    def delete(self, role_id):
        """
        删除角色

        :param role_id: 角色ID
        :return: E_SUCC, NONE
        """
        role = self.read_role_byid(role_id, ismaster=True)
        #role没有status值标识是否删除
        role.delete()
        return E_SUCC, None
