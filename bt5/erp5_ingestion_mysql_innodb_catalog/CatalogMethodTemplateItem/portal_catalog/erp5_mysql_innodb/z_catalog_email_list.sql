<dtml-let email_list="[]" column_list="['url_string']">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if expr="getPortalType[loop_item]=='Email'">
      <dtml-call expr="email_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(email_list) > 0">
    INSERT INTO
      email (uid, <dtml-in column_list>`<dtml-var sequence-item>`<dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
    VALUES
      <dtml-in prefix="loop" expr="email_list">
      (
        <dtml-sqlvar expr="uid[loop_item]" type="int">,  
        <dtml-sqlvar expr="getUrlString[loop_item]" type="string" optional>
      )
      <dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
    ON DUPLICATE KEY UPDATE
    <dtml-in column_list>
      `<dtml-var sequence-item>` = VALUES(<dtml-var sequence-item>)<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>
