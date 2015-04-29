#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
号码通服务器测试
'''

import os
import sys
import unittest
import time
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from service.user import UserService
from service.context import Context
from service.user import UserService
import conf4test
import utils4test

class TestUser(unittest.TestCase):
    def setUp(self):
        self.yp_service = UserService()
        self.phone = "18612965072"
        self.password = "123456"
        self.cxt = Context.inst()
        self.login()

        #sunyanfeng
        self.audit_uid = 40
        self.audit_phone = '15010761863'

        self.common_params = {
            'sign_type': 'MD5',
            'ts': int(time.time()),
            'uid': self.uid,
            'sid': self.sid
        }

        #用于tearDown中删除
        self.create_audit_ids = []
        self.create_page_ids = []
        self.create_error_ids = []

        print conf4test.host

    def login(self):
        user_info = UserService().login(self.phone, self.password)
        if user_info:
            self.uid = user_info["id"]
            self.sid = user_info["session"]["sid"]
        else:
            raise Exception('User not exist')
        print user_info

    def tearDown(self):
         pass

    def test_user(self):

        pass




if __name__ == "__main__":
    unittest.main()

