#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
鉴权登陆接口, 供各个子系统调用
"""
import time
import urlparse
import tornado
from handler.base import BaseHandler
from conf.settings import E_SUCC, E_AUTH, E_RESRC, E_TIMEOUT, E_FORBID
from service.auth import AuthService
from service.user import UserService
from model.menu import Menu
from model.user import Organization, User


class AuthHandler(BaseHandler):
    """
    鉴权登陆接口Handler
    """
    def check(self):
        """
        权限、超时验证
        """
        key = self.get_argument('key').encode('utf-8')
        timestamp = int(self.get_argument('ts'))
        sign = self.get_argument('sign').encode('utf-8')
        verified = AuthService().verify(key, timestamp, sign)
        code = E_SUCC
        now = int(time.time())
        if not verified:
            code = E_AUTH
        elif (now - timestamp) > 2000:
            code = E_TIMEOUT
        return code

    def send_response(self, res, code):
        """
        根据content_type, 发送响应
        """
        cont_type = getattr(self, 'content_type', 'json')
        if cont_type == 'json':
            alt = self.get_argument('alt', "json")
            if alt == "json":
                self.send_json(res, code)
            elif alt == "jsonp":
                var = self.get_argument('callback', "jsonp2")
                self.send_json(res, code, var)
        elif cont_type == 'redirect':
            self.redirect(res)
        elif cont_type == 'text':
            self.write(str(res))
        else:
            raise tornado.web.HTTPError(404)

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
        code, res = self.check(), None
        if code == E_SUCC:
            if module in ('get', 'post'):
                module += '_'
            method = getattr(self, module or 'index')
            if method:
                code, res = method()
            else:
                code, res = E_RESRC, None
        self.send_response(res, code)

    def post(self, module):
        """
        预处理post: 验证、分析uri、调用uri对应的方法、返回处理结果
        """
        module = self.parse_module(module)
        code, res = self.check(), None
        if code == E_SUCC:
            if module in ('get', 'post'):
                module += '_'
            method = getattr(self, module or 'index')
            if method:
                code, res = method()
            else:
                code, res = E_RESRC, None
        self.send_response(res, code)

    def check_login(self):
        """
        根据session_id判断用户是否登录，如果登录，返回用户信息，否则为null
        """
        code, res = E_SUCC, None

        # 获取参数
        session_id = self.get_argument('session_id').encode('utf-8')

        user = AuthService().get_user_by_sessionid(session_id)
        if user:
            org = user.organization
            org = {'id':org.id, 'name':org.name, 'full_name':org.full_name} if org else None
            res = {'id':user.id, 'name':user.name, 'real_name':user.real_name,
                   'is_root':user.is_root, 'is_staff':user.is_staff, 'staff_no':user.staff_no,
                   'email':user.email, 'phone':user.phone, 'orgization':org,
                   'jlb_uid':user.jlb_uid}
        return code, res

    def touch_resource(self):
        """
        对资源列表的任何一个资源的指定的最低权限判断
        key:子系统的key
        session_id: 会话ID
        resources: 资源列表, {group1}:{resource1}, {group2}:{resource2}
        """
        code, res = E_SUCC, None

        # 获取参数
        key = self.get_argument('key').encode('utf-8')
        session_id = self.get_argument('session_id').encode('utf-8')
        resources = self.get_argument('resources').encode('utf-8').split(',')

        subsys = AuthService().get_subsystem(key)
        user = AuthService().get_user_by_sessionid(session_id)
        res = bool(user and user.touch_resource(subsys['id'], resources))
        return code, res

    def check_perm(self):
        """
        验证指定的资源访问权限
        key:子系统的key
        session_id: 会话ID
        oper: 资源操作对应的code值（乃臣设计时，操作,  add, update, delete, query, pub）
        resource: 资源, {group1}:{resource1}
        attr: 不再需要（乃臣：权限属性的键值对, attrName=attrValue&attrName=attrValue）
        """
        code, res = E_SUCC, None

        # 获取参数
        key = self.get_argument('key').encode('utf-8')
        session_id = self.get_argument('session_id').encode('utf-8')
        oper = self.get_argument('oper').encode('utf-8')
        resource = self.get_argument('resource').encode('utf-8')
        attr = dict(urlparse.parse_qsl(self.get_argument('attr', '')))

        subsys = AuthService().get_subsystem(key)
        user = AuthService().get_user_by_sessionid(session_id)
        res = bool(user and user.has_perm(subsys['id'], oper, resource, **attr))
        return code, res

    def get_perm_list(self):
        """
        获取登陆用户的指定资源的权限列表
        key:子系统的key
        session_id: 会话ID
        resource: 资源, {group1}:{resource1}
        """
        code, res = E_SUCC, []

        # 获取参数
        key = self.get_argument('key').encode('utf-8')
        session_id = self.get_argument('session_id').encode('utf-8')
        resource = self.get_argument('resource', '').encode('utf-8')

        subsys = AuthService().get_subsystem(key)
        user = AuthService().get_user_by_sessionid(session_id)
        if user:
            res = user.get_perm_list(subsys['id'], resource)
        return code, res

    def get_organization(self):
        """
        获取组织, 由版权系统调用
        key:子系统的key
        session_id: 会话ID
        id: 组织ID
        """
        code, res = E_SUCC, None

        # 获取参数
        key = self.get_argument('key').encode('utf-8')
        session_id = self.get_argument('session_id').encode('utf-8')
        org_id = int(self.get_argument('id'))

        subsys = AuthService().get_subsystem(key)
        user = AuthService().get_user_by_sessionid(session_id)
        #liugang 因增加了资源操作， 查看功能分为list和单个记录的detail查看
        #if user and user.has_perm(subsys['id'], 'query', 'organization', id=org_id):
        if user and user.has_perm(subsys['id'], 'list', 'org', id=org_id):
            res = Organization.mgr(ismaster=True).one(org_id)
        else:
            code = E_AUTH
        return code, res

    def save_organization(self):
        """
        更新、创建组织, 由版权系统调用, 所有的组织都为CP这个组织下级组织
        key:子系统的key
        session_id: 会话ID
        id: 组织ID
        name: 组织名称
        type: 类型, 默认CP
        status: 状态
        """
        code, res = E_SUCC, None

        # 获取参数
        # key = self.get_argument('key').encode('utf-8')
        # session_id = self.get_argument('session_id').encode('utf-8')
        org_id = int(self.get_argument('id', '0'))
        name = self.get_argument('name')
        status = int(self.get_argument('status', 1))

        # subsys = AuthService().get_subsystem(key)
        # user = AuthService().get_user_by_sessionid(session_id)
        parent = Organization.mgr().Q().filter(name='CP')[0]
        if parent: # and user
            level = parent.level + 1
            if org_id:
                org = Organization.mgr(ismaster=True).one(org_id)
                assert org.parent_id == parent.id
            else:
                org = Organization.new()
            if True: #user.has_perm(subsys['id'], 'all', 'organization', id=parent.id):
                org.name, org.level, org.parent_id, org.status = name, level, parent.id, status
                res = org.save()
            else:
                code = E_AUTH
        else:
            code = E_AUTH
        return code, res

    def get_user_list(self):
        """
        根据查询条件获取用户列表
        user_id: 用户ID
        org_id: 组织ID
        name: 用户登录名
        real_name: 用户真实姓名
        p: 页码
        psize: 每页大小
        """
        code, res = E_SUCC, None

        # 获取参数
        user_id = int(self.get_argument('user_id', 0))
        org_id = int(self.get_argument('org_id', 0))
        name = self.get_argument('name', '')
        real_name = self.get_argument('real_name', '')
        page = int(self.get_argument('p', 1))
        psize = int(self.get_argument('psize', 20))

        query = User.mgr().Q()
        if user_id:
            query.filter(id=user_id)
        if org_id:
            query.filter(org_id=org_id)
        if name:
            query.extra("name like '%%%s%%'"%name)
        if real_name:
            query.extra("real_name like '%%%s%%'"%real_name)
        count = query.count()
        ulist = []
        for i in query.set_limit((page-1)*psize, page*psize):
            ulist.append({'id':i.id, 'name':i.name, 'real_name':i.real_name,
                          'is_staff':i.is_staff, 'staff_no':i.staff_no,
                          'email':i.email, 'phone':i.phone, 'jlb_uid':i.jlb_uid})
        res = {'count':count, 'list':ulist}
        return code, res

    def get_multi_user(self):
        """
        根据UID列表件获取用户列表
        @uid_list: 用户ID列表, 逗号分隔
        """
        code, res = E_SUCC, None

        # 获取参数
        uid_list = self.get_argument('uid_list')
        if not uid_list:
            return code, []

        res = {}
        for i in User.mgr().Q().extra("id in (%s)" % ','.join(uid_list.split(','))):
            res[i.id] = {'id':i.id, 'name':i.name, 'real_name':i.real_name,
                         'is_staff':i.is_staff, 'staff_no':i.staff_no,
                         'email':i.email, 'phone':i.phone, 'jlb_uid':i.jlb_uid}
        return code, res

    def get_multi_user_byjlb(self):
        """
        根据UID列表件获取用户列表
        @uid_list: 用户ID列表, 逗号分隔
        """
        code, res = E_SUCC, None

        # 获取参数
        uid_list = self.get_argument('uid_list')
        if not uid_list:
            return code, []

        res = {}
        for i in User.mgr().Q().extra("jlb_uid in (%s)" % ','.join(uid_list.split(','))):
            res[i['jlb_uid']] = {
                'id':i.id, 'name':i.name, 'real_name':i.real_name,
                'is_staff':i.is_staff, 'staff_no':i.staff_no, 'passwd':i.passwd,
                'email':i.email, 'phone':i.phone, 'jlb_uid':i.jlb_uid
            }
        return code, res

    def login(self):
        """
        根据用户名登录
        name: 登录名
        password: 密码
        """
        code, res = E_SUCC, None

        # 获取参数
        name = self.get_argument('name')
        password = self.get_argument('password')

        #res = User().login(name, password)
        res = UserService().login(name, password)
        return code, res

    def get_top_menulist(self):
        """
        根据会话ID获取相关系统的顶级菜单列表
        """
        # 获取参数
        key = self.get_argument('key')
        session_id = self.get_argument('session_id')

        auth_srv = AuthService()
        subsys = auth_srv.get_subsystem(key)
        user = AuthService().get_user_by_sessionid(session_id)

        # 过滤menu
        menulist = []
        for menu in Menu.mgr().Q().filter(system_id=subsys['id'],
                                          level=0).orderby('no'):
            if self._check_menu(menu, subsys, user):
                menulist.append(dict(menu))
        return E_SUCC, {
            'subsys':subsys,
            'menu_list':menulist,
        }

    def get_menulist(self):
        """
        根据父级菜单获取子菜单列表
        """
        # 获取参数
        key = self.get_argument('key')
        parent_id = int(self.get_argument('parent_id'))
        session_id = self.get_argument('session_id')

        auth_srv = AuthService()
        subsys = auth_srv.get_subsystem(key)

        user = AuthService().get_user_by_sessionid(session_id)

        # 过滤menu
        menulist = []
        for menu in Menu.mgr().Q().filter(system_id=subsys['id'], parent_id=parent_id).orderby('no'):
            if self._check_menu(menu, subsys, user):
                menulist.append(dict(menu))

        return E_SUCC, {
            'subsys':subsys,
            'menu_list':menulist,
        }

    def _check_menu(self, menu, subsys, user):
        """
        审核菜单
        """
        family = list(menu.descent())
        family.append(menu)
        for i in family:
            if i.resource:
                res = ['%s:%s' % (i.resource.group, i.resource.name)]
            else:
                res = [':']
            if user.touch_resource(subsys['id'], res):
                return True
        return False

    def get_user(self):
        name = self.get_argument('name', '')
        if not name:
            return E_FORBID, None
        res = User.mgr(ismaster=True).Q().filter(name=name).query()
        if res:
            return E_SUCC, res[0]

        res = User.mgr(ismaster=True).Q().filter(phone=name).query()
        return E_SUCC, res[0] if res else None

    def get_user_byid(self):
        user_id = int(self.get_argument('uid', 0))
        user = User.mgr(ismaster=True).one(user_id)

        return E_SUCC, user

