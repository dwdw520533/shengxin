#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
记录带回状态
"""
from conf.settings import CS_PHONE_LOG_DIR
from lib.utils import write2log
from handler.base import BaseHandler


class CallHandler(BaseHandler):
    """
    记录带回状态
    """
    def log__state(self):
        """
        GET方法
        """
        state = self.get_argument('state_str', '')
        write2log(CS_PHONE_LOG_DIR, 'csphone', state)
        self.json2dwz('200', '', '', msg='ok')
