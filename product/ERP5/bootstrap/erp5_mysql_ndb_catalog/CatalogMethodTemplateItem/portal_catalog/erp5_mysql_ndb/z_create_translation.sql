CREATE TABLE translation (
  language VARCHAR(255),
  message_context VARCHAR(50),
  original_message VARCHAR(255),
  translated_message VARCHAR(255),
  KEY `message` (`translated_message`),
  KEY `original_message` (`original_message`)
) TYPE=ndb;
