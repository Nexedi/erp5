<dtml-let row_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(security_uid))">
    <dtml-if expr="optimised_roles_and_users[loop_item]">
      <dtml-in prefix="role" expr="optimised_roles_and_users[loop_item]">
        <dtml-call expr="row_list.append([security_uid[loop_item], role_item])">
      </dtml-in>
    </dtml-if>
  </dtml-in>
  <dtml-if expr="row_list">
INSERT INTO
  roles_and_users
VALUES
    <dtml-in prefix="row" expr="row_list">
(<dtml-sqlvar expr="row_item[0]" type="string">, <dtml-sqlvar expr="row_item[1]" type="string">)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>
