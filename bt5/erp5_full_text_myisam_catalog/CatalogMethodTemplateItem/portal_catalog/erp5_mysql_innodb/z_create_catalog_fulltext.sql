# Host:
# Database: test
# Table: 'catalog_full_text'
#
CREATE TABLE `catalog_full_text` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `title` varchar(255) default '',
  `description` text,
  PRIMARY KEY  (`uid`),
  FULLTEXT `title` (`title`),
  FULLTEXT `description` (`description`)
) ENGINE=MyISAM;
