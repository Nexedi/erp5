CREATE TABLE `content_translation` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `property_name` VARCHAR(100) BINARY,
  `content_language` VARCHAR(100) BINARY,
  `translated_text` TEXT,
  PRIMARY KEY (`uid`, `property_name`, `content_language`),
  FULLTEXT KEY (`translated_text`) COMMENT 'parser "TokenBigramSplitSymbolAlphaDigit"'
) ENGINE=mroonga;
