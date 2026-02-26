CREATE TABLE content_translation (
  uid INTEGER NOT NULL,
  property_name BLOB NOT NULL,
  content_language BLOB NOT NULL,
  translated_text TEXT,
  PRIMARY KEY (uid, property_name, content_language)
);

<dtml-var sql_delimiter>

CREATE VIRTUAL TABLE content_translation_fts
USING fts5(
  uid UNINDEXED,
  property_name UNINDEXED,
  content_language UNINDEXED,
  translated_text
);