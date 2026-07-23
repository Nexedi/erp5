CREATE TABLE email (
  uid INTEGER NOT NULL PRIMARY KEY,
  url_string TEXT
);
<dtml-var sql_delimiter>
CREATE INDEX idx_email_url_string
ON email (url_string);