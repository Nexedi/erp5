CREATE TABLE `measure` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `resource_uid` BIGINT UNSIGNED NOT NULL,
  `variation` VARCHAR(255),
  `metric_type_uid` BIGINT UNSIGNED NOT NULL,
  `quantity` REAL NOT NULL,
  PRIMARY KEY (`uid`, `variation`),
  KEY (`metric_type_uid`)
) ENGINE=ROCKSDB;
