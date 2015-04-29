#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
登陆认证
"""
from conf.settings import (E_SUCC, E_USER_EXISTED, E_USER_EMAIL_EXIST,
                           E_USER_NOT_EXIST, E_USER_PHONE_EXIST)

from model.user import User
from model.user import UserRole
from service.org import OrganizationService


class UserService(object):
    """
    用户服务
    """
    def get_list_objects(self, params):
        """
        获取岗位列表，通过传入参数可实现搜索并获得用户对象query合集

        :param params: {
            "user_id": user_id,
            "name": name,
            "real_name": real_name,
            "phone": phone,
            "org_id": org_id,
            "page": page,
            "psize": psize,
            "orderby": orderby,
        }
        :return: 状态码， 查询的用户对象query合集， 不是返回dict
        """
        page, psize, orderby = params["page"], params["psize"], params["orderby"]
        #query = User.mgr().Q().filter(status=1)
        query = User.mgr().Q() #不过滤status
        if params["user_id"]:
            query.filter(id=params["user_id"])
        if params["phone"]:
            query.filter(phone=params["phone"])
        if params["name"]:
            query.extra("name LIKE '%%%s%%'" % params["name"])
        if params["real_name"]:
            query.extra("real_name LIKE '%%%s%%'" % params["real_name"])
        if params["org_id"]:
            org_list = OrganizationService().get_orgs_child(params["org_id"])
            query.extra("org_id in (%s)" % (",".join([str(i.id) for i in org_list])))

        count = query.count()
        if count == 0:
            return E_SUCC, {"count": 0, "user_list": []}

        if orderby:
            tmp_orderby = orderby.split(" ")
            query = query.orderby(tmp_orderby[0], tmp_orderby[1])
        else:
            query = query.orderby("ID", "DESC")
        list_query = query.set_limit((page - 1) * psize, psize)

        user_list = list_query

        #user_list = query.query()
        #return E_SUCC, {"count": count, "list": user_list}
        return E_SUCC, {"count": count, "user_list": user_list}


    def get_user_byid(self, uid):
        """
        根据uid获取用户信息
        :param uid: 用户ID
        :return: user
        """
        res = User.mgr().Q().filter(id=uid, status=1).query()
        return res[0] if res else None

    def get_user_byjlb_id(self, jlb_uid):
        """
        根据近邻宝uid获取用户信息
        :param jlb_uid: 近邻宝UID
        :return: user
        """
        res = User.mgr().Q().filter(jlb_uid=jlb_uid, status=1).query()
        return res[0] if res else None

    def read_user_obj_byid(self, uid, ismaster=False):
        """
        根据用户ID读取信息
        :param uid: 用户ID
        :return: 用户对象
        """
        return User.mgr(ismaster=ismaster).one(uid)

    def check_and_save(self, params):
        """
        检查输入信息并保存

        :param params: {
            "user_id":user_id,
            "name":name,
            "real_name":real_name,
            "passwd":passwd,
            "is_root":is_root,
            "is_staff":is_staff,
            "org_id":org_id,
            "position_id":position_id,
            "staff_no":staff_no,
            "email":email,
            "phone":phone,
            "status":status,
            "role_ids":role_ids,
            "new_role_ids":new_role_ids,
            "cur_user_name": 当前用户名称,
        }
        :return: 状态码， 用户信息 or None
        """
        user_id = params["user_id"]

        if not user_id:
            code, _ = self.check_user_info(params)
            if code != E_SUCC:
                return code, None

        if not params["email"]:
            params["email"] = "%s@test.com" % params["phone"]

        user_info = {
            "id": params["user_id"],
            "name": params["name"],
            "real_name": params["real_name"],
            "passwd": params["passwd"],
            "is_root": params["is_root"],
            "is_staff": params["is_staff"],
            "org_id": params["org_id"],
            "position_id": params["position_id"],
            "staff_no": params["staff_no"],
            "email": params["email"],
            "phone": params["phone"],
            "status": params["status"],
            "update_user": params["cur_user_name"],
        }
        if not user_id:
            user_info["create_user"] = params["cur_user_name"]

        code, user = self.save(user_info)
        if code == E_SUCC:
            #保存用户和角色之间的关系
            self.save_user_roles(user['id'], params['new_role_ids'])
            self.save_user_roles(user["id"], params["new_role_ids"])

        return code, user

    def check_user_info(self, user_info):
        """
        检查用户信息是否有效， 如name是否重复，phone是否存在

        :param user_info: 字典信息
        :return: 状态码, None
        """
        user = User.mgr().Q().filter(name=user_info["name"])[0]
        if user and user_info["user_id"] != user.id:
            return E_USER_EXISTED, None

        user = User.mgr().Q().filter(email=user_info["email"])[0]
        if user and user_info["user_id"] != user.id:
            return E_USER_EMAIL_EXIST, None

        user = User.mgr().Q().filter(phone=user_info["phone"])[0]
        if user:
            return E_USER_PHONE_EXIST, None

        return E_SUCC, None

    def save(self, user_info):
        """
        保存用户的基本字段信息

        :param user_info dict:
        :return: 状态码， 用户信息
        """
        user_id = user_info["id"]
        if user_id:
            user = User.mgr(ismaster=True).one(user_id)
            if not user:
                return E_USER_NOT_EXIST, None
        else:
            user = User.new()
        del user_info["id"]

        for k in user_info:
            user[k] = user_info[k]

        user.save()
        return E_SUCC, dict(user)

    def delete(self, user_id):
        """
        删除用户

        :param user_id: 用户ID
        :return:E_SUCC, None
        """
        user = User.mgr(ismaster=1).one(user_id)
        user.status = 0
        user.save()
        return E_SUCC, None

    def save_user_roles(self, user_id, new_role_ids):
        """
        保存或更新用户对应的角色信息

        :param user_id: 用户ID
        :param new_role_ids: 角色ids列表
        :return:状态码，None
        """
        # 更新角色列表
        cur_roles = [i.role_id for i in UserRole.mgr().Q().filter(uid=user_id)]
        for i in [j for j in cur_roles if j not in new_role_ids]:
            urole = UserRole.mgr(ismaster=1).Q().filter(uid=user_id, role_id=i)[0]
            if urole:
                urole.delete()
        for i in [j for j in new_role_ids if j not in cur_roles]:
            urole = UserRole.new()
            urole.uid, urole.role_id = user_id, i
            urole.save()

        return E_SUCC, None

    def login(self, name, passwd):
        """
        进行登录名、密码验证

        :param name:name
        :param passwd:密码
        :return: user或者None
        """
        user = User.mgr().Q().filter(name=name)[0] or User.mgr().Q().filter(phone=name)[0]
        if user and User().check_passwd(user.passwd, passwd):
            return user
        return None
