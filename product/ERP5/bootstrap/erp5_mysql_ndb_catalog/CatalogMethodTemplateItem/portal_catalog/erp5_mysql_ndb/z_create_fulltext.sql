# Host:
# Database: test
# Table: 'full_text'
#
CREATE TABLE `full_text` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `SearchableText` text,
  PRIMARY KEY  (`uid`),
  FULLTEXT `SearchableText` (`SearchableText`)
) ENGINE=MyISAM;
