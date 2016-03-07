CREATE TABLE `egov` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `portal_type` VARCHAR(255) DEFAULT '',
  `translated_validation_state_title` VARCHAR(255) DEFAULT '',
  `modification_date` DATETIME,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB
