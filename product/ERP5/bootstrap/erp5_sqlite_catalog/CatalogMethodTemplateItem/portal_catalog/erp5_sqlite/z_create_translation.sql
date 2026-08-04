CREATE TABLE translation (
  language TEXT,
  message_context TEXT,
  portal_type TEXT,
  original_message TEXT,
  translated_message TEXT
);
<dtml-var sql_delimiter>
CREATE INDEX translation_message ON translation (translated_message);
<dtml-var sql_delimiter>
CREATE INDEX translation_original_message ON translation (original_message);
<dtml-var sql_delimiter>
CREATE INDEX translation_type_translated_message ON translation (portal_type, translated_message);
