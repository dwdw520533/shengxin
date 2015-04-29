#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
p4阶段，当创建完新表后， 拷贝旧表数据到新表中，
"""
import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))

#因为position_id字段不同， 不在此文件中处理user, t_user表
from model.old_user import (Organization as OldOrganization,
                            User as OldUser,
                            Perm as OldPerm,
                            PermAttr as OldPermAttr,
                            Role as OldRole,
                            RolePerm as OldRolePerm,
                            UserRole as OldUserRole)
from model.user import (Organization as NewOrganization,
                        User as NewUser,
                        Perm as NewPerm,
                        PermAttr as NewPermAttr,
                        Role as NewRole,
                        RolePerm as NewRolePerm,
                        UserRole as NewUserRole)

from model.notice import (Notice as NewNotice,
                          NoticeCategory as NewNoticeCategory,
                          NoticeWho as NewNoticeWho)
from model.old_notice import (Notice as OldNotice,
                              NoticeCategory as OldNoticeCategory,
                              NoticeWho as OldNoticeWho)

from model.menu import Menu as NewMenu
from model.old_menu import Menu as OldMenu
from model.subsystem import SubSystem as NewSubSystem
from model.old_subsystem import SubSystem as OldSubSystem

class OldToNewService(object):
    """
    拷贝旧表数据到新表中
    """
    def start(self):
        """
        拷贝旧表数据到新t_xxxx表中
        resource表中数据

        :return: None
        """
        # 所有表
        # old_new_models = {OldNotice: NewNotice,
        #                   OldMenu: NewMenu,
        #                   OldUser: NewUser,
        #                   OldSubSystem: NewSubSystem,
        #                   OldNoticeCategory: NewNoticeCategory,
        #                   OldNoticeWho: NewNoticeWho,
        #                   OldOrganization: NewOrganization,
        #                   OldPerm: NewPerm,
        #                   OldPermAttr: NewPermAttr,
        #                   OldRole: NewRole,
        #                   OldRolePerm: NewRolePerm,
        #                   OldUserRole: NewUserRole}
        #psize = 1000
        #for (old_m, new_m) in old_new_models.items():
            #count = old_m.mgr().Q().count()
            # page_count = (count + psize - 1) /psize
            # for page in xrange(page_count):
            #     for old_obj in old_m.mgr().Q().set_limit(page*psize, psize):

        old_new_models = {OldMenu: NewMenu,
                          OldUser: NewUser,
                          OldSubSystem: NewSubSystem}

        for (old_m, new_m) in old_new_models.items():
            #不再限定用户条件， 不排除org_id为0的用户
            data_res = old_m.mgr().Q()

            for old_obj in data_res:
                obj_dict = {}
                for i in new_m._fields:
                    if new_m._table == 't_user' and i in('position_id', 'org_id'):
                        obj_dict[i] = 0  #组织、岗位都置为0
                    else:
                        obj_dict[i] = old_obj[i]
                new_m.new(obj_dict).add()

            logging.warn('-----------table %s is over', new_m._table)


if __name__ == '__main__':
    OldToNewService().start()
