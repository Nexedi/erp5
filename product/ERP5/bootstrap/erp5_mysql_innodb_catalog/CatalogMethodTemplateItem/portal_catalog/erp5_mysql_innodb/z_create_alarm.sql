# Host:
# Database: test
# Table: 'catalog'
#
CREATE TABLE `alarm` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `alarm_date` DATETIME,
  PRIMARY KEY  (`uid`)
) ENGINE=ROCKSDB;
