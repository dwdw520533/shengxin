#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
通用方法for单元测试
'''
import requests
import urllib
import json
import string
import random
import logging
import urllib2
from lib.utils import force_utf8

def send_request(url, params=None):
        """
        发送请求
        :url: 请求地址
        :params: 请求参数
        return json
        """
        try:
            print "params-----------------------------"
            print "url: %s" % url

            resp = urllib2.urlopen(url, urllib.urlencode(params) if params else {})
            res = resp.read()
            res_utf8 = force_utf8(json.loads(res))
            print "res=: %s" % res_utf8
            return res_utf8
        except Exception, e:
            logging.error('send request error %s', str(e), exc_info=True)
            return None

def send_req(host, uri, data, params=None, method='get', headers=None, is_check_code=False, test_unit=None):
    try:
        print "-----------------------------"

        # GdsAppAgent

        headers = headers or {"ZkfcAppAgent":"p1=1111||p2=1212"}

        url = '%s%s' % (host ,uri)
        #print url
        if method == 'get':
            r = requests.get(url, params=data , headers=headers)
        elif params is None:
            r = requests.post(url, data=data , headers=headers)
        else:
            r = requests.request(method, url, data = data, params = params, headers = headers)

        print ">>TEST_REQ:%s:%s" % (method,r.url)
        print r.request.body

        req_code = r.status_code
        #print ">>%s" % r.headers['content-type']
        if req_code != 200:
            err = ">>Server_ERR:%s ,%s" % (req_code ,url)
            print err
            if is_check_code:
                test_unit.assertEquals(req_code, 200, err)
        else:
            res_json = r.json()
            #print res_json
            try:
                res_code = res_json['code']
                #print "isinstance(res_json, dict)=%s" % isinstance(res_json, dict)
                if isinstance(res_json, dict):
                    if res_code != 0:
                        err = u">>BIZ_ERR:error_code:%s , %s, %s" % (res_json['code'], res_json['msg'], url)
                        print err
                        if is_check_code:
                            test_unit.assertEquals(res_code, 0, err)
                    else:
                        # print "res_code!=0!"
                        pass
                    print ">>RESPONSE_RES:%s" % res_json
                    return res_json.get('res',None) ,res_code
                else:
                    print "empty!"
            except Exception ,e:
                err = ">>BIZ_ERR: %s,%s,%s" % (res_json, e,url)
                print err
                if is_check_code:
                    test_unit.assertEquals(res_code, 0, err)
                return res_json, req_code
            else:
                print ">>RESPONSE_RES:%s" % res_json
                if isinstance(res_json, int):
                    return res_json, req_code
                else:
                    return res_json.get('res',None),req_code
    except Exception ,e:
        err = ">>NWK_ERR: %s ,%s" % (e, url)
        print err
        if is_check_code:
            test_unit.assertEquals("!", "", err)
        return False, False
