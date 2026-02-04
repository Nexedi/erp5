INSERT INTO translation VALUES (?, ?, ?, ?, ?)

-- PARAMS

<dtml-in prefix="loop" expr="_.range(_.len(language))">
(
  <dtml-sqlvar expr="language[loop_item]" type="string">,
  <dtml-sqlvar expr="message_context[loop_item]" type="string">,
  <dtml-sqlvar expr="portal_type[loop_item]" type="string">,
  <dtml-sqlvar expr="original_message[loop_item]" type="string">,
  <dtml-sqlvar expr="translated_message[loop_item]" type="string">
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
