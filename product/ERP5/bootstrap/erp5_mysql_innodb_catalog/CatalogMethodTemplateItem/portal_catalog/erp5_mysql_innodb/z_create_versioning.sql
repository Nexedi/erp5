CREATE TABLE `versioning` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `version` varchar(255) default '',
  `size` BIGINT SIGNED,
  `language` varchar(5) default '',
  `revision` varchar(10) default '',
  `subject_set_uid` INT UNSIGNED,
  `effective_date` datetime default NULL,
  `expiration_date` datetime default NULL,
  `creation_date_index` INT,
  `frequency_index` INT,
  PRIMARY KEY  (`uid`),
  KEY `version` (`version`),
  KEY `language` (`language`),
  KEY `subject_set_uid` (`subject_set_uid`),
  KEY `effective_date` (`effective_date`),
  KEY `expiration_date` (`expiration_date`),
  KEY `frequency_index` (`creation_date_index`, `frequency_index`)
) ENGINE=ROCKSDB;
