#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import datetime
import tornado.web
uibase = tornado.web.UIModule

class MyHomeModule(uibase):
	def render(self, notice_list):
		return self.render_string("ui_mod/myhome.html",
            notice_list = notice_list)

class Pagination(uibase):
	def render(self, count, page, psize, target_type='navTab'):
		return self.render_string("ui_mod/pagination.html",
			count = count,
			page = page,
			psize = psize,
			target_type = target_type
		)

class MenuItem(uibase):
	def render(self, menu):
		return self.render_string("ui_mod/menu_item.html",
			menu = menu,
		)

class PermConfData(uibase):
    def render(self, perm_attr):
        return self.render_string('user/perm/conf.html',
                    perm_attr = perm_attr)

class ResActionsData(uibase):
    def render(self, res_ractions, cur_ract_codes):
        return self.render_string('user/perm/res_ractions.html',
                    res_ractions = res_ractions,
                    cur_ract_codes=cur_ract_codes)

