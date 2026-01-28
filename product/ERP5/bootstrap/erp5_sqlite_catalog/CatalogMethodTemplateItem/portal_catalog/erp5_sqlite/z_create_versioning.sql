CREATE TABLE versioning (
  uid INTEGER NOT NULL,
  version TEXT DEFAULT '',
  size INTEGER,
  language TEXT DEFAULT '',
  revision TEXT DEFAULT '',
  subject_set_uid INTEGER,
  effective_date TEXT DEFAULT NULL,
  expiration_date TEXT DEFAULT NULL,
  creation_date_index INTEGER,
  frequency_index INTEGER,
  PRIMARY KEY (uid)
);
CREATE INDEX versioning_version ON versioning (version);
CREATE INDEX versioning_language ON versioning (language);
CREATE INDEX versioning_subject_set_uid ON versioning (subject_set_uid);
CREATE INDEX versioning_effective_date ON versioning (effective_date);
CREATE INDEX versioning_expiration_date ON versioning (expiration_date);
CREATE INDEX versioning_frequency_index ON versioning (creation_date_index, frequency_index);
