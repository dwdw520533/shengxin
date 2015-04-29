#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
用户-角色-权限关系服务
'''
from model.user import UserRole
from model.user import RolePerm


class RelationService(object):
    """
    用户-角色-权限关系服务
    """
    def get_user_role(self, uid):
        """
        获取用户角色关系
        :param uid:
        :return:
        """
        return UserRole.mgr().Q().filter(uid=uid).query()

    def get_role_perm(self, role_ids):
        """
        获取角色权限关系
        :param role_ids:
        :return:
        """
        query = RolePerm.mgr().Q()
        extra_sql = "role_id in (%s)" % (",".join([str(i) for i in role_ids]))
        return query.extra(extra_sql).query()
