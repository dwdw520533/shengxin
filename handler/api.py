#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
内部系统API
"""
from handler.base import BaseHandler
from conf.settings import E_SUCC, E_RESRC, E_USER_NOT_EXIST
from model.user import User
from model.old_user import User as OldUser
from service.user import UserService
from service.org import OrganizationService


class ApiHandler(BaseHandler):
    """
    内部系统API
    """
    def parse_module(self, module):
        """
        切分uri, 分成模块: /auth/{mod}/{submod} --> mod_sub
        """
        mod, sub = "", ""
        if module:
            arr = module.split("/")
            if len(arr) >= 3:
                mod, sub = arr[1], arr[2]
            elif len(arr) >= 2:
                mod = arr[1]
        return '%s__%s'%(mod, sub) if sub else mod

    def get(self, module):
        """
        预处理get: 验证、分析uri、调用uri对应的方法、返回处理结果
        """
        module = self.parse_module(module)
        if module in ('get', 'post'):
            module += '_'
        method = getattr(self, module or 'index')
        if method:
            code, res = method()
        else:
            code, res = E_RESRC, None
        self.send_json(res, code)

    def post(self, module):
        """
        预处理post: 验证、分析uri、调用uri对应的方法、返回处理结果
        """
        module = self.parse_module(module)
        if module in ('get', 'post'):
            module += '_'
        method = getattr(self, module or 'index')
        if method:
            code, res = method()
        else:
            code, res = E_RESRC, None
        self.send_json(res, code)

    def user__getbyid(self):
        """
        根据用户ID获取用户数据
        """
        uid = int(self.get_argument('uid'))
        user = UserService().get_user_byid(uid)
        if not user:
            return E_USER_NOT_EXIST, None

        return E_SUCC, user

    def user__getbyid_old(self):
        """
        根据用户ID获取用户数据
        """
        uid = int(self.get_argument('uid'))
        user = OldUser.mgr().one(uid)
        if not user:
            return E_USER_NOT_EXIST, None

        return E_SUCC, user

    def user__getmulti(self):
        """
        根据UID列表件获取用户
        """
        # 获取参数
        uid_list = self.get_argument('uid_list')
        sn = self.get_argument('sn', "")

        res = {}
        for i in User.mgr().Q().extra("%s in (%s)" %
                                      ("jlb_uid" if sn else "id", uid_list)):
            res[i.jlb_uid if sn else i.id] = i
        return E_SUCC, res

    def org__search(self):
        """
        根据组织名搜索组织列表
        """
        name = self.get_argument('name', "")
        org_id = int(self.get_argument('id', 0) or 0)

        org_id_list = []
        if org_id:
            org_list = OrganizationService().get_orgs_child(org_id)
            org_id_list = [i["id"] for i in org_list]

        return E_SUCC, OrganizationService().get_orgs_byname(name, org_id_list)

    def org__list(self):
        """
        获取组织列表
        :return:
        """
        org_id = int(self.get_argument('id', 0) or 0)
        if org_id:
            org_list = OrganizationService().get_orgs_child(org_id)
        else:
            org_list = OrganizationService().read_all_orgs()

        for i in org_list:
            i["full_name"] = i.full_name

        return E_SUCC, org_list

    def org__detail(self):
        """
        获取组织信息
        """
        id = self.get_argument("id")
        org = OrganizationService().read_org_byid(id)
        org["full_name"] = org.full_name
        return E_SUCC, org

    def user__getbyphone(self):
        """
        根据用户手机号获取用户数据
        """
        phone = int(self.get_argument('phone'))
        user = User.mgr(ismaster=True).Q().filter(phone=phone)[0]
        if not user:
            return E_USER_NOT_EXIST, None

        user.status = 1
        user.save()

        return E_SUCC, user

    def org__get_org_page(self):
        """
        根据组织名搜索组织列表(分页)
        """
        name = self.get_argument('name', "")
        org_id = int(self.get_argument('id', 0) or 0)
        page = int(self.get_argument('page', 1) or 1)
        psize = int(self.get_argument('psize', 20) or 20)

        org_id_list = []
        if org_id:
            org_list = OrganizationService().get_orgs_child(org_id)
            org_id_list = [i["id"] for i in org_list]

        count, result = OrganizationService().get_org_page(name, page, psize, org_id_list)
        return E_SUCC, {
            "count": count,
            "list": self._format_org_list(result)
        }

    def org__get_org_multi_page(self):
        """
        根据组织ID串获取多个组织信息
        """
        name = self.get_argument('name', "")
        org_ids = self.get_argument('org_ids')
        page = int(self.get_argument('page', 1) or 1)
        psize = int(self.get_argument('psize', 20) or 20)

        count, result = OrganizationService().get_org_page(name,
                                                           page,
                                                           psize,
                                                           org_ids.split(","))
        return E_SUCC, {
            "count": count,
            "list": self._format_org_list(result)
        }

    def _format_org_list(self, org_list):
        """
        格式化组织列表
        :param org_list: 组织list
        :return:list
        """
        if not org_list:
            return []

        result = []
        for i in org_list:
            parent_org = OrganizationService().read_org_byid(i["parent_id"])
            info = {
                "id": i["id"],
                "name": i["name"],
                "parent_id": i["parent_id"],
                "parent_name": parent_org.full_name if parent_org else "无",
                "create_time": i["create_time"]
                }
            result.append(info)
        return result