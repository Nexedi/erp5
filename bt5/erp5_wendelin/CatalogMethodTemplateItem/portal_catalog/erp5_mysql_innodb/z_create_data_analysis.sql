# Host:
# Database: test
# Table: 'catalog'
#
CREATE TABLE `data_analysis` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `refresh_state` varchar(255) default '',
  PRIMARY KEY  (`uid`),
  KEY `refresh_state` (`refresh_state`)
) ENGINE=InnoDB;
