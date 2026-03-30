SELECT
  DISTINCT uid, local_roles_group_id
FROM 
  roles_and_users
WHERE 
  allowedRolesAndUsers 
  IN (<dtml-in security_roles_list><dtml-sqlvar sequence-item type="string"><dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
