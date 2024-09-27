CREATE TABLE `email` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `url_string` varchar(255),
  PRIMARY KEY `uid` (`uid`),
  KEY `url_string` (`url_string`)
) ENGINE=ROCKSDB;