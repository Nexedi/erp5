CREATE TABLE `shadir` (
  `uid` BIGINT UNSIGNED PRIMARY KEY,
  `sha512` BINARY(64) NOT NULL,
  `filename` TINYTEXT,
  `summary` TEXT,
  KEY(`sha512`)
) ENGINE=InnoDB;
