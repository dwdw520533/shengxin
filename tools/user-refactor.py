#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Abstract: init all the necessay models

import os
import sys
sys.path.append(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))
from model.user import (Organization, User, Position,
                        UserRole, Role, RolePerm, Perm,
                        PermAttr, PermRaction, ResAction,
                        Resource, PositionRole,
                        ResRaction, ResGroup)
from model.notice import Notice, NoticeCategory, NoticeWho
from model.menu import Menu
from model.subsystem import SubSystem


class BootStrap(object):
    '''
    initing
    '''
    def start(self):
        # create table ...
        '''
        for i in (
                Organization, User, Position,
                UserRole, Role, RolePerm,
                Perm, PermAttr, PermRaction,
                ResAction, Resource, PositionRole,
                ResRaction, ResGroup,
                Notice, Menu, SubSystem):
            i.new().init_table()
        '''
        for i in (NoticeCategory, NoticeWho):
            i.new().init_table()
        #ResRaction.new().init_table()
        #PermRaction.new().init_table()

if __name__ == "__main__":
    bs = BootStrap()
    bs.start()

