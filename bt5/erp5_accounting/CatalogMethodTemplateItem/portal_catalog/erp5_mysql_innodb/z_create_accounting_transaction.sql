CREATE TABLE `accounting_transaction` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `order_id` TINYINT UNSIGNED NOT NULL,

  `section_uid` BIGINT UNSIGNED,
  `mirror_section_uid` BIGINT UNSIGNED,
  `resource_uid` BIGINT UNSIGNED,

  `project_uid` BIGINT UNSIGNED,
  `payment_uid` BIGINT UNSIGNED,

  `accounting_transaction_title` VARCHAR(255),
  `reference` VARCHAR(255),
  `specific_reference` VARCHAR(255),

  `operation_date` datetime default NULL,

  `total_debit` real,
  `total_credit` real,

  PRIMARY KEY (`uid`, `order_id`),
  KEY (`section_uid`, `mirror_section_uid`)
  -- TODO: keys
) ENGINE=ROCKSDB
