CREATE TABLE roles_and_users (
  uid INT UNSIGNED,
  local_roles_group_id VARCHAR(255) default '',
  allowedRolesAndUsers VARCHAR(255),
  KEY `uid` (`uid`),
  KEY `allowedRolesAndUsers` (`allowedRolesAndUsers`),
  KEY `local_roles_group_id` (`local_roles_group_id`)
)  ENGINE=ROCKSDB;
