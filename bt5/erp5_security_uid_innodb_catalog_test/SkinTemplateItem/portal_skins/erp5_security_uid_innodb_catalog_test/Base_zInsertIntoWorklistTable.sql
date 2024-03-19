INSERT INTO
  worklist_cache
  (`count`, `owner`, `viewable_owner`, `security_uid`, `alternate_security_uid`, `other_security_uid`, `portal_type`, `validation_state`, `simulation_state`, `parent_uid`, `title`,`opportunity_state`, `causality_state`, `invoice_state`, `payment_state`, `event_state`, `immobilisation_state`, `reference`, `grouping_reference`,
   `source_reference`, `destination_reference`, `string_index`, `int_index`, `float_index`, `has_cell_content`, `creation_date`,
   `modification_date`)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(count))">
  (
  <dtml-sqlvar expr="count[loop_item]" type="int">,
  <dtml-sqlvar expr="owner[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="viewable_owner[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="security_uid[loop_item]" type="int">,
  <dtml-sqlvar expr="alternate_security_uid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="other_security_uid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="portal_type[loop_item]" type="string">,
  <dtml-sqlvar expr="validation_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="simulation_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="parent_uid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="title[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="opportunity_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="causality_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="invoice_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="payment_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="event_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="immobilisation_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="reference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="grouping_reference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="source_reference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="destination_reference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="string_index[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="int_index[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="float_index[loop_item]" type="float" optional>,
  <dtml-sqlvar expr="has_cell_content[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="creation_date[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="modification_date[loop_item]" type="datetime" optional>
  )
  <dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>