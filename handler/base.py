#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handler基类
"""
import json
import urllib
import urlparse
import functools
import tornado.web
from conf.settings import SESSION_USER, SESSION_SYSTEM
from conf.settings import ERR_DESC, E_PARAM
from lib.utils import url_add_params, json_default
from model.user import User, Organization
from model.subsystem import SubSystem
from model.notice import Notice, NoticeWho


class ParamException(Exception):
    code = E_PARAM
    msg = None

    def __init__(self, msg, *args, **kwargs):
        super(ParamException, self).__init__(*args, **kwargs)
        self.msg = msg

def authenticated(method):
    """Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If you configure a login url with a query parameter, Tornado will
    assume you know what you're doing and use it as-is.  If not, it
    will add a `next` parameter so the login page knows where to send
    you once you're logged in.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            url = self.get_login_url()
            splited = urlparse.urlsplit(url)
            if urlparse.urlsplit(self.request.uri).path != splited.path:
                if self.request.method in ("GET", "HEAD"):
                    if "?" not in url:
                        if splited.scheme:
                            # if login url is absolute, make next absolute too
                            next_url = self.request.full_url()
                        else:
                            next_url = self.request.uri
                        url += "?" + urllib.urlencode(dict(next=next_url))
                    self.redirect(url)
                    return
                raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


