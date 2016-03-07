DELETE FROM roles_and_users
<dtml-var sql_delimiter>
INSERT INTO roles_and_users (uid, allowedRolesAndUsers) VALUES
<dtml-in prefix="role" expr="getPortalObject().portal_catalog.getSQLCatalog().getRoleAndSecurityUidList()">
(<dtml-sqlvar expr="role_item[2]" type="int">, <dtml-sqlvar expr="role_item[1]" type="string">)<dtml-if sequence-end><dtml-else>,
</dtml-if>
</dtml-in>