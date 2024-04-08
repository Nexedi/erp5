CREATE TABLE alternate_roles_and_users (
  `uid` BIGINT UNSIGNED NOT NULL,
  `alternate_security_uid` INT UNSIGNED,
  `other_security_uid` INT UNSIGNED,
  PRIMARY KEY  (`uid`)
)
