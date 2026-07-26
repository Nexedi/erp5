-- Table: subject

CREATE TABLE subject (
  subject_set_uid INTEGER NOT NULL,
  subject TEXT
);
<dtml-var sql_delimiter>
CREATE INDEX subject_subject_set_uid ON subject (subject_set_uid);
<dtml-var sql_delimiter>
CREATE INDEX subject_subject ON subject (subject);
