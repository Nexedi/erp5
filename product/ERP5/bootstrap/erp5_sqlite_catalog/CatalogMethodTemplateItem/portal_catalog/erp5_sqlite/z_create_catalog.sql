-- Host:
-- Database: test
-- Table: 'catalog'
--
CREATE TABLE catalog (
  uid INTEGER NOT NULL,
  security_uid INTEGER,
  owner TEXT NOT NULL DEFAULT '',
  viewable_owner TEXT NOT NULL DEFAULT '',
  path TEXT NOT NULL DEFAULT '',
  relative_url TEXT NOT NULL DEFAULT '',
  parent_uid INTEGER DEFAULT 0,
  id TEXT DEFAULT '',
  description TEXT,
  title TEXT DEFAULT '',
  meta_type TEXT DEFAULT '',
  portal_type TEXT DEFAULT '',
  opportunity_state TEXT DEFAULT '',
  corporate_registration_code TEXT,
  ean13_code TEXT,
  validation_state TEXT DEFAULT '',
  simulation_state TEXT DEFAULT '',
  causality_state TEXT DEFAULT '',
  invoice_state TEXT DEFAULT '',
  payment_state TEXT DEFAULT '',
  event_state TEXT DEFAULT '',
  immobilisation_state TEXT DEFAULT '',
  reference TEXT DEFAULT '',
  grouping_reference TEXT DEFAULT '',
  grouping_date TEXT,
  source_reference TEXT DEFAULT '',
  destination_reference TEXT DEFAULT '',
  string_index TEXT,
  int_index INTEGER,
  float_index REAL,
  has_cell_content INTEGER,
  creation_date TEXT,
  modification_date TEXT,
  indexation_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (uid)
);

CREATE INDEX security_uid ON catalog (security_uid);
CREATE INDEX owner ON catalog (owner);
CREATE INDEX viewable_owner ON catalog (viewable_owner);
CREATE INDEX parent_uid ON catalog (parent_uid);
CREATE INDEX path ON catalog (path);
CREATE INDEX title ON catalog (title);
CREATE INDEX reference ON catalog (reference);
CREATE INDEX relative_url ON catalog (relative_url);
CREATE INDEX portal_type_reference ON catalog (portal_type, reference);
CREATE INDEX opportunity_state ON catalog (opportunity_state);
CREATE INDEX validation_state_portal_type
  ON catalog (validation_state, portal_type);
CREATE INDEX simulation_state_portal_type
  ON catalog (simulation_state, portal_type);
CREATE INDEX causality_state_portal_type
  ON catalog (causality_state, portal_type);
CREATE INDEX indexation_timestamp
  ON catalog (indexation_timestamp);
CREATE INDEX invoice_state ON catalog (invoice_state);
CREATE INDEX payment_state ON catalog (payment_state);
CREATE INDEX event_state ON catalog (event_state);


CREATE TRIGGER trg_catalog_indexation_timestamp
AFTER UPDATE ON catalog
FOR EACH ROW
WHEN NEW.indexation_timestamp = OLD.indexation_timestamp
BEGIN
  UPDATE catalog
  SET indexation_timestamp = CURRENT_TIMESTAMP
  WHERE uid = NEW.uid;
END;