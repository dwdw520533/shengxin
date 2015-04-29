#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
启动入口
'''
# sys
import os
import sys
import logging

# tornado
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

define('port', default=8423, help='run on this port', type=int)
define('debug', default=True, help='enable debug mode')
define('runmode', default='dev', help='dev gray prod')
define('project_path', default=sys.path[0], help='deploy_path')

tornado.options.parse_command_line()

if options.debug:
    import tornado.autoreload

# my...
from lib import uimodules, uimethods
from conf.settings import AUTH_CNF
from service.auth import AuthService

# handler
from handler.index import (IndexHandler, MeHandler, MenuTreeHandler,
                           ProxyHandler)
from handler.org import OrgHandler
from handler.user import UserHandler
from handler.role import RoleHandler
from handler.perm import PermHandler
from handler.resource import ResourceHandler
from handler.menu import MenuHandler
from handler.subsystem import SubSystemHandler
from handler.auth import AuthHandler
from handler.notice import NoticeHandler
from handler.call import CallHandler
from handler.api import ApiHandler
from handler.position import PositionHandler
from handler.resaction import ResActionHandler
from handler.resgroup import ResGroupHandler


class Application(tornado.web.Application):
    '''
    应用类
    '''
    def __init__(self):
        '''
        应用初始化
        '''
        settings = {
            'ui_modules': uimodules,
            'ui_methods': uimethods,
            'static_path': os.path.join(options.project_path, 'static'),
            'template_path': os.path.join(options.project_path, 'tpl'),
            'xsrf_cookies': False,
            'site_title': 'demo',
            'login_url':AUTH_CNF['login_url'],
            'session_mgr': AuthService().session_mgr,
            'debug': options.debug,
        }
        handlers = [
            (r'/', IndexHandler),
            (r'/me(/[a-zA-Z/]*)?', MeHandler),
            (r'/user(/[a-zA-Z/]*)?', UserHandler),
            (r'/position(/[a-zA-Z/]*)?', PositionHandler),
            (r'/raction(/[a-zA-Z/]*)?', ResActionHandler),
            (r'/resgroup(/[a-zA-Z/]*)?', ResGroupHandler),
            (r'/role(/[a-zA-Z/]*)?', RoleHandler),
            (r'/perm(/[a-zA-Z/_]*)?', PermHandler),
            (r'/org(/[a-zA-Z/]*)?', OrgHandler),
            (r'/resource(/[a-zA-Z/]*)?', ResourceHandler),
            (r'/tree(/[a-zA-Z/]*)?', MenuTreeHandler),
            (r'/menu(/[a-zA-Z/]*)?', MenuHandler),
            (r'/subsystem(/[a-zA-Z/]*)?', SubSystemHandler),
            (r'/proxy(/[a-zA-Z/]*)?', ProxyHandler),
            (r'/auth(/[a-zA-Z/_]*)?', AuthHandler),
            (r'/notice(/[a-zA-Z/_]*)?', NoticeHandler),
            (r'/call(/[a-zA-Z/_]*)?', CallHandler),
            (r'/api(/[a-zA-Z/_]*)?', ApiHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

    def log_request(self, handler):
        '''
        定制如何记录日志
        @handler: request handler
        '''
        status = handler.get_status()
        if status < 400:
            if handler.request.uri[0:7] == '/static':
                return
            log_method = logging.info
        elif status < 500:
            log_method = logging.warning
        else:
            log_method = logging.error
        request_time = 1000.0 * handler.request.request_time()
        if request_time > 30.0 or options.debug or status >= 400:
            log_method('%d %s %.2fms', status, handler._request_summary(), request_time)

if __name__ == '__main__':
    tornado.httpserver.HTTPServer(Application(), xheaders=True).listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

