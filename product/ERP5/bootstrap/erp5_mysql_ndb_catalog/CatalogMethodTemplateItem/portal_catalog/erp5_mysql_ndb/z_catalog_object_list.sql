REPLACE INTO
  catalog
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="security_uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getPath[loop_item]" type="string">,
  <dtml-sqlvar expr="getRelativeUrl[loop_item]" type="string">,
  <dtml-sqlvar expr="getParentUid[loop_item]" type="int">,
  <dtml-sqlvar expr="id[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getDescription[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getTitle[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="meta_type[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getPortalType[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="opportunity_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getCorporateRegistrationCode[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getEan13Code[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="validation_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSimulationState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="causality_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="invoice_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="payment_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="event_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getImmobilisationState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getGroupingReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSourceReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getDestinationReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getStringIndex[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getIntIndex[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getFloatIndex[loop_item]" type="float" optional>,
  <dtml-sqlvar expr="hasCellContent[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getCreationDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getModificationDate[loop_item]" type="datetime" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
