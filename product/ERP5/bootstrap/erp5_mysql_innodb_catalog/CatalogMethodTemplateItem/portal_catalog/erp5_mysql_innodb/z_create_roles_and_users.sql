CREATE TABLE roles_and_users (
  uid INT UNSIGNED,
  allowedRolesAndUsers VARCHAR(255),
  KEY `uid` (`uid`),
  KEY `allowedRolesAndUsers` (`allowedRolesAndUsers`)
)  ENGINE=ROCKSDB;
