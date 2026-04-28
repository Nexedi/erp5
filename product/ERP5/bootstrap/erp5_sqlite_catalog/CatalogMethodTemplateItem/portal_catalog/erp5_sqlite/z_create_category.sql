-- Host: 
-- Database: test
-- Table: 'category'
-- 

CREATE TABLE category (
  uid INTEGER NOT NULL,
  category_uid INTEGER DEFAULT 0,
  base_category_uid INTEGER DEFAULT 0,
  category_strict_membership INTEGER DEFAULT 0,
  PRIMARY KEY (uid, category_uid, base_category_uid, category_strict_membership)
);

CREATE INDEX Membership 
  ON category (category_uid, base_category_uid);