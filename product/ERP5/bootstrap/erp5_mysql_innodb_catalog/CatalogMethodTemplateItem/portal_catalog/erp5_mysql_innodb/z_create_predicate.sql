CREATE TABLE predicate (
  uid BIGINT UNSIGNED NOT NULL,
  `quantity` real ,
  `quantity_range_min` real ,
  `quantity_range_max` real ,
  `start_date` datetime,
  `start_date_range_min` datetime ,
  `start_date_range_max` datetime ,
  PRIMARY KEY `uid` (`uid`)
) ENGINE=ROCKSDB;
