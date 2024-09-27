CREATE TABLE `syncml` (
  `path` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `gid` varchar(255) COLLATE utf8_unicode_ci DEFAULT '',
  `data` LONGBLOB NULL,
  PRIMARY KEY (`path`),
  KEY `gid` (`gid`,`path`)
) ENGINE=ROCKSDB;
