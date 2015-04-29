#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公告管理
"""
from handler.base import BaseHandler
from model.notice import NoticeCategory, Notice, NoticeWho
from model.user import User, Organization


class NoticeHandler(BaseHandler):
    """
    公告管理
    """
    def list(self):
        """
        公告查询
        """
        notice_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        category_id = int(self.get_argument('category_id', 0))
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        query = Notice.mgr().Q()
        if notice_id:
            query.filter(id=notice_id)
        if category_id:
            query.filter(category_id=category_id)
        if name:
            query.extra("name LIKE '%%%s%%'" % name)
        count = query.count()
        page_count = (count+psize-1)/psize
        query.orderby('is_top', 'DESC').orderby('create_time', 'DESC')
        notice_list = query[(page-1)*psize:page*psize]
        self.render('setting/notice_list.html',
                    target_tab=self.target_tab,
                    name=name,
                    category_id=category_id,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    notice_list=notice_list,
                    category_list=NoticeCategory.mgr().Q().data())

    def save(self):
        """
        公告保存
        """
        notice_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        content = self.get_argument('content')
        category_id = int(self.get_argument('category_id'))
        is_top = int(self.get_argument('is_top'))
        is_global = int(self.get_argument('is_global'))
        no = int(self.get_argument('no', 0))
        user_id_list = self.get_argument('user_notice_%d.id' % notice_id, '').split(',')
        user_id_list = [int(i) for i in user_id_list if i]
        org_id_list = self.get_argument('org_notice_%d.id' % notice_id, '').split(',')
        org_id_list = [int(i) for i in org_id_list if i]

        # 参数检查
        msg = ''
        if not (is_global or user_id_list or org_id_list):
            msg = '非广播时，请选择人员或者部门'
        if msg:
            self.json2dwz('300', '', msg=msg)
            return
        # 保存到数据库
        if notice_id:
            notice = Notice.mgr(ismaster=True).one(notice_id)
        else:
            notice = Notice.new()
            notice.create_user = self.current_user['name']
        notice.name, notice.content, notice.category_id = name, content, category_id
        notice.is_top, notice.is_global, notice.no = is_top, is_global, no
        notice.update_user = self.current_user['name']
        notice = notice.save()
        # 公告与用户
        who_user_list = NoticeWho.mgr(ismaster=1).Q().filter(who_type='user', notice_id=notice.id).data()
        for i in who_user_list:
            if i.who_id not in user_id_list:
                i.delete()
        for i in user_id_list:
            if i not in [u.who_id for u in who_user_list]:
                nw = NoticeWho.new()
                nw.notice_id, nw.who_type, nw.who_id = notice.id, 'user', i
                nw.save()
        # 公告与组织
        query = NoticeWho.mgr(ismaster=1).Q()
        who_org_list = query.filter(who_type='organization', notice_id=notice.id).data()
        for i in who_org_list:
            if i.who_id not in org_id_list:
                i.delete()
        for i in org_id_list:
            if i not in [u.who_id for u in who_org_list]:
                nw = NoticeWho.new()
                nw.notice_id, nw.who_type, nw.who_id = notice.id, 'organization', i
                nw.save()
        self.json2dwz('200', 'closeCurrent', self.target_tab)

    def add(self):
        """
        公告增加
        """
        self.render('setting/notice_add.html',
                    target_tab=self.target_tab,
                    category_list=NoticeCategory.mgr().Q().data())

    def edit(self):
        """
        公告编辑
        """
        notice_id = int(self.get_argument('id'))
        notice = Notice.mgr(ismaster=1).one(notice_id)
        query = NoticeWho.mgr(ismaster=1).Q()
        who_user_list = query.filter(who_type='user', notice_id=notice_id).data()
        query = NoticeWho.mgr(ismaster=1).Q()
        who_org_list = query.filter(who_type='organization', notice_id=notice_id).data()
        user_name_list = [u.real_name for u in [User.mgr().one(i.who_id) for i in who_user_list] if u]
        org_name_list = [o.name for o in [Organization.mgr().one(i.who_id) for i in who_org_list] if o]
        self.render('setting/notice_edit.html',
                    target_tab=self.target_tab,
                    notice=notice,
                    category_list=NoticeCategory.mgr().Q().data(),
                    user_ids=','.join([str(i.who_id) for i in who_user_list]),
                    org_ids=','.join([str(i.who_id) for i in who_org_list]),
                    user_names=','.join(user_name_list),
                    org_names=','.join(org_name_list))

    def delete(self):
        """
        公告删除
        """
        notice_id = int(self.get_argument('id'))
        notice = Notice.mgr(ismaster=1).one(notice_id)
        if notice:
            notice.delete()
        for i in NoticeWho.mgr(ismaster=1).Q().filter(notice_id=notice_id):
            i.delete()
        self.json2dwz('200', 'forward', self.target_tab, forward_url='notice/list')

    def category__list(self):
        """
        公告类型查询
        """
        nc_id = int(self.get_argument('id', 0))
        name = self.get_argument('name', '')
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        query = NoticeCategory.mgr().Q()
        if nc_id:
            query.filter(id=nc_id)
        if name:
            query.extra("name LIKE '%%%s%%'"%name)
        count = query.count()
        page_count = (count+psize-1)/psize
        category_list = query[(page-1)*psize:page*psize]
        self.render('setting/notice_cate_list.html',
                    target_tab=self.target_tab,
                    name=name,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    category_list=category_list)

    def category__save(self):
        """
        公告类型保存
        """
        nc_id = int(self.get_argument('id', 0))
        name = self.get_argument('name')
        no = int(self.get_argument('no', 0))
        # 参数检查
        msg = ''
        cate = NoticeCategory.mgr().Q().filter(name=name)[0]
        if cate and nc_id != cate.id:
            msg = '类型(%s)已经存在' % name
        if msg:
            self.json2dwz('300', '', msg=msg)
            return
        # 保存到数据库
        if nc_id:
            ncate = NoticeCategory.mgr(ismaster=True).one(nc_id)
        else:
            ncate = NoticeCategory.new()
        ncate.name, ncate.no = name, no
        ncate.save()
        self.json2dwz('200', 'closeCurrent', self.target_tab)

    def category__add(self):
        """
        公告类型增加
        """
        self.render('setting/notice_cate_add.html',
                    target_tab=self.target_tab)

    def category__edit(self):
        """
        公告类型编辑
        """
        nc_id = int(self.get_argument('id'))
        notice_cate = NoticeCategory.mgr(ismaster=1).one(nc_id)
        self.render('setting/notice_cate_edit.html',
                    target_tab=self.target_tab,
                    notice_cate=notice_cate)

    def category__delete(self):
        """
        公告类型删除
        """
        nc_id = int(self.get_argument('id'))
        notice_cate = NoticeCategory.mgr(ismaster=1).one(nc_id)
        if notice_cate:
            notice_cate.delete()
        self.json2dwz('200', 'forward', self.target_tab, forward_url='notice/category/list')

    def who__user(self):
        """
        公告用户查询
        """
        name = self.get_argument('name', '')
        real_name = self.get_argument('real_name', '')
        org_id = int(self.get_argument('org_id', 0))
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        query = User.mgr().Q()
        if name:
            query.extra("name LIKE '%%%s%%'"%name)
        if real_name:
            query.extra("real_name LIKE '%%%s%%'"%real_name)
        count = query.count()
        page_count = (count+psize-1)/psize
        if org_id:
            org = Organization.mgr().one(org_id)
            if org:
                org_list = [str(i.id) for i in org.children]
                org_list.append(str(org.id))
                query.extra('org_id in (%s)' % ','.join(org_list))
        user_list = query[(page-1)*psize:page*psize]
        org_list = Organization.mgr().Q()
        self.render('setting/notice_user.html',
                    name=name,
                    real_name=real_name,
                    org_id=org_id,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    user_list=user_list,
                    org_list=org_list)

    def who__organization(self):
        """
        公告组织查询
        """
        name = self.get_argument('name', '')
        parent_id = int(self.get_argument('parent_id', 0))
        page = int(self.get_argument('pageNum', 1))
        psize = int(self.get_argument('numPerPage', 20))
        query = Organization.mgr().Q()
        if name:
            query.extra("name LIKE '%%%s%%'"%name)
        if parent_id:
            query.filter(parent_id=parent_id)
        count = query.count()
        page_count = (count+psize-1)/psize
        org_list = query[(page-1)*psize:page*psize]
        all_org_list = Organization.mgr().Q()
        self.render('setting/notice_organization.html',
                    name=name,
                    parent_id=parent_id,
                    page=page,
                    psize=psize,
                    count=count,
                    page_count=page_count,
                    org_list=org_list,
                    all_org_list=all_org_list)

