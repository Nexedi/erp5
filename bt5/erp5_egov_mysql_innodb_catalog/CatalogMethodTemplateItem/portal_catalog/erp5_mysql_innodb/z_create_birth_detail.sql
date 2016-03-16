CREATE TABLE `birth_detail` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `birthplace_city` VARCHAR(255) DEFAULT '',
  `birth_date` datetime DEFAULT NULL,
  PRIMARY KEY (`uid`),
  KEY `birthplace` (`birthplace_city`),
  KEY `birth_date` (`birth_date`)
) ENGINE=InnoDB
