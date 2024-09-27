CREATE TABLE `quantity_unit_conversion` (
  `uid` BIGINT UNSIGNED,
  `resource_uid` BIGINT UNSIGNED NOT NULL,
  `quantity_unit_uid` BIGINT UNSIGNED NOT NULL,
  `quantity` REAL NOT NULL,
  PRIMARY KEY (`resource_uid`, `quantity_unit_uid`),
  KEY (`uid`)
) ENGINE=ROCKSDB;
