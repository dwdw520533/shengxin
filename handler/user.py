#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户管理
"""
from handler.base import BaseHandler
from conf.settings import (AUTH_CNF, E_SUCC,
                           E_USER_EXISTED, E_USER_EMAIL_EXIST,
                           E_CREATE_JLB_USER_FAILED, E_USER_PHONE_EXIST)
from model.user import UserRole
from service.user import UserService
from service.org import OrganizationService
from service.role import RoleService
from service.position import PositionService


class UserHandler(BaseHandler):
    """
    用户管理
    """
    def index(self):
        """
        用户管理菜单(depreciated)
        """
        if not self.current_user:
            self.redirect('/user/login')
        else:
            self.render('user/index.html')

    def list(self):
        """
        用户查询
        """
        user_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        real_name = self.get_argument('real_name', '')
        phone = self.get_argument('phone', '')
        org_id = int(self.get_argument('orgu.id', 0))
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        orderby = self.get_argument('orderby', 'ID DESC')
        params = {
            'user_id': user_id,
            'name': name,
            'real_name': real_name,
            'phone': phone,
            'org_id': org_id,
            'page': page,
            'psize': psize,
            'orderby': orderby,
        }
        #_, res = UserService().get_list_objects(self, params)
        _, res = UserService().get_list_objects(params)

        user_list = res.get('user_list', [])
        count = res.get('count', 0)
        page_count = (count + psize - 1) / psize
        #all_orgs = self.filter_org_query(Organization.mgr().Q())
        all_orgs = OrganizationService().read_all_orgs()

        self.render('user/user_list.html',
                    target_tab=self.target_tab,
                    name=name,
                    real_name=real_name,
                    org_id=org_id,
                    phone=phone,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    user_list=user_list,
                    all_org_list=all_orgs)

    def save(self):
        """
        保存用户
        """
        user_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        real_name = self.get_argument('real_name')
        passwd = self.get_argument('password', '')
        is_root = int(self.get_argument('is_root', 0))
        is_staff = int(self.get_argument('is_staff', 0))
        org_id = self.get_argument_int('org_u0.id', 0)
        position_id = self.get_argument_int('position_id', 0)
        staff_no = int(self.get_argument('staff_no', 0) or 0)
        email = self.get_argument('email', '')
        phone = self.get_argument('phone', '')
        status = self.get_argument_int('status', 1)
        role_ids = []
        for i in self.request.arguments:
            if i.startswith('role__'):
                role_ids.append(self.get_argument(i, ''))

        new_role_ids = [int(i) for i in role_ids if i]

        params = {
            'user_id':user_id,
            'name':name,
            'real_name':real_name,
            'passwd':passwd,
            'is_root':is_root,
            'is_staff':is_staff,
            'org_id':org_id,
            'position_id':position_id,
            'staff_no':staff_no,
            'email':email,
            'phone':phone,
            'status':status,
            'role_ids':role_ids,
            'new_role_ids':new_role_ids,
            'cur_user_name': self.current_user['name']
        }
        code, _ = UserService().check_and_save(params)
        if code == E_SUCC:
            self.json2dwz('200', 'closeCurrent', self.target_tab, forward_url='user/list')

        msg = ''
        if code == E_USER_EXISTED:
            msg = '用户[%s]已经存在' % name
        elif code == E_USER_EMAIL_EXIST:
            msg = 'email[%s]已经存在' % email
        elif code == E_USER_PHONE_EXIST:
            msg = '电话[%s]已经存在' % phone
        elif code == E_CREATE_JLB_USER_FAILED:
            msg = '自动创建近邻宝用户失败, 请联系技术人员!'
        else:
            msg = ''

        if msg:
            self.json2dwz('300', '', msg=msg)

    def add(self):
        """
        增加用户
        """
        #all_orgs = self.filter_org_query(Organization.mgr().Q())
        #all_roles = self.filter_role_query(Role.mgr().Q())
        all_orgs = OrganizationService().read_all_orgs()
        all_roles = RoleService().read_all_roles()
        all_options = PositionService().read_all_positions()
        self.render('user/user_add.html',
                    target_tab=self.target_tab,
                    all_orgs=all_orgs,
                    all_options=all_options,
                    all_roles=all_roles)

    def edit(self):
        """
        增加用户
        """
        uid = int(self.get_argument('id'))
        user = UserService().read_user_obj_byid(uid, ismaster=1)
        cur_roles = [i.role_id for i in UserRole.mgr().Q().filter(uid=uid)]
        #all_roles = self.filter_role_query(Role.mgr().Q())
        #all_orgs = self.filter_org_query(Organization.mgr().Q())
        all_orgs = OrganizationService().read_all_orgs()
        all_roles = RoleService().read_all_roles()
        all_options = PositionService().read_all_positions()
        cur_org_positions = PositionService().read_positions_by_orgid(user['org_id'])
        self.render('user/user_edit.html',
                    target_tab=self.target_tab,
                    user=user,
                    all_orgs=all_orgs,
                    cur_roles=cur_roles,
                    cur_org_positions=cur_org_positions,
                    all_options=all_options,
                    all_roles=all_roles)

    def detail(self):
        """
        用户详情
        """
        uid = int(self.get_argument('id'))
        user = UserService().read_user_obj_byid(uid, ismaster=1)
        cur_roles = [i.role_id for i in UserRole.mgr().Q().filter(uid=uid)]
        all_orgs = OrganizationService().read_all_orgs()
        all_roles = RoleService().read_all_roles()
        all_options = PositionService().read_all_positions()
        cur_org_positions = PositionService().read_positions_by_orgid(user['org_id'])
        self.render('user/user_detail.html',
                    target_tab=self.target_tab,
                    user=user,
                    all_orgs=all_orgs,
                    cur_roles=cur_roles,
                    cur_org_positions=cur_org_positions,
                    all_options=all_options,
                    all_roles=all_roles)

    def delete(self):
        """
        删除用户
        """
        uid = int(self.get_argument('id'))
        UserService().delete(uid)
        self.json2dwz('200', 'forward', self.target_tab, forward_url='user/list')

    def login(self):
        """
        登陆处理
        """
        next_url = self.get_argument('next', '/')
        if self.request.method == 'GET':
            if self.current_user:
                self.redirect(next_url)
                return
            self.render('user/login.html', next_url=next_url, error='')
        else:
            name = self.get_argument('name', '')
            passwd = self.get_argument('passwd', '')
            err_count = self.session[AUTH_CNF['login_errcnt']] or 0
            if err_count >= 3:
                self.render('user/login.html', next_url=next_url, error='密码错误超过3次, 被锁定')
            else:
                user = UserService().login(name, passwd)
                if not user:
                    err_count += 1
                    self.session.set(AUTH_CNF['login_errcnt'], err_count, 300)
                    retry_cnt = 3 - err_count
                    self.render('user/login.html',
                                next_url=next_url,
                                error='密码错误, 还有%s机会' % retry_cnt)
                else:
                    del self.session[AUTH_CNF['login_errcnt']]
                    self.session.save()
                    self._login(user['id'])
                    self.redirect(next_url)

    def logout(self):
        """
        登出
        """
        next_url = self.get_argument('next', '/')
        if self.request.method == 'GET':
            self._logout()
            self.redirect(next_url)

    def passwd__change(self):
        """
        修改密码
        """
        self.render('user/passwd_change.html')

    def passwd__save(self):
        """
        保存密码
        """
        old_passwd = self.get_argument('old_passwd')
        new_passwd = self.get_argument('new_passwd')
        msg = ''
        if self.current_user:
            user = UserService().read_user_obj_byid(self.current_user.id,
                                                    ismaster=True)
            if user and user.check_passwd(user.passwd, old_passwd):
                user.passwd = new_passwd
                user.save()
            else:
                msg = '密码错误'
        else:
            msg = '会话超时, 请重新登录'
        if not msg:
            self.json2dwz('200', 'closeCurrent', 'tab_user', forward_url='user/list',
                          msg='密码修改成功')
        else:
            self.json2dwz('300', 'closeCurrent', 'tab_user', forward_url='user/list',
                          msg=msg)

