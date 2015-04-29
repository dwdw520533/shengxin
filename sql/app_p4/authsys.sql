-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: 10.0.1.249    Database: authsys
-- ------------------------------------------------------
-- Server version       5.6.21-70.0-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- 2015.4.16，创建每个旧表对应的新表，liugang

-- Create syntax for TABLE 't_menu'
CREATE TABLE `t_menu` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `system_id` int(11) NOT NULL DEFAULT '0' COMMENT '子系统ID',
  `parent_id` int(11) NOT NULL DEFAULT '0' COMMENT '上级菜单ID',
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '菜单名',
  `level` int(11) NOT NULL DEFAULT '0' COMMENT '菜单级别',
  `resource_id` int(11) NOT NULL DEFAULT '0' COMMENT '对应的资源ID',
  `uri` varchar(255) NOT NULL DEFAULT '' COMMENT '对应的uri',
  `target_tab` varchar(32) NOT NULL DEFAULT '' COMMENT '页面上显示的tabID',
  `no` int(11) NOT NULL DEFAULT '0' COMMENT '菜单序号',
  `create_user` varchar(32) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_user` varchar(32) NOT NULL DEFAULT '',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sysid_parentid_name` (`system_id`,`parent_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_notice'
CREATE TABLE `t_notice` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '标题',
  `content` text NOT NULL COMMENT '内容',
  `category_id` int(11) NOT NULL DEFAULT '0' COMMENT '分类ID',
  `is_top` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否置顶',
  `is_global` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否面向所有人',
  `no` int(11) NOT NULL DEFAULT '0' COMMENT '序号',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否有效',
  `create_user` varchar(32) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_user` varchar(32) NOT NULL DEFAULT '',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `no` (`no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_notice_category'
CREATE TABLE `t_notice_category` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '类别名称',
  `no` int(11) NOT NULL DEFAULT '0' COMMENT '序号',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_notice_who'
CREATE TABLE `t_notice_who` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `notice_id` int(11) NOT NULL DEFAULT '0' COMMENT '公告ID',
  `who_type` enum('user','organization','role') NOT NULL DEFAULT 'user' COMMENT '类型',
  `who_id` int(11) NOT NULL DEFAULT '0' COMMENT '用户ID,组织ID,角色ID',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `noticeid_whotype_whoid` (`notice_id`,`who_type`,`who_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_organization'
CREATE TABLE `t_organization` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '组织名称',
  `level` int(11) NOT NULL DEFAULT '0' COMMENT '组织级别',
  `parent_id` int(11) NOT NULL DEFAULT '0' COMMENT '上级组织ID',
  `status` int(11) NOT NULL DEFAULT '1' COMMENT '状态',
  `create_user` varchar(32) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_user` varchar(32) NOT NULL DEFAULT '',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `parent_name` (`parent_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_perm'
CREATE TABLE `t_perm` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '权限名称',
  `oper` varchar(32) NOT NULL DEFAULT '' COMMENT '操作(add,delete,update,query)',
  `resource_id` int(11) NOT NULL DEFAULT '0' COMMENT '资源ID',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_perm_attr'
CREATE TABLE `t_perm_attr` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `perm_id` int(11) NOT NULL DEFAULT '0' COMMENT '权限ID',
  `attr_name` varchar(32) NOT NULL DEFAULT '' COMMENT '属性名',
  `attr_val` varchar(32) NOT NULL DEFAULT '' COMMENT '属性值',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `perm_id_name` (`perm_id`,`attr_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_perm_raction'
CREATE TABLE `t_perm_raction` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `perm_id` int(11) NOT NULL DEFAULT '0' COMMENT '权限ID',
  `ract_code` varchar(100) NOT NULL DEFAULT '' COMMENT '资源操作编码',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `perm_id_racode` (`perm_id`,`ract_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_position'
CREATE TABLE `t_position` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '岗位名称',
  `organization_id` int(11) NOT NULL DEFAULT '0' COMMENT '所属组织ID',
  `note` text NOT NULL COMMENT '岗位说明',
  `status` int(11) NOT NULL DEFAULT '1' COMMENT '状态 1启用2禁用3删除',
  `create_user` varchar(32) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_user` varchar(32) NOT NULL DEFAULT '',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `org_id_name` (`organization_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_position_role'
CREATE TABLE `t_position_role` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `position_id` int(11) NOT NULL DEFAULT '0' COMMENT '岗位ID',
  `role_id` int(11) NOT NULL DEFAULT '0' COMMENT '角色ID',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `posid_roleid` (`position_id`,`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_res_action'
CREATE TABLE `t_res_action` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '操作名称',
  `code` varchar(64) NOT NULL DEFAULT '' COMMENT '操作编码',
  `status` int(11) NOT NULL DEFAULT '1' COMMENT '状态 1启用2禁用3删除',
  `create_user` varchar(32) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_user` varchar(32) NOT NULL DEFAULT '',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resa_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_res_group'
CREATE TABLE `t_res_group` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '英文名称',
  `nick` varchar(64) NOT NULL DEFAULT '' COMMENT '显示名称',
  `status` int(11) NOT NULL DEFAULT '1' COMMENT '状态 1启用2禁用3删除',
  `sub_sys_id` int(11) NOT NULL DEFAULT '0' COMMENT '系统id',
  `create_user` varchar(32) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_user` varchar(32) NOT NULL DEFAULT '',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subsys_name` (`sub_sys_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_res_raction'
CREATE TABLE `t_res_raction` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `res_id` int(11) NOT NULL DEFAULT '0' COMMENT '资源ID',
  `ract_code` varchar(100) NOT NULL DEFAULT '' COMMENT '资源操作编码',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `res_id_code` (`res_id`,`ract_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_resource'
CREATE TABLE `t_resource` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '资源名',
  `nick` varchar(64) NOT NULL DEFAULT '' COMMENT '显示名',
  `group` varchar(32) NOT NULL DEFAULT '' COMMENT '分组',
  `system_id` int(11) NOT NULL DEFAULT '0' COMMENT '子系统ID',
  `attr` varchar(255) NOT NULL DEFAULT '' COMMENT '属性名,冒号分割',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `system_id_group_name` (`system_id`,`group`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_role'
CREATE TABLE `t_role` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '角色名称',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_role_perm'
CREATE TABLE `t_role_perm` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) NOT NULL DEFAULT '0' COMMENT '角色ID',
  `perm_id` int(11) NOT NULL DEFAULT '0' COMMENT '权限ID',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `roleid_permid` (`role_id`,`perm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_subsystem'
CREATE TABLE `t_subsystem` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '名称',
  `domain` varchar(64) NOT NULL DEFAULT '' COMMENT '域名',
  `syskey` varchar(32) NOT NULL DEFAULT '' COMMENT 'key',
  `secret` varchar(32) NOT NULL DEFAULT '' COMMENT 'secret',
  `create_user` varchar(32) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_user` varchar(32) NOT NULL DEFAULT '',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `syskey` (`syskey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_user'
CREATE TABLE `t_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '登陆名',
  `passwd` varchar(64) NOT NULL DEFAULT '' COMMENT '密码',
  `real_name` varchar(64) NOT NULL DEFAULT '' COMMENT '真实名字',
  `is_root` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否root用户',
  `is_staff` tinyint(4) NOT NULL DEFAULT '1' COMMENT '是否内部员工',
  `staff_no` int(11) NOT NULL DEFAULT '0' COMMENT '员工号',
  `org_id` int(11) NOT NULL DEFAULT '0' COMMENT '组织ID',
  `position_id` int(11) NOT NULL DEFAULT '0' COMMENT '岗位ID',
  `jlb_uid` int(11) NOT NULL DEFAULT '0' COMMENT '近邻宝ID',
  `email` varchar(64) NOT NULL DEFAULT '',
  `phone` varchar(16) NOT NULL DEFAULT '',
  `status` int(11) NOT NULL DEFAULT '1' COMMENT '是否有效',
  `create_user` varchar(32) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `update_user` varchar(32) NOT NULL DEFAULT '',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_name` (`name`),
  UNIQUE KEY `idx_email` (`email`),
  UNIQUE KEY `idx_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 't_user_role'
CREATE TABLE `t_user_role` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL DEFAULT '0' COMMENT '用户ID',
  `role_id` int(11) NOT NULL DEFAULT '0' COMMENT '角色ID',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid_roleid` (`uid`,`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 2015-04-18 syf
update t_menu set uri='/config/express/query_list' where id=20;

