#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
测试环境host配置
'''
#authsys根目录下执行, 本地环境
#python init.py -runmode=dev -log_file_prefix=/Users/liu/data/log/authsys.tornado.log
env = 'dev'
host = 'http://127.0.0.1:8423'

#开发环境
#host = 'http://10.0.1.232:6000'

#测试环境1， 245机器
#测试环境2， 246机器

#生产环境
#env = 'prd'
#host = 'http://'
