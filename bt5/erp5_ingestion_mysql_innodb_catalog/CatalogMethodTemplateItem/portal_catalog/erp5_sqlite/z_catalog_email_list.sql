<dtml-let email_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if expr="getPortalType[loop_item]=='Email'">
      <dtml-call expr="email_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(email_list) > 0">
    REPLACE INTO
      email
    VALUES
      <dtml-in prefix="loop" expr="email_list">
      (
        <dtml-sqlvar expr="uid[loop_item]" type="int">,  
        <dtml-sqlvar expr="getUrlString[loop_item]" type="string" optional>
      )
      <dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>