CREATE TABLE `content_translation` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `property_name` VARBINARY(100),
  `content_language` VARBINARY(100),
  `translated_text` TEXT,
  PRIMARY KEY (`uid`, `property_name`, `content_language`),
  FULLTEXT KEY (`translated_text`)
) ENGINE=MyISAM;
