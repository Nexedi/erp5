CREATE TABLE `portal_ids` (
  `id_group` VARCHAR(255) BINARY,
  `last_id` BIGINT UNSIGNED,
  PRIMARY KEY  (`id_group`)
) ENGINE=InnoDB;