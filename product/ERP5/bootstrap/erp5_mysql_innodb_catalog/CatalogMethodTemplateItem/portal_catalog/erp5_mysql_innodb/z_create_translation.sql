CREATE TABLE translation (
  language VARCHAR(255),
  message_context VARCHAR(50),
  portal_type VARCHAR(255),
  original_message VARCHAR(255),
  translated_message VARCHAR(255),
  KEY `message` (`translated_message`),
  KEY `original_message` (`original_message`),
  KEY `type_translated_message` (`portal_type`,`translated_message`)
) ENGINE=ROCKSDB;
