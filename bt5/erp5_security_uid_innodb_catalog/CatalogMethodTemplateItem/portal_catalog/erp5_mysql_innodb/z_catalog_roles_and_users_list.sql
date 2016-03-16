<dtml-let row_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(optimised_roles_and_users))">
    <dtml-in prefix="role" expr="optimised_roles_and_users[loop_item]">
      <dtml-call expr="row_list.append([role_item[0], role_item[1], role_item[2]])">
    </dtml-in>
  </dtml-in>
  <dtml-if expr="row_list">
INSERT INTO
  roles_and_users(uid, local_roles_group_id, allowedRolesAndUsers)
VALUES
    <dtml-in prefix="row" expr="row_list">
(<dtml-sqlvar expr="row_item[0]" type="string">, <dtml-sqlvar expr="row_item[1]" type="string">, <dtml-sqlvar expr="row_item[2]" type="string">)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>
