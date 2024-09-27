# Host:
# Database: test
# Table: 'item'
#
CREATE TABLE `item` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `order_id` TINYINT UNSIGNED NOT NULL,
  `date` datetime,
  `node_uid` BIGINT UNSIGNED default '0',
  `section_uid` BIGINT UNSIGNED default '0',
  `resource_uid` BIGINT UNSIGNED default '0',
  `aggregate_uid` BIGINT UNSIGNED default '0',
  `variation_text` VARCHAR(255),
  `simulation_state` VARCHAR(255) default '',
  PRIMARY KEY (`uid`, `aggregate_uid`,`order_id`),
  KEY `section_uid` (`section_uid`),
  KEY `resource_uid` (`resource_uid`),
  KEY `variation_text` (`variation_text`),
  KEY `aggregate_simulation_state_date` (`aggregate_uid`,`simulation_state`,`date`),
  KEY `node_simulation_state_date` (`node_uid`,`simulation_state`,`date`)
) ENGINE=ROCKSDB;
