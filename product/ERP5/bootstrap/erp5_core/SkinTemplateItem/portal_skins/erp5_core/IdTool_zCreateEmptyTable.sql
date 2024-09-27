CREATE TABLE `portal_ids` (
  `id_group` VARBINARY(255),
  `last_id` BIGINT UNSIGNED,
  PRIMARY KEY  (`id_group`)
) ENGINE=ROCKSDB;