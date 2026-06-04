CREATE TABLE email (
  uid INTEGER NOT NULL PRIMARY KEY,
  url_string TEXT
);

CREATE INDEX idx_email_url_string
ON email (url_string);