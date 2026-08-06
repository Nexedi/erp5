CREATE TABLE predicate (
  uid INTEGER NOT NULL,
  quantity REAL,
  quantity_range_min REAL,
  quantity_range_max REAL,
  start_date TEXT,
  start_date_range_min TEXT,
  start_date_range_max TEXT,
  PRIMARY KEY (uid)
);