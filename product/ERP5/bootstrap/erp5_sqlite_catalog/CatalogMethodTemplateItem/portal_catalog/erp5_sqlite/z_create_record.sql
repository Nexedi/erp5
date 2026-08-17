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
<dtml-var sql_delimiter>
CREATE INDEX record_played ON record (played);
<dtml-var sql_delimiter>
CREATE INDEX record_date ON record (date);