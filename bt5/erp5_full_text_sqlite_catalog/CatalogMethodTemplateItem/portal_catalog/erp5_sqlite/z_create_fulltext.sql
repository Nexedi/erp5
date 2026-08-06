CREATE TABLE full_text (
  uid INTEGER NOT NULL PRIMARY KEY,
  SearchableText TEXT
);

<dtml-var sql_delimiter>


CREATE VIRTUAL TABLE full_text_fts
USING fts5(
  SearchableText,
  content='full_text',
  content_rowid='uid',
  tokenize='unicode61'
);

<dtml-var sql_delimiter>


CREATE TRIGGER full_text_ai AFTER INSERT ON full_text BEGIN
  INSERT INTO full_text_fts(rowid, SearchableText)
  VALUES (new.uid, new.SearchableText);
END;


<dtml-var sql_delimiter>


CREATE TRIGGER full_text_ad AFTER DELETE ON full_text BEGIN
  INSERT INTO full_text_fts(full_text_fts, rowid, SearchableText)
  VALUES('delete', old.uid, old.SearchableText);
END;

<dtml-var sql_delimiter>


CREATE TRIGGER full_text_au AFTER UPDATE ON full_text BEGIN
  INSERT INTO full_text_fts(full_text_fts, rowid, SearchableText)
  VALUES('delete', old.uid, old.SearchableText);

  INSERT INTO full_text_fts(rowid, SearchableText)
  VALUES (new.uid, new.SearchableText);
END;

