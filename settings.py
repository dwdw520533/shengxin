# -*- coding: utf-8 -*-
#!/usr/bin/env python
__author__ = 'Kinslayer'
import os
import platform
import web
import logging
from sqlalchemy import create_engine

TEST = False
token = "dongwei123456789"
encodingAESKey = "xBj5QuQwiqhBxxgUrVunSc5plmQKCBa6QwwFzcaXgMy"

appId = 'wxf8b4f85f3a794e77'
appSecret = '4333d426b8d01a3fe64d53f36892df'

HERE = os.path.dirname(__file__)

PARENT_DIR = os.path.dirname(HERE)

DBPATH = os.path.join(PARENT_DIR, 'database').replace('\\', '/')
logpath = os.path.join(PARENT_DIR, 'log').replace('\\', '/')


DBN = r'mysql://wepay:wepay@localhost/wepay_host?charset=utf8'
engine = create_engine(DBN, echo=False, pool_recycle=7200)

if not os.path.exists(logpath):
    os.mkdir(logpath)

logfile = os.path.join(logpath, 'wepay_host.log')
print logfile
#print logfile
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(filename)s]: %(levelname)s - %(message)s',
                    #datefmt='%a, %d %b %Y %H:%M:%S',
                    datefmt='%Y-%m-%d %X',
                    filename=logfile,
                    filemode='a')

