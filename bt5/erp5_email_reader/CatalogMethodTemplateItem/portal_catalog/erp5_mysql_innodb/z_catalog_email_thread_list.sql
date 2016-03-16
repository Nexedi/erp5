<dtml-let email_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if expr="getPortalType[loop_item]=='Email Thread'">
      <dtml-call expr="email_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(email_list) > 0">
    REPLACE INTO
      email_thread
    VALUES
      <dtml-in prefix="loop" expr="email_list">
      (
        <dtml-sqlvar expr="uid[loop_item]" type="int">,  
        <dtml-sqlvar expr="getSender[loop_item]" type="string" optional>,
        <dtml-sqlvar expr="getRecipient[loop_item]" type="string" optional>,
        <dtml-sqlvar expr="getCcRecipient[loop_item]" type="string" optional>,
        <dtml-sqlvar expr="getBccRecipient[loop_item]" type="string" optional>,
        <dtml-sqlvar expr="getStartDate[loop_item]" type="datetime" optional>,
        <dtml-sqlvar expr="getValidationState[loop_item]" type="string" optional>
      )
      <dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>