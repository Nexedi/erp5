CREATE TABLE roles_and_users (
  uid INT UNSIGNED NOT NULL,
  allowedRolesAndUsers VARCHAR(255) NOT NULL,
  KEY `uid` (`uid`),
  KEY `allowedRolesAndUsers` (`allowedRolesAndUsers`)
)  ENGINE=InnoDB;
