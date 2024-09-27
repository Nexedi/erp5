# Host:
# Database: test
# Table: 'record'
#
CREATE TABLE `record` (
  `uid` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `path` varchar(255) NOT NULL default '',
  `catalog` BOOL NOT NULL default 0,
  `played` BOOL NOT NULL default 0,
  `date` DATETIME NOT NULL,
  PRIMARY KEY  (`uid`),
  KEY `played` (`played`),
  KEY `date` (`date`)
) ENGINE=ROCKSDB;
