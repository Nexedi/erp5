CREATE TABLE translation (
  language TEXT,
  message_context TEXT,
  portal_type TEXT,
  original_message TEXT,
  translated_message TEXT
);

CREATE INDEX translation_message ON translation (translated_message);
CREATE INDEX translation_original_message ON translation (original_message);
CREATE INDEX translation_type_translated_message ON translation (portal_type, translated_message);
