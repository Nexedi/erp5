 REPLACE INTO
  catalog
  (`uid`, `security_uid`, `path`, `owner`, `relative_url`, `parent_uid`, `id`, `description`, `title`,
   `portal_type`, `validation_state`, `simulation_state`,
   `reference`,
   `source_reference`, `string_index`, `int_index`, `has_cell_content`, `creation_date`,
   `modification_date`, `start_date`, `stop_date`, `indexation_date`)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="security_uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getPath[loop_item]" type="string">,
  <dtml-sqlvar expr="(getViewPermissionOwner[loop_item] is not None) and getViewPermissionOwner[loop_item] or ''" type="string" optional>,
  <dtml-sqlvar expr="getRelativeUrl[loop_item]" type="string">,
  <dtml-sqlvar expr="getParentUid[loop_item]" type="int">,
  <dtml-sqlvar expr="id[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getDescription[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getTitle[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getPortalType[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getValidationState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSimulationState[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSourceReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getStringIndex[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getIntIndex[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="hasCellContent[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getCreationDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getModificationDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getStartDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getStopDate[loop_item]" type="datetime" optional>,
  null
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>