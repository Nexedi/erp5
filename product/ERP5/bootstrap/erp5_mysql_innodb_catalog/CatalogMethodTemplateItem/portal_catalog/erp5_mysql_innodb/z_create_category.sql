# Host: 
# Database: test
# Table: 'category'
# 
CREATE TABLE `category` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `category_uid` BIGINT UNSIGNED default '0',
  `base_category_uid` BIGINT UNSIGNED default '0',
  `category_strict_membership` tinyint(1) default '0',
  PRIMARY KEY (`uid`, `category_uid`, `base_category_uid`, `category_strict_membership`),
  KEY `Membership` (`category_uid`,`base_category_uid`)
) ENGINE=ROCKSDB;