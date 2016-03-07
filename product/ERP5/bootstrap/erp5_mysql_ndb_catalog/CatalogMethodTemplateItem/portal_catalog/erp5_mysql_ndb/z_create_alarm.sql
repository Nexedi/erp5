# Host:
# Database: test
# Table: 'catalog'
#
CREATE TABLE `alarm` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `alarm_date` datetime default '2006-01-01',
  PRIMARY KEY  (`uid`)
) TYPE=ndb;
