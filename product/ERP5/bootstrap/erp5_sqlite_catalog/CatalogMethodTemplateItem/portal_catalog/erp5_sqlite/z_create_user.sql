CREATE TABLE user (
  uid INTEGER NOT NULL,
  user_id TEXT DEFAULT '',
  PRIMARY KEY (uid)
);

CREATE INDEX user_user_id ON user (user_id);
