CREATE TABLE catalog_full_text (
  uid INTEGER NOT NULL PRIMARY KEY,
  title TEXT DEFAULT '',
  description TEXT
);

<dtml-var sql_delimiter>


CREATE VIRTUAL TABLE catalog_full_text_fts
USING fts5(
  uid UNINDEXED,
  title,
  description
);