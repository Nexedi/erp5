# Host:
# Database: test
# Table: 'movement'
#
CREATE TABLE `movement` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `explanation_uid` BIGINT UNSIGNED default '0',
  `source_uid` BIGINT UNSIGNED default '0',
  `destination_uid` BIGINT UNSIGNED default '0',
  `resource_uid` BIGINT UNSIGNED default '0',
  `quantity` real default '0.0',
  `start_date` datetime,
  `stop_date` datetime,
  `price` real,
  `is_accountable` bool,
  `is_divergent` bool,
  `variation_text` VARCHAR(255),
  PRIMARY KEY `uid` (`uid`),
  KEY `explanation_uid` (`explanation_uid`),
  KEY `source_uid` (`source_uid`),
  KEY `destination_uid` (`destination_uid`),
  KEY `resource_uid` (`resource_uid`),
  KEY `is_accountable` (`is_accountable`),
  KEY `variation_text` (`variation_text`)
) ENGINE=ROCKSDB;
