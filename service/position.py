#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
岗位
"""
from model.user import Position, PositionRole, User
from conf.settings import (E_SUCC, E_POSITION_EXIST,
                           E_POSITION_NOT_EXIST, E_POSITION_HAS_USERS,
                           E_POSITION_DO_BIND_USERS)


class PositionService(object):
    """
    岗位服务
    """
    def get_list(self, params):
        """
        获取岗位列表，通过传入参数可实现搜索并获得列表

        :param params dict:
        :return: E_SUCC, {'count': count, 'list': position_list}
        """
        page, psize, orderby = params['page'], params['psize'], params['orderby']
        query = Position.mgr().Q()
        #todo 待核实， 是否需要查询某个组织下的”所有“子组织包含的岗位
        if params['organization_id']:
            query.filter(organization_id=params['organization_id'])
        if params['name']:
            query.extra("name LIKE '%%%s%%'" % params['name'])
        if params['status']:
            query.filter(status=params['status'])

        count = query.count()
        if count == 0:
            return E_SUCC, {'count': 0, 'list': []}

        query = query.set_limit((page - 1) * psize, psize)
        if orderby:
            tmp_orderby = orderby.split(' ')
            query = query.orderby(tmp_orderby[0], tmp_orderby[1])
        else:
            query = query.orderby('id', 'DESC')

        position_list = query.query()

        return E_SUCC, {'count': count, 'list': position_list}

    def save(self, params):
        """
        创建或更新岗位信息

        :param params: dict{
            'position_id': 组织id,
            'name': name,
            'organization_id': organization_id,
            'note': note,
            'status': status,
            'cur_username': 当前用户名称,
            'new_roles': 新角色id的列表,
        }
        :return: 业务码，岗位信息
        """
        pos_info = {
            'id': params['position_id'],
            'name': params['name'],
            'organization_id': params['organization_id'],
            'note': params['note'],
            'status': params['status'],
            'update_user': params['cur_username'],
        }
        if not params['position_id']:
            pos_info['create_user'] = params['cur_username']

        if params['position_id']:
            #禁用或删除前， 检查是否有绑定用户。 有， 则不能操作
            is_bind = False
            if params['status'] in (2, 3) and params['position_id']:
                is_bind = self.is_bind_users(params['position_id'])
            if is_bind:
                return E_POSITION_DO_BIND_USERS, None

        #是否已存在同一个岗位， 有，则不能保存
        is_pos = False
        if params['organization_id'] \
                and not params['position_id'] \
                and params['name']:
            is_pos = self.is_pos_exist(params['organization_id'],
                                       params['name'])
        if is_pos:
            return E_POSITION_EXIST, None

        code, pos = self.save_baseinfo(pos_info)

        if code == E_SUCC:
            #保存岗位和角色之间的关系
            self.save_pos_roles(pos['id'], params['new_roles'])

        return code, dict(pos)

    def is_bind_users(self, position_id):
        """
        检查岗位是否有绑定用户

        :param position_id
        :return: True or False
        """
        query = User.mgr().Q().filter(position_id=position_id)
        query.filter(status=1)
        return True if query.count() else False

    def is_pos_exist(self, org_id, pos_name):
        """
        检查岗位是否有绑定用户

        :param org_id 组织id
        :param pos_id 岗位名称
        :return: True or False
        """
        query = Position.mgr().Q().filter(organization_id=org_id,
                                          name=pos_name)
        return True if query.count() else False

    def save_baseinfo(self, pos_info):
        """
        保存岗位的基本字段信息

        :param pos_info dict:
        :return: 状态码， 岗位信息
        """
        position_id = pos_info['id']
        if position_id:
            pos = self.read_position_byid(position_id, ismaster=True)
            if not pos:
                return E_POSITION_NOT_EXIST, None
        else:
            pos = Position.new()
        del pos_info['id']

        for k in pos_info:
            pos[k] = pos_info[k]

        pos.save()
        return E_SUCC, dict(pos)

    def save_pos_roles(self, pos_id, role_ids):
        """
        保存或更新岗位对应的角色信息

        :param pos_id: 岗位ID
        :param role_ids: 角色ids列表
        :return:状态码，None
        """
        cur_roles = [i.role_id for i in PositionRole.mgr().Q().filter(position_id=pos_id)]
        for i in [j for j in cur_roles if j not in role_ids]:
            posr = PositionRole.mgr(ismaster=1).Q().filter(position_id=pos_id, role_id=i)[0]
            if posr:
                posr.delete()
        for i in [i for i in role_ids if i not in cur_roles]:
            posr = PositionRole.new()
            posr.position_id, posr.role_id = pos_id, i
            posr.save()

        return E_SUCC, None

    def set_status(self, position_id, status):
        """
        设置岗位的状态，

        :param position_id: 岗位ID
        :param status: 1启用, 2禁用, 3删除
        :return: 状态码，岗位信息
        """
        position = Position.mgr(ismaster=1).one(position_id)
        position.status = status
        position.save()

        return E_SUCC, position

    def read_position_byid(self, position_id, ismaster=False):
        """
        根据id获取岗位信息

        :param position_id: 岗位ID
        :param ismaster: 是否从主库获取数据
        :return: 岗位记录信息或者None
        """
        pos = Position.mgr(ismaster=ismaster).Q().filter(id=position_id)
        return pos[0]

    def read_positions_by_orgid(self, org_id, status=1, ismaster=False):
        """
        获取某个组织org_id下的岗位列表

        :param org_id: 组织ID
        :param status: 状态， 1启用, 2禁用, 3删除
        :param ismaster: 是否从主库获取数据
        :return: 岗位列表
        """
        query = Position.mgr(ismaster=ismaster).Q()
        res = query.filter(organization_id=org_id, status=status).query()
        return res

    def read_all_positions(self, status=1):
        """
        获取所有的岗位

        :param status: 状态
        :return: position对象合集
        """
        return Position.mgr().Q().filter(status=status)

    def get_roleids_byposid(self, pos_id):
        """
        获取所有的角色id列表

        :param pos_id: 岗位ID
        :return: role id列表或[]
        """
        role_ids = []
        for i in PositionRole.mgr().Q().filter(position_id=pos_id):
            role_ids.append(i.role_id)

        return role_ids

    def check_and_delete(self, pos_id):
        """
        检查并删除岗位, 如果该岗位中包含用户，则不能删除

        :param pos_id: 组织ID
        :return: 业务码， None
                 E_SUCC,
                 E_POSITION_HAS_USERS,
                 OPERSYS_CALL_API_FAILED,
                 OPERSYS_ORG_HAS_LOGIS
        """
        pos = self.read_position_byid(pos_id, ismaster=1)
        pos_users = self.read_users_byposid(pos_id, status=1)
        if len(pos_users) > 0:
            return E_POSITION_HAS_USERS, None

        pos.delete()
        return E_SUCC, None

    def read_users_byposid(self, pos_id, status=1, ismaster=False):
        """
        根据岗位ID读取用户信息合集
        :param pos_id: 岗位ID
        :param status: 状态

        :return: 用户合集字典
        """
        query = User.mgr(ismaster=ismaster).Q()

        return query.filter(position_id=pos_id, status=status).data()
