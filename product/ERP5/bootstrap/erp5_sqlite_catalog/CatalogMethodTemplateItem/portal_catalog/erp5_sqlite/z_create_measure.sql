CREATE TABLE measure (
  uid INTEGER NOT NULL,
  resource_uid INTEGER NOT NULL,
  variation TEXT,
  metric_type_uid INTEGER NOT NULL,
  quantity REAL NOT NULL,
  PRIMARY KEY (uid, variation)
);
<dtml-var sql_delimiter>
CREATE INDEX metric_type_uid ON measure (metric_type_uid);