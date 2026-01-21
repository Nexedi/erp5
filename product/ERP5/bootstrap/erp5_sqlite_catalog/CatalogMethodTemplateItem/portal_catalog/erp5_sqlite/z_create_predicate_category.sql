-- Host: 
-- Database: test
-- Table: 'predicate_category'
--

CREATE TABLE predicate_category (
  uid INTEGER NOT NULL,
  category_uid INTEGER DEFAULT 0,
  base_category_uid INTEGER DEFAULT 0,
  category_strict_membership INTEGER DEFAULT 0,
  PRIMARY KEY (uid, category_uid, base_category_uid, category_strict_membership)
);

CREATE INDEX predicate_category_category_strict_membership 
  ON predicate_category (category_strict_membership);
CREATE INDEX predicate_category_membership 
  ON predicate_category (category_uid, base_category_uid);