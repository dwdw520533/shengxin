#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
用户相关Model
'''

import random
import hashlib
import datetime
from lib.localcache import mem_cache
from lib.database import Model
from model.subsystem import SubSystem

class UserBase(Model):
    '''
    用户相关的基类
    '''
    _db = 'authsys'
    _pk = 'id'

class Organization(UserBase):
    '''
    组织(部门)
    '''
    _table = 'organization'
    _fields = set(['id', 'name', 'level', 'parent_id', 'status', 'create_user',
                   'create_time', 'update_user', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`name` varchar(32) NOT NULL DEFAULT '' COMMENT '组织名称'",
               "`level` int NOT NULL DEFAULT '0' COMMENT '组织级别'",
               "`parent_id` int NOT NULL DEFAULT '0' COMMENT '上级组织ID'",
               "`status` int NOT NULL DEFAULT '1' COMMENT '状态'",
               "`create_user` varchar(32) NOT NULL DEFAULT ''",
               "`create_time` datetime NOT NULL DEFAULT '1970-01-01'",
               "`update_user` varchar(32) NOT NULL DEFAULT ''",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `parent_name` (`parent_id`,`name`)")
    def before_add(self):
        '''
        插入数据前回调
        '''
        self['create_time'] = datetime.datetime.now()

    def path(self):
        '''
        组织的树根到自己节点的路径
        '''
        path = [self]
        parent = self.parent
        if parent:
            path = parent.path() + path
        return path

    @mem_cache(10, start=1)
    def one_cache(self, org_id):
        '''
        缓存在内存10秒
        '''
        return Organization.mgr(self.ismaster).one(org_id)

    @property
    def parent(self):
        '''
        父级组织
        '''
        return self.one_cache(self.parent_id)

    @property
    def full_name(self):
        '''
        组织全名
        '''
        return '-'.join([o.name for o in self.path()])

    @property
    def children(self):
        '''
        所有下级组织
        '''
        for i in Organization.mgr(self.ismaster).Q().filter(parent_id=self.id):
            yield i
            for j in i.children:
                yield j

class User(UserBase):
    '''
    用户
    '''
    _table = 'user'
    _fields = set(['id', 'name', 'passwd', 'real_name', 'is_root', 'is_staff',
                   'staff_no', 'org_id', 'jlb_uid', 'email', 'phone', 'status', 'create_user',
                   'create_time', 'update_user', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`name` varchar(32) NOT NULL DEFAULT '' COMMENT '登陆名'",
               "`passwd` varchar(64) NOT NULL DEFAULT '' COMMENT '密码'",
               "`real_name` varchar(64) NOT NULL DEFAULT '' COMMENT '真实名字'",
               "`is_root` tinyint NOT NULL DEFAULT '0' COMMENT '是否root用户'",
               "`is_staff` tinyint NOT NULL DEFAULT '1' COMMENT '是否内部员工'",
               "`staff_no` int NOT NULL DEFAULT '0' COMMENT '员工号'",
               "`org_id` int NOT NULL DEFAULT '0' COMMENT '组织ID'",
               "`jlb_uid` int NOT NULL DEFAULT '0' COMMENT '近邻宝ID'",
               "`email` varchar(64) NOT NULL DEFAULT ''",
               "`phone` varchar(16) NOT NULL DEFAULT '' ",
               "`status` int NOT NULL DEFAULT '1' COMMENT '是否有效'",
               "`create_user` varchar(32) NOT NULL DEFAULT ''",
               "`create_time` datetime NOT NULL DEFAULT '1970-01-01'",
               "`update_user` varchar(32) NOT NULL DEFAULT ''",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `idx_name` (`name`)",
               "UNIQUE KEY `idx_email` (`email`)",
               "UNIQUE KEY `idx_phone` (`phone`)",
               "UNIQUE KEY `idx_jlbuid` (`jlb_uid`)")

    def before_add(self):
        '''
        插入数据前, 回调
        '''
        if 'passwd' in self and self.passwd and self.passwd.find('&') == -1:
            self['passwd'] = self._encry_passwd(self.passwd)
        self['create_time'] = datetime.datetime.now()

    def before_update(self):
        '''
        更新数据前, 回调
        '''
        if 'passwd' in self:
            if self['passwd'] and self['passwd'].find('&') == -1:
                self['passwd'] = self._encry_passwd(self['passwd'])
            else:
                del self['passwd']

    def before_delete(self):
        '''
        删除用户时, 自动删除该用户和角色的关系
        '''
        for i in UserRole.mgr(self.ismaster).Q().filter(uid=self.id):
            i.delete()

    @property
    def organization(self):
        '''
        所在组织
        '''
        return Organization.mgr(self.ismaster).one_cache(self.org_id)

    def login(self, name, passwd):
        '''
        进行登录名、密码验证
        '''
        user = self.Q().filter(name=name)[0] or self.Q().filter(phone=name)[0]
        if user and self.check_passwd(user.passwd, passwd):
            return user
        return None

    def _hexdigest(self, salt, raw):
        '''
        hash
        '''
        return hashlib.sha1(salt+raw+salt).hexdigest()

    def _encry_passwd(self, rawpasswd):
        '''
        用sha1哈希密码
        '''
        rval = str(random.random())
        salt = self._hexdigest(rval, rval)[:6]
        hashval = self._hexdigest(salt, rawpasswd)
        return '%s&%s' % (salt, hashval)

    def check_passwd(self, encpasswd, rawpasswd):
        '''
        校验密码
        '''
        if encpasswd.find('&') > -1:
            salt, hashval = encpasswd.split('&')
            chk = self._hexdigest(salt, rawpasswd) == hashval
        else:
            chk = encpasswd == rawpasswd
        return chk

    def roles(self):
        '''
        拥有的所有角色
        '''
        role_id_list = [str(i.role_id) for i in UserRole.mgr(self.ismaster).Q().filter(uid=self.id)]
        if role_id_list:
            role_list = Role.mgr(self.ismaster).Q().extra('id in (%s)' % ','.join(role_id_list)).data()
        else:
            role_list = []
        return role_list

    def perms(self):
        '''
        所有权限
        '''
        if self._perms is None:
            self._perms = []
            for role in self.roles():
                self._perms.extend(role.perms())
        return self._perms

    def check_resource(self, system_id, res_to_check, res_haved, strict=True):
        '''
        校验资源
        system_id: 待检验的子系统ID
        res_to_check: 待检验的资源, 格式：{resource_group:resource_name}
        res_haved: 用户拥有的资源
        strict: 是否严格检验。若非严格, 进行资源组的检验
        '''
        arr, flag = res_to_check.split(':'), False
        if system_id == res_haved.system_id:
            if res_haved.name == 'whole_system':
                return True
            if len(arr) == 2:
                flag = (arr[0] == res_haved.group) and (arr[1] == res_haved.name)
            elif len(arr) == 1 and not strict:
                flag = (arr[0] == res_haved.group)
        return flag

    def touch_resource(self, system_id, resource_list=None):
        '''
        检验是否拥有指定资源列表的任何一个资源的最低权限
        system_id: 待检验的子系统ID
        resource_list: 资源列表, resource_group:resource_name
        '''
        resource_list = resource_list or []
        if self.is_root:
            return True
        for i in self.perms():
            if not resource_list and system_id == i.resource.system_id:
                return True
            else:
                for r in resource_list:
                    if self.check_resource(system_id, r, i.resource, False):
                        return True
        return False

    def has_perm(self, system_id, oper, resource, **attr):
        '''
        检验是否拥有指定资源的访问权限
        system_id: 待检验的子系统ID
        oper: 操作, add delete update query
        resource: 资源：resource_group:resource_name
        attr: 资源的属性(动态)
        '''
        if self.is_root:
            return True
        for i in self.perms():
            if (i.oper == 'all' or i.oper == oper) and self.check_resource(system_id, resource, i.resource):
                flag = True
                for a in i.attr:
                    my_val = str(i.attr[a])
                    my_val_list = [j for j in my_val.split(':') if j]
                    check_val = str(attr.get(a, ''))
                    if not (my_val == 'all' or check_val in my_val_list or my_val == check_val):
                        flag = False
                if flag:
                    return True
        return False

    def get_perm_list(self, system_id, resource=''):
        '''
        获取该用户对某个资源的所有权限
        system_id: 子系统ID
        resource: 资源：resource_group:resource_name, 若为空，则返回所有权限
        '''
        perm_list = []
        for i in self.perms():
            all_flag = not resource and system_id == i.resource.system_id
            if all_flag or self.check_resource(system_id, resource, i.resource, False):
                _resource = {'name':i.resource.name, 'group':i.resource.group}
                perm = {'oper':i.oper, 'resource':_resource, 'attr':i.attr}
                perm_list.append(perm)
        return perm_list

class UserRole(UserBase):
    '''
    用户角色关系
    '''
    _table = 'user_role'
    _fields = set(['id', 'uid', 'role_id', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`uid` INT NOT NULL DEFAULT '0' COMMENT '用户ID'",
               "`role_id` INT NOT NULL DEFAULT '0' COMMENT '角色ID'",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `uid_roleid` (`uid`, `role_id`)")

class Role(UserBase):
    '''
    角色
    '''
    _table = 'role'
    _fields = set(['id', 'name', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`name` varchar(32) NOT NULL DEFAULT '' COMMENT '角色名称'",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `name` (`name`)")

    def before_delete(self):
        '''
        删除角色的同时删除其与用户、权限的关系
        '''
        for i in UserRole.mgr(self.ismaster).Q().filter(role_id=self.id):
            i.delete()
        for i in RolePerm.mgr(self.ismaster).Q().filter(role_id=self.id):
            i.delete()

    def perms(self):
        '''
        本角色所拥有的所有权限
        '''
        perms = []
        for i in RolePerm.mgr(self.ismaster).Q().filter(role_id=self.id):
            perm = Perm.mgr(self.ismaster).Q().filter(id=i.perm_id)[0]
            if perm:
                perms.append(perm)
        return perms

class RolePerm(UserBase):
    '''
    角色-权限中间关系
    '''
    _table = 'role_perm'
    _fields = set(['id', 'role_id', 'perm_id', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`role_id` INT NOT NULL DEFAULT '0' COMMENT '角色ID'",
               "`perm_id` INT NOT NULL DEFAULT '0' COMMENT '权限ID'",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `roleid_permid` (`role_id`, `perm_id`)")

class Perm(UserBase):
    '''
    权限
    '''
    _table = 'perm'
    _fields = set(['id', 'name', 'oper', 'resource_id', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`name` varchar(32) NOT NULL DEFAULT '' COMMENT '权限名称'",
               "`oper` varchar(32) NOT NULL DEFAULT '' COMMENT '操作(add,delete,update,query)'",
               "`resource_id` int  NOT NULL DEFAULT '0' COMMENT '资源ID'",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `name` (`name`)")
    def before_delete(self):
        '''
        删除权限的同时删除其与角色、属性的关系
        '''
        for i in RolePerm.mgr(self.ismaster).Q().filter(perm_id=self.id):
            i.delete()
        for i in PermAttr.mgr(self.ismaster).Q().filter(perm_id=self.id):
            i.delete()

    @property
    def resource(self):
        '''
        该权限对应的资源
        '''
        return Resource.mgr(self.ismaster).one(self.resource_id)

    @property
    def attr(self):
        '''
        该权限的属性
        '''
        res = {}
        for i in PermAttr.mgr(self.ismaster).Q().filter(perm_id=self.id):
            res[i.attr_name] = i.attr_val
        return res

class PermAttr(UserBase):
    '''
    权限的属性值, 根据权限对应的资源的属性
    '''
    _table = 'perm_attr'
    _fields = set(['id', 'perm_id', 'attr_name', 'attr_val', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`perm_id` INT NOT NULL DEFAULT '0' COMMENT '权限ID'",
               "`attr_name` varchar(32) NOT NULL DEFAULT '' COMMENT '属性名'",
               "`attr_val` varchar(32) NOT NULL DEFAULT '' COMMENT '属性值'",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `perm_id_name` (`perm_id`, `attr_name`)")

class Resource(UserBase):
    '''
    资源
    '''
    _table = 'resource'
    _fields = set(['id', 'name', 'nick', 'group', 'system_id', 'attr', 'update_time'])
    _scheme = ("`id` BIGINT NOT NULL AUTO_INCREMENT",
               "`name` varchar(32) NOT NULL DEFAULT '' COMMENT '资源名'",
               "`nick` varchar(64) NOT NULL DEFAULT '' COMMENT '显示名'",
               "`group` varchar(32) NOT NULL DEFAULT '' COMMENT '分组'",
               "`system_id` int NOT NULL DEFAULT '0' COMMENT '子系统ID'",
               "`attr` varchar(255) NOT NULL DEFAULT '' COMMENT '属性名,冒号分割'",
               "`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
               "PRIMARY KEY `idx_id` (`id`)",
               "UNIQUE KEY `system_id_group_name` (`system_id`,`group`,`name`)")
    @property
    def full_name(self):
        '''
        资源的全名
        '''
        return '%s-%s-%s' % (self.system.name, self.group, self.nick)

    @property
    def system(self):
        '''
        资源所属的子系统
        '''
        return SubSystem.mgr(self.ismaster).one(self.system_id)

