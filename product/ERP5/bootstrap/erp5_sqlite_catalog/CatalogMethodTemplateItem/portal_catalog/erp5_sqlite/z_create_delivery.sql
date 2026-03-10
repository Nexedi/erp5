-- Table: delivery

CREATE TABLE delivery (
  uid INTEGER NOT NULL,
  source_uid INTEGER DEFAULT 0,
  destination_uid INTEGER DEFAULT 0,
  source_section_uid INTEGER DEFAULT 0,
  destination_section_uid INTEGER DEFAULT 0,
  resource_uid INTEGER DEFAULT 0,
  start_date TEXT DEFAULT NULL,
  start_date_range_min TEXT DEFAULT NULL,
  start_date_range_max TEXT DEFAULT NULL,
  stop_date TEXT DEFAULT NULL,
  stop_date_range_min TEXT DEFAULT NULL,
  stop_date_range_max TEXT DEFAULT NULL,
  PRIMARY KEY (uid)
);

CREATE INDEX source_uid ON delivery (source_uid);
CREATE INDEX destination_uid ON delivery (destination_uid);
CREATE INDEX source_section_uid ON delivery (source_section_uid);
CREATE INDEX destination_section_uid ON delivery (destination_section_uid);
CREATE INDEX resource_uid ON delivery (resource_uid);
CREATE INDEX start_date ON delivery (start_date);