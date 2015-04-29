2015.4月P4阶段升级，需要做的操作：
1. 执行authsys.sql文件,  创建新的表, 名称统一为 t_XXXXXX。
======强制要求， 需要增加如下内容==========

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


---------sql文件夹结构说明 -------------
升级的sql文件见authsys.sql


1. sql目录包含的文件介绍

版本号对应目录1（该目录下包含各个库名.sql）
版本号命名规则：《目前可根据app当前的版本号来命名目录， 如app2.0》
- - - - boxgrade.sql (库.sql文件中包含待执行的sql)
- - - - cabzoo.sql
- - - - opersys.sql


1、*.sql文件说明：
文件为表变动时，对应的需要执行的sql语句。
在修改、增加、删除表字段时，除了修改Model中的文件，也需要记录该sql文件。
该语句用于李永裕进行测试和系统升级时执行对应的sql操作。


3、sql文件中内容说明：
3.1 注释行格式： 两个中横杠+ '空格' + 年与日 + 操作表简要说明 + 修改人名称
3.2 新增加的sql放在文档末尾， sql语句注意以“分号结尾”
3.3 例子说明
------------------------------------------------------------------------
-- 2015.3.5，柜体表添加字段，liugang
alter table t_cabinet add column verify_time bigint NOT NULL DEFAULT '0' COMMENT '柜体和服务器端时间比较后的差值';

-- 2015.3.5 创建待审核黄页，liugang
CREATE TABLE `t_yellow_audit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL COMMENT '商户名称',
  `phone` varchar(16) NOT NULL COMMENT '电话',
  `address` varchar(128) NOT NULL DEFAULT '' COMMENT '详细地址',
  `start_business` varchar(128) NOT NULL DEFAULT '' COMMENT '上班时间',
  `end_business` varchar(128) NOT NULL DEFAULT '' COMMENT '下班时间',
  `longitude` varchar(64) NOT NULL DEFAULT '' COMMENT '经度',
  `latitude` varchar(64) NOT NULL DEFAULT '' COMMENT '维度',
  `note` varchar(256) NOT NULL DEFAULT '' COMMENT '备注',
  `yellow_page_id` int(11) NOT NULL DEFAULT '0' COMMENT 'yellow_pages表记录id',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0审核中1审核通过2审核未通过',
  `audit_note` varchar(256) NOT NULL DEFAULT '' COMMENT '审核备注',
  `create_phone` varchar(16) NOT NULL COMMENT '创建人电话',
  `create_user` int(11) NOT NULL COMMENT '创建人',
  `create_time` datetime NOT NULL COMMENT '创建日期',
  `update_user` int(11) NOT NULL DEFAULT '0' COMMENT '更新人',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8；
