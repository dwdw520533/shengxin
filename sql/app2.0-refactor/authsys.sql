-- 2015-03-31 liugang user表增加 岗位id字段
ALTER TABLE user ADD COLUMN position_id int NOT NULL DEFAULT '0' COMMENT '岗位ID' after org_id;

CREATE TABLE `position` (
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

CREATE TABLE `resource_action` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '操作名称',
  `code` varchar(64) NOT NULL DEFAULT '' COMMENT '操作编码',
  `resource_id` int(11) NOT NULL DEFAULT '0' COMMENT '资源id',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `position_role` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `position_id` INT NOT NULL DEFAULT '0' COMMENT '岗位ID',
  `role_id` INT NOT NULL DEFAULT '0' COMMENT '角色ID',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY `idx_id` (`id`),
  UNIQUE KEY `posid_roleid` (`position_id`, `role_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;