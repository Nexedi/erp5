CREATE TABLE `email_thread` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `sender` varchar(40),
  `recipient` varchar(255),
  `cc_recipient` varchar(255),
  `bcc_recipient` varchar(255),
  `start_date` datetime,
  `validation_state` varchar(20),  
  PRIMARY KEY `uid` (`uid`),
  KEY `sender` (`sender`),
  KEY `recipient` (`recipient`),
  KEY `cc_recipient` (`cc_recipient`),
  KEY `bcc_recipient` (`bcc_recipient`),
  KEY `validation_state` (`validation_state`),
  KEY `start_date` (`start_date`, `validation_state`)
) ENGINE=ROCKSDB;