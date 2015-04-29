#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import datetime
from lib.utils import url_add_params

def strftime_day(handler, dtime):
    return dtime.strftime('%Y-%m-%d')
    
def jsondump(handler, obj):
	import json
	return json.dumps(obj)

def base64_url(handler, url):
	import base64
	return base64.b64encode(url)

def extract_url(handler, url):
	return url.split("http://")[1].split("/")[0]

def formatdate(handler, obj=None, format="%Y-%m-%d %H:%M:%S"):
	from datetime import datetime
	res = datetime.now() if not obj else obj
	return res.strftime(format)

def number_parity(handler, number):
	# check a number is an odd number or an even number
	if number % 2 == 0:
		return 'odd'
	else:
		return 'even'

def stc_url(handler, uri):
	return 'stc/%s'%uri

def touch_resource(handler, resource_list):
    '''
    for tpl to judge if touch on of resource list
    '''
    if handler.current_user:
        cur = handler.get_current_subsystem()
        return handler.current_user.touch_resource(cur.id,resource_list)
    return False

def touch_menu(handler, menu):
    '''
    for tpl to control menu hidden or show
    '''
    if handler.current_user.is_root:
        return True
    cur = handler.get_current_subsystem()
    family = list(menu.descent())
    family.append(menu)
    for i in family:
        if i.resource:
            res = ['%s:%s'%(i.resource.group,i.resource.name)]
        else:
            res = [':']
        #return True
        if handler.current_user.touch_resource(cur.id,res):
            return True
    return False

def has_perm(handler, oper, resource, **attr):
    '''
    for tpl to judge permmsion
    '''
    if handler.current_user:
        cur = handler.get_current_subsystem()
        return handler.current_user.has_perm(cur.id,oper,resource,**attr)
    return False

def menu_url(handler, menu):
    '''
    generate menu url
    '''
    cur = handler.get_current_subsystem()
    if menu.uri.startswith('http://'):
        url = url_add_params(menu.uri,target_tab=menu.target_tab)
    elif cur.domain:
        url = 'http://%s%s' % (cur.domain,menu.uri)
        url = url_add_params(url,target_tab=menu.target_tab)
        url = '/proxy?%s' % urllib.urlencode({'x-url':url})
    else:
        url = url_add_params(menu.uri,target_tab=menu.target_tab)
    return url

def wrap_url(handler, syskey, url):
	return handler.wrap_url(syskey,url)

