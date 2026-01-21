-- Host:
-- Database: test
-- Table: 'record'
--

CREATE TABLE record (
  uid INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL DEFAULT '',
  catalog INTEGER NOT NULL DEFAULT 0,
  played INTEGER NOT NULL DEFAULT 0,
  date TEXT NOT NULL
);

CREATE INDEX record_played ON record (played);
CREATE INDEX record_date ON record (date);