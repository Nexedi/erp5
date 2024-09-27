CREATE TABLE subject (
  subject_set_uid INT UNSIGNED NOT NULL,
  subject VARCHAR(255),
  KEY `subject_set_uid` (`subject_set_uid`),
  KEY `subject` (`subject`)
) ENGINE=ROCKSDB;
