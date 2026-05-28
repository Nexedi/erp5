-- Table: subject

CREATE TABLE subject (
  subject_set_uid INTEGER NOT NULL,
  subject TEXT
);

CREATE INDEX subject_subject_set_uid ON subject (subject_set_uid);
CREATE INDEX subject_subject ON subject (subject);
