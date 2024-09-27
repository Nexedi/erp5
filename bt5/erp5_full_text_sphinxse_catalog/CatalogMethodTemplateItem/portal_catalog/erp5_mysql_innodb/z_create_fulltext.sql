# Host:
# Database: test
# Table: 'full_text'
#
CREATE TABLE `full_text` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `SearchableText` MEDIUMTEXT,
  PRIMARY KEY  (`uid`)
) ENGINE=ROCKSDB;
