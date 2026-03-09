CREATE TABLE user (
  uid INTEGER NOT NULL,
  user_id TEXT DEFAULT '',
  PRIMARY KEY (uid)
);
<dtml-var sql_delimiter>
CREATE INDEX user_user_id ON user (user_id);
