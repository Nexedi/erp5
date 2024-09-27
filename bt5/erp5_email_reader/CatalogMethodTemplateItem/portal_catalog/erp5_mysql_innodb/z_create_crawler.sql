CREATE TABLE `crawler` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `frequency_index` INT,
  `creation_date_index` INT,
  PRIMARY KEY  (`uid`),
  KEY `creation_date_index` (`creation_date_index`, `frequency_index`)
) ENGINE=ROCKSDB;
