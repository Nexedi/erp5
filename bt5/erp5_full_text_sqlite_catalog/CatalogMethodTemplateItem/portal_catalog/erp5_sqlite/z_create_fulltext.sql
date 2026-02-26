CREATE TABLE full_text (
  uid INTEGER NOT NULL PRIMARY KEY,
  SearchableText TEXT
);

<dtml-var sql_delimiter>


CREATE VIRTUAL TABLE full_text_fts
USING fts5(
  uid UNINDEXED,
  SearchableText
);