CREATE TABLE reporting_outcome (
  uid BIGINT UNSIGNED NOT NULL,
  outcome_description VARCHAR(255),
  PRIMARY KEY `uid` (`uid`)
) ENGINE=ROCKSDB;
