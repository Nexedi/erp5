CREATE TABLE catalog_full_text (
  uid INTEGER NOT NULL PRIMARY KEY,
  title TEXT DEFAULT '',
  description TEXT
);

<dtml-var sql_delimiter>


CREATE VIRTUAL TABLE catalog_full_text_fts
USING fts5(
  title,
  description,
  content='catalog_full_text',
  content_rowid='uid',
  tokenize='unicode61'
);

<dtml-var sql_delimiter>


CREATE TRIGGER catalog_full_text_ai
AFTER INSERT ON catalog_full_text
BEGIN
  INSERT INTO catalog_full_text_fts(rowid, title, description)
  VALUES (new.uid, new.title, new.description);
END;

<dtml-var sql_delimiter>


CREATE TRIGGER catalog_full_text_ad
AFTER DELETE ON catalog_full_text
BEGIN
  INSERT INTO catalog_full_text_fts(
    catalog_full_text_fts,
    rowid,
    title,
    description
  )
  VALUES('delete', old.uid, old.title, old.description);
END;

<dtml-var sql_delimiter>


CREATE TRIGGER catalog_full_text_au
AFTER UPDATE ON catalog_full_text
BEGIN
  INSERT INTO catalog_full_text_fts(
    catalog_full_text_fts,
    rowid,
    title,
    description
  )
  VALUES('delete', old.uid, old.title, old.description);

  INSERT INTO catalog_full_text_fts(rowid, title, description)
  VALUES (new.uid, new.title, new.description);
END;