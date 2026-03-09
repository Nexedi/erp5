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
  translated_text,
  content='content_translation',
  content_rowid='uid',
  tokenize='unicode61'
);


<dtml-var sql_delimiter>

CREATE TRIGGER content_translation_ai
AFTER INSERT ON content_translation
BEGIN
  INSERT INTO content_translation_fts(rowid, translated_text)
  VALUES (new.uid, new.translated_text);
END;

<dtml-var sql_delimiter>

CREATE TRIGGER content_translation_ad
AFTER DELETE ON content_translation
BEGIN
  INSERT INTO content_translation_fts(
    content_translation_fts,
    rowid,
    translated_text
  )
  VALUES('delete', old.uid, old.translated_text);
END;

<dtml-var sql_delimiter>

CREATE TRIGGER content_translation_au
AFTER UPDATE ON content_translation
BEGIN
  INSERT INTO content_translation_fts(
    content_translation_fts,
    rowid,
    translated_text
  )
  VALUES('delete', old.uid, old.translated_text);

  INSERT INTO content_translation_fts(rowid, translated_text)
  VALUES (new.uid, new.translated_text);
END;