CREATE TABLE `user` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `user_id` varchar(255) binary default '',
  PRIMARY KEY (`uid`),
  KEY `user_id` (`user_id`)
) ENGINE=ROCKSDB;
