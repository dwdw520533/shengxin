#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
首页、菜单等
"""
import urlparse
from lib.utils import url_add_params
import tornado
from handler.base import BaseHandler, authenticated
from model.menu import Menu
from model.notice import Notice
from service.context import Context


class IndexHandler(BaseHandler):
    """
    首页
    """
    @authenticated
    def get(self):
        """
        GET方法
        """
        # switch to subsystem
        system_id = int(self.get_argument('system_id', 0))
        if system_id:
            self.switch_subsystem(system_id)
            self.redirect('/')
            return
        cur, menu_0_list = self.get_current_subsystem(), []
        user_group = None
        if cur:
            menu_0_list = Menu.mgr().Q().filter(system_id=cur.id, level=0).orderby('no').data()
            # TODO此次可以增加只对客服用户才会去获取
            if cur.id == 2 and cur:
                user_group = Context.inst().read_user_group(self.current_user['id'], cur['domain'])

        # 获取当前用户的公告
        self.render("index.html", cur_subsystem=cur, user_group=user_group,
                    menu_0_list=menu_0_list, current_system=cur,
                    subsystems=self.get_subsystems(),
                    notice_list=self.get_notice_list())


class MeHandler(BaseHandler):
    """
    当前用户
    """
    def index(self):
        """
        首页
        """
        self.render("me/index.html")

    def home(self):
        """
        我的主页
        """
        self.render("me/home.html",
                    notice_list=self.get_notice_list())

    def notice(self):
        """
        通知
        """
        notice_id = int(self.get_argument('notice_id'))
        notice = Notice.mgr().one(notice_id)
        self.render("me/notice.html",
                    notice=notice)


class MenuTreeHandler(BaseHandler):
    """
    菜单Tree
    """
    def index(self):
        """
        子菜单列表
        """
        parent_id = int(self.get_argument('parent_id'))
        cur = self.get_current_subsystem()
        menu_list = Menu.mgr().Q().filter(system_id=cur.id,
                                          parent_id=parent_id).orderby('no').data()
        self.render("setting/index.html",
                    menu_list=menu_list)


class ProxyHandler(BaseHandler):
    """
    代理转发HTTP请求到各个子系统
    异步http调用
    """
    @staticmethod
    def async_open(url, body=None, method='GET', headers=None, callback=None):
        """
        异步请求
        """
        http = tornado.httpclient.AsyncHTTPClient()
        req = tornado.httpclient.HTTPRequest(url, body=body, method=method, headers=headers)
        http.fetch(req, callback=callback)

    def on_async_response(self, response):
        """
        回调函数
        """
        for i in response.headers:
            if i in ('content-type', 'content-encoding', 'Content-Disposition'):
                self.set_header(i, response.headers[i])
        self.finish(response.body)

    @tornado.web.asynchronous
    def index(self):
        """
        异步HTTP
        """
        url = self.get_argument('x-url')
        headers = self.request.headers.copy()
        headers['Host'] = urlparse.urlparse(url).netloc

        # 构造各个子系统的url以及相应的参数
        data = {'x-proxy':'http://%s/proxy'%self.request.host}
        query_dict = dict(urlparse.parse_qsl(urlparse.urlparse(self.request.uri).query))
        for k in query_dict:
            if k != 'x-url':
                data[k] = query_dict[k]
        url = url_add_params(url, **data)

        # POST方法的HTTP BODY
        if self.request.method == 'POST':
            body = self.request.body
        else:
            body = None
        self.async_open(url, body, self.request.method, headers, self.on_async_response)

