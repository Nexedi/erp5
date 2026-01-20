<dtml-comment>
* deletion_timestanmp is needed both to know when a deletion happened (when restoring consistency) and to forget old-enough entries.
* path is needed to locate the document once the ZODB has been truncated before the deletion transaction.
* uid is needed to detect if the document we do retrieve is the one which was deleted, or another one.
* an index with deletion_timestanmp as first column is needed for good query performance.
* a primary key is good for good deletion performance.
* there is no natural primary key in this table, because a given path may have multiple uids / a given uid may have multiple paths over time.
</dtml-comment>
CREATE TABLE `deleted_catalog` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `path` varchar(255) NOT NULL,
  `deletion_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`deletion_timestamp`, `path`, `uid`)
) ENGINE=InnoDB;
