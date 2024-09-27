CREATE TABLE `portal_ids` (
  `id_group` VARBINARY(255),
  `last_id` BIGINT UNSIGNED,
  PRIMARY KEY  (`id_group`)
) ENGINE=ROCKSDB
<dtml-var sql_delimiter>
<dtml-in expr="getPortalObject().portal_ids.getDictLengthIdsItems()">
INSERT INTO `portal_ids` (`id_group`, `last_id`) VALUES (<dtml-sqlvar sequence-key type="string">, <dtml-sqlvar sequence-item type="int">)
<dtml-var sql_delimiter>
</dtml-in>
COMMIT