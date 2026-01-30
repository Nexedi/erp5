CREATE TABLE quantity_unit_conversion (
  uid INTEGER,
  resource_uid INTEGER NOT NULL,
  quantity_unit_uid INTEGER NOT NULL,
  quantity REAL NOT NULL,
  PRIMARY KEY (resource_uid, quantity_unit_uid)
);

CREATE INDEX uid ON quantity_unit_conversion (uid);