-- Host:
-- Database: test
-- Table: 'item'
--

CREATE TABLE item (
  uid INTEGER NOT NULL,
  order_id INTEGER NOT NULL,
  date TEXT,
  node_uid INTEGER DEFAULT 0,
  section_uid INTEGER DEFAULT 0,
  resource_uid INTEGER DEFAULT 0,
  aggregate_uid INTEGER DEFAULT 0,
  variation_text TEXT,
  simulation_state TEXT DEFAULT '',
  PRIMARY KEY (uid, aggregate_uid, order_id)
);

CREATE INDEX item_section_uid ON item (section_uid);
CREATE INDEX item_resource_uid ON item (resource_uid);
CREATE INDEX item_variation_text ON item (variation_text);
CREATE INDEX item_aggregate_simulation_state_date 
  ON item (aggregate_uid, simulation_state, date);
CREATE INDEX item_node_simulation_state_date 
  ON item (node_uid, simulation_state, date);