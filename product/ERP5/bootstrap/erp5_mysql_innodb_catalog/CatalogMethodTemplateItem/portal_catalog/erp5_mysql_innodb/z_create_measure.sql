CREATE TABLE `measure` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `resource_uid` BIGINT UNSIGNED NOT NULL,
  `variation` VARCHAR(255),
  `metric_type_uid` BIGINT UNSIGNED NOT NULL,
  `quantity` REAL NOT NULL,
  `variation_text_line_1` varchar(255) DEFAULT NULL,
  `variation_text_line_2` varchar(255) DEFAULT NULL,
  `variation_text_line_3` varchar(255) DEFAULT NULL,
  `variation_text_line_4` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`uid`, `variation`),
  KEY (`metric_type_uid`)
) ENGINE=InnoDB;
