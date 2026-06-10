-- Host:
-- Database: test
-- Table: 'stock'
--

CREATE TABLE stock (
  uid INTEGER NOT NULL,
  order_id INTEGER NOT NULL,
  explanation_uid INTEGER,
  node_uid INTEGER,
  section_uid INTEGER,
  payment_uid INTEGER,
  function_uid INTEGER,
  project_uid INTEGER,
  funding_uid INTEGER,
  ledger_uid INTEGER,
  payment_request_uid INTEGER,
  mirror_section_uid INTEGER,
  mirror_node_uid INTEGER,
  resource_uid INTEGER,
  quantity REAL,
  is_cancellation INTEGER,
  is_accountable INTEGER,
  date TEXT,
  mirror_date TEXT,
  total_price REAL,
  portal_type TEXT,
  simulation_state TEXT DEFAULT '',
  variation_text TEXT,
  sub_variation_text TEXT,
  is_source INTEGER,
  PRIMARY KEY (uid, order_id)
);
<dtml-var sql_delimiter>
-- Indexes prefixed by table name
CREATE INDEX stock_quantity ON stock (quantity);
<dtml-var sql_delimiter>
CREATE INDEX stock_section_uid_portal_type_mirror_section_uid
  ON stock (section_uid, portal_type, mirror_section_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_mirror_section_uid ON stock (mirror_section_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_mirror_node_uid ON stock (mirror_node_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_node_uid ON stock (node_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_payment_uid ON stock (payment_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_function_uid ON stock (function_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_payment_request_uid ON stock (payment_request_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_project_uid ON stock (project_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_funding_uid ON stock (funding_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_explanation_uid ON stock (explanation_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_state_section_node_date
  ON stock (simulation_state, section_uid, node_uid, date);
<dtml-var sql_delimiter>
CREATE INDEX stock_resource_node_uid ON stock (resource_uid, node_uid);
<dtml-var sql_delimiter>
CREATE INDEX stock_resource_section_node_uid
  ON stock (resource_uid, section_uid, node_uid, simulation_state);
<dtml-var sql_delimiter>
CREATE INDEX stock_date ON stock (date);
