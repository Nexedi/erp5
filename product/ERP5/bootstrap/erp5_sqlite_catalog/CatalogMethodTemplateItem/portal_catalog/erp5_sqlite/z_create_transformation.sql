CREATE TABLE transformation (
  uid INTEGER NOT NULL,
  variation_text TEXT DEFAULT '',
  transformed_uid INTEGER NOT NULL,
  transformed_variation_text TEXT DEFAULT '',
  quantity REAL
);
<dtml-var sql_delimiter>
CREATE INDEX transformation_resource ON transformation (uid, variation_text);
<dtml-var sql_delimiter>
CREATE INDEX transformation_transformed_resource ON transformation (transformed_uid, transformed_variation_text);
