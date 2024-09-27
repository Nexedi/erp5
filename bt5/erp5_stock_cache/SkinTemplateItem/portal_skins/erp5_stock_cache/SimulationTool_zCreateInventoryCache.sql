Create table `inventory_cache` (
      `query` BINARY(16) NOT NULL,
      `date` datetime NOT NULL,
      `result` LONGBLOB NOT NULL,
   PRIMARY KEY (`query`, `date`),
   KEY (`date`)
) Engine=ROCKSDB