class BaseHandler(tornado.web.RequestHandler):
    """
    基础功能封装
    """
    ARG_DEFAULT = object()
    def initialize(self, prefix=None):
        """
        重写Handler初始化
        """

        self.module_prefix = prefix

    def send_json(self, res, code, callback=None):
        """
        发送json数据
        """
        response = {
            "status": code,
            "msg": ERR_DESC.get(code, None),
            "res": res
        }
        response = json.dumps(response, default=json_default)
        if callback:
            response = '%s(%s);' % (callback, response)
            self.set_header('Content-Type', 'application/json')
        self.finish(response)
 
    def get_argument(self, name, default=tornado.web.RequestHandler._ARG_DEFAULT, strip=True):
        """
        重写以把unicode的参数都进行utf-8编码
        """
        value = super(BaseHandler, self).get_argument(name, default, strip)
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return value

    def get_argument_int(self, name, default=ARG_DEFAULT):
        """
        获取整型参数
        :param name: 参数名
        :param default: 如果未传此参数时得到的默认值
        :return: 返回得到的整型值
        """
        value = self.get_argument(name, default)
        if value == self.ARG_DEFAULT:
            raise ParamException("参数: %s 不能为空" % name)
        elif value == default:
            return value
        try:
            value = int(value)
        except:
            if default != self.ARG_DEFAULT:
                return default
            raise ParamException("参数: %s 格式不正确" % name)
        return value

    def prepare(self):
        """
        called by tornado before every request handling
        """
        self.target_tab = self.get_argument('target_tab', '')

    @property
    def session(self):
        """
        会话
        """
        if not hasattr(self, '_session'):
            session_mgr = self.application.settings['session_mgr']
            session_mgr.set_request_handler(self)
            setattr(self, '_session', session_mgr.load_session())
        return getattr(self, '_session')

    @staticmethod
    def parse_module(module):
        """
        解析模块
        """
        mod, sub = "", ""
        if module:
            arr = module.split("/")
            if len(arr) >= 3:
                mod, sub = arr[1], arr[2]
            elif len(arr) >= 2:
                mod = arr[1]
        return '%s__%s'%(mod, sub) if sub else mod

    @authenticated
    def get(self, module):
        """
        GET 方法
        """
        module = self.parse_module(module)
        method = getattr(self, module or 'index')
        if method and module not in ('get', 'post'):
            method()
        else:
            raise tornado.web.HTTPError(404)

    @authenticated
    def post(self, module):
        """
        POST 方法
        """
        module = self.parse_module(module)
        method = getattr(self, module or 'index')
        if method and module not in ('get', 'post'):
            method()
        else:
            raise tornado.web.HTTPError(404)

    def get_current_user(self):
        """
        Tornado的回调函数, 获取当前用户
        """
        uinfo, user = self.session[SESSION_USER], None
        if uinfo:
            user = User.mgr().Q().filter(id=uinfo['uid'])[0]
            if not user:
                self._logout()
        return user

    def _login(self, uid):
        """
        登录, 记录到SESSION
        """
        self.session[SESSION_USER] = {'uid':uid}
        self.session.save()

    def _logout(self):
        """
        登出, 清空SESSION
        """
        self.session[SESSION_USER] = None
        self.session.save()

    def json2dwz(self, code, cb_type='closeCurrent', nav_tab_id='', forward_url='', msg=''):
        """
        send status response to dwz
        """
        res = {
            'statusCode':code,
            'callbackType':cb_type,
            'navTabId':nav_tab_id,
            'forwardUrl':forward_url,
            'message':msg
        }
        res = json.dumps(res)
        self.write(res)

    def has_perm(self, oper, resource, **attr):
        """
        check perm of current user
        """
        return self.current_user.has_perm(oper, resource, **attr)

    def wrap_url(self, syskey, url):
        """
        wrap the url for subsystem
        """
        proxy_source = 'http://%s/proxy' % self.request.host
        subsys = SubSystem.mgr().Q().filter(syskey=syskey)[0]
        if not url.startswith('http://'):
            url = urlparse.urljoin('http://%s'%subsys.domain, url)
        url = url_add_params(proxy_source, False, **{'x-url':url})
        url = url_add_params(url, False, target_tab=self.target_tab)
        return url

    def get_subsystems(self):
        """
        get all subsystems the user touch
        """
        return SubSystem.mgr().Q().data()

    def get_current_subsystem(self):
        """
        get the subsystem to display
        """
        subsystems = self.get_subsystems()
        return subsystems[0] if subsystems else None

    def switch_subsystem(self, system_id):
        """
        切换到指定的子系统
        """
        system = SubSystem.mgr().one(system_id)
        if system and self.current_user.touch_resource(system.id):
            self.session[SESSION_SYSTEM] = {'system_id':system_id}
            self.session.save()

    def get_notice_list(self, length=10):
        """
        取得当前用户的公告信息: 指派给该用户的 + 指派给所属部门的 + 广播的
        """
        # 当前用户的公告
        user = self.current_user
        notice_user_list = NoticeWho.mgr().Q().filter(who_type='user', who_id=user.id).data()
        # 当前用户的部门的公告
        org = Organization.mgr().one(user.org_id)
        org_list = org.path() if org else []
        org_list = ','.join([str(i.id) for i in org_list])
        query = NoticeWho.mgr().Q().filter(who_type='organization')
        notice_org_list = query.extra('who_id in (%s)'%org_list).data() if org_list else []
        # 当前用户的、非广播的公告ID
        notice_list = notice_user_list + notice_org_list
        notice_ids = ','.join([str(i.notice_id) for i in notice_list])
        # 加上广播的公告
        sql = 'is_global=1 OR id in (%s)'%notice_ids if notice_ids else 'is_global=1'
        query = Notice.mgr().Q().extra(sql)
        return query.orderby('is_top', 'DESC').orderby('create_time', 'DESC')[:length]

    def filter_org_query(self, query):
        """
        根据用户权限过滤组织
        (乃臣：设定只能访问某些指定的ID记录, 在Perm的attr属性中获取)
        """
        orgids = []
        for i in self.current_user.get_perm_list(1, 'user:organization'):
            orgids.extend(i['attr'].get('id', '').split(':'))
        # 如果是root或者拥有all
        if self.current_user.is_root or orgids.count('all'):
            return query
        orgid_list = []
        for i in orgids:
            orgid_list.append(i)
            if i and i != 'all':
                org = Organization.mgr().one(int(i))
                if org:
                    orgid_list.extend([str(i.id) for i in org.children])
        orgids = ','.join([i for i in orgid_list if i and i != 'all'])
        if orgids:
            query.extra("id in (%s)" % orgids)
        else:
            query.filter(id=0) # 忽略所有
        return query

    def filter_user_query(self, query):
        """
        根据用户权限过滤用户
        """
        orgids, uids = [], []
        for i in self.current_user.get_perm_list(1, 'user:user'):
            org_id, _id = i['attr'].get('org_id', ''), i['attr'].get('id', '')
            orgids.extend([j for j in org_id.split(':') if j])
            uids.extend([j for j in _id.split(':') if j])
        # 如果是root或者拥有all
        if self.current_user.is_root or (orgids.count('all') and uids.count('all')):
            return query
        # 通过组织过滤
        if orgids.count('all') == 0:
            orgid_list = []
            for i in orgids:
                orgid_list.append(i)
                if i and i != 'all':
                    org = Organization.mgr().one(int(i))
                    if org:
                        orgid_list.extend([str(i.id) for i in org.children])
            orgids = ','.join([i for i in orgid_list if i and i != 'all'])
            if orgids:
                query.extra("org_id in (%s)" % orgids)
            else:
                query.filter(id=0) #忽略所有
        # 通过用户ID过滤
        if uids.count('all') == 0:
            uids = ','.join([i for i in uids if i and i != 'all'])
            if uids:
                query.extra("id in (%s)" % uids)
            else:
                query.filter(id=0) #忽略所有
        return query

    def filter_role_query(self, query):
        """
        根据用户权限过滤角色
        """
        role_ids = []
        for i in self.current_user.get_perm_list(1, 'user:role'):
            _id = i['attr'].get('id', '')
            role_ids.extend([j for j in _id.split(':') if j])
        # 如果是root或者拥有all
        if self.current_user.is_root or role_ids.count('all'):
            return query
        # 通过角色ID过滤
        role_ids = ','.join([i for i in role_ids if i and i != 'all'])
        if role_ids:
            query.extra("id in (%s)" % role_ids)
        else:
            query.filter(id=0) #忽略所有
        return query

    def filter_perm_query(self, query):
        """
        根据用户权限过滤权限
        """
        perm_ids = []
        for i in self.current_user.get_perm_list(1, 'user:perm'):
            _id = i['attr'].get('id', '')
            perm_ids.extend([j for j in _id.split(':') if j])
        # 如果是root或者拥有all
        if self.current_user.is_root or perm_ids.count('all'):
            return query
        # 通过角色ID过滤
        perm_ids = ','.join([i for i in perm_ids if i and i != 'all'])
        if perm_ids:
            query.extra("id in (%s)" % perm_ids)
        else:
            query.filter(id=0) #忽略所有
        return query

    def filter_resource_query(self, query):
        """
        根据用户权限过滤资源
        """
        resource_ids = []
        for i in self.current_user.get_perm_list(1, 'user:resource'):
            _id = i['attr'].get('id', '')
            resource_ids.extend([j for j in _id.split(':') if j])
        # 如果是root或者拥有all
        if self.current_user.is_root or resource_ids.count('all'):
            return query
        # 通过资源ID过滤
        resource_ids = ','.join([i for i in resource_ids if i and i != 'all'])
        if resource_ids:
            query.extra("id in (%s)" % resource_ids)
        else:
            query.filter(id=0) #忽略所有
        return query

