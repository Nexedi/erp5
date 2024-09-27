CREATE TABLE `transformation` (
  `uid` bigint(20) unsigned NOT NULL,
  `variation_text` varchar(255) default '',
  `transformed_uid` bigint(20) unsigned NOT NULL,
  `transformed_variation_text` varchar(255) default '',
  `quantity` double,
  KEY `resource` (`uid`, `variation_text`),
  KEY `transformed_resource` (`transformed_uid`, `transformed_variation_text`)
) ENGINE=ROCKSDB;
