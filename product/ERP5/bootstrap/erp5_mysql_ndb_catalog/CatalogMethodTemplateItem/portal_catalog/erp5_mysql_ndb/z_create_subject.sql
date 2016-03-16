CREATE TABLE subject (
  uid BIGINT UNSIGNED NOT NULL,
  subject VARCHAR(255),
  PRIMARY KEY `uid` (`uid`),
  KEY `allowedRolesAndUsers` (`Subject`)
) TYPE=ndb; 
