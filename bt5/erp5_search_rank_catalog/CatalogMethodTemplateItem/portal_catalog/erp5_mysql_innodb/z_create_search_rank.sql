# Host:
# Database: test
# Table: 'search_rank'
#
CREATE TABLE `search_rank` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `search_rank` DECIMAL UNSIGNED ZEROFILL default 0,
  PRIMARY KEY `uid` (`uid`),
  KEY `search_rank` (`search_rank`)
) ENGINE=InnoDB;
