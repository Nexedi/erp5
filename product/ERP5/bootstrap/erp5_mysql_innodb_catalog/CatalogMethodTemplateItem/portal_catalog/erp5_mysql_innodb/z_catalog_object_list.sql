REPLACE INTO
  catalog
  (`uid`, `security_uid`, `owner`, `viewable_owner`, `path`, `relative_url`, `parent_uid`, `id`, `description`, `title`, `meta_type`,
   `portal_type`, `opportunity_state`, `corporate_registration_code`, `ean13_code`, `validation_state`, `simulation_state`,
   `causality_state`, `invoice_state`, `payment_state`, `event_state`, `immobilisation_state`, `reference`, `grouping_reference`, `grouping_date`,
   `source_reference`, `destination_reference`, `string_index`, `int_index`, `float_index`, `has_cell_content`, `creation_date`,
   `modification_date`)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="security_uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getOwnerInfo[loop_item]['id']" type="string">,
  <dtml-sqlvar expr="(getViewPermissionOwner[loop_item] is not None) and getViewPermissionOwner[loop_item] or ''" type="string" optional>,
  <dtml-sqlvar expr="getPath[loop_item]" type="string">,
  <dtml-sqlvar expr="getRelativeUrl[loop_item]" type="string">,
  <dtml-sqlvar expr="getParentUid[loop_item]" type="int">,
  <dtml-sqlvar expr="id[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getDescription[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getTitle[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="meta_type[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getPortalType[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getOpportunityState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getCorporateRegistrationCode[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getEan13Code[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getValidationState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSimulationState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getCausalityState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getInvoiceState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getPaymentState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getEventState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getImmobilisationState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getGroupingReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getGroupingDate[loop_item]" type="datetime" optional>,
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